from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

import keyboard.reply as rkb
import keyboard.inline as ikb
from utils.check_hex import is_hex_string
from assets.FSMClass import addFID, createTask
from database.orm_query import orm_add_user, orm_get_user, orm_top_up_user_balance, orm_update_user_fid
from handlers.menu_process import get_menu_content

user_private_router = Router()


# TODO метод проверки на int. Можно будет потом вынести в отдельную библиотечку проектную, если ещё где-то потребуется
def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


################################ USER COMMANDS ################################

#TODO: вынести в файл c обработчиками команд
@user_private_router.message(CommandStart())
async def start_cmd(msg: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    answer = (f"Хало, {msg.from_user.full_name}.\n\n"
              "Прокачаем твой WARPCAST ???\n\n"
              "LFG!!!")
    await msg.delete()
    try:
        user = await orm_get_user(session=session, msg=msg)
        print('Уже зареган')
        if user is None:
            user = await orm_add_user(session=session, msg=msg)
            print('Данные добавлены')
        print('Пользователь ' + user.username + ' в здании')
    except:
        print('Не работает нихуя')
    await msg.answer(text=answer, reply_markup=rkb.create_kb("Заработать токенсы",
                                                             "Заказать накрутку",
                                                             "Профиль",
                                                             "Мои заказы",
                                                             placeholder="Жмяк кряк",
                                                             sizes=(2, 1, 1)
                                                             )
                     )


#TODO: вынести в файл c обработчиками команд
@user_private_router.message(Command("faq"))
async def faq_cmd(msg: Message, state: FSMContext):
    await state.clear()
    #TODO: написать мини промт как работает наш сервис
    answer = (f'Ну типо вопрос ответ для всякой хуиты')
    await msg.delete()
    await msg.answer(text=answer)

################################### PROFILE ###################################
#Профиль добавил кнопку Добавить FID если он отсутствует + добавление
@user_private_router.message(F.text == "Профиль")
async def show_profile_data(msg: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    user = await orm_get_user(session=session, msg=msg)

    answer = (f"Hola {msg.from_user.full_name}\n\n"
              f"FID: {user.fid}\n\n"
              f"Баланс: {user.balance}")

    if user.fid is None:
        kb = ikb.create_callback_ikb(btns={
                         " ДОБАВИТЬ FID: ": f'addFID'
                     })
    else:
        kb = None
    await msg.answer(text=answer,
                     reply_markup=kb)


@user_private_router.callback_query(F.data == 'addFID')
async def get_fid_data(call: CallbackQuery, state: FSMContext):
    await state.set_state(addFID.FID)
    answer = "Отправь свой WARPCAST FID"
    await call.message.edit_text(answer)


@user_private_router.message(addFID.FID)
async def add_fid_data(msg: Message, session: AsyncSession, state: FSMContext):
    fid = msg.text
    if is_number(fid):
        fid = int(fid)
        if await orm_get_user(session=session, msg=msg, fid=fid) is not None:
            answer = f"Такой FID уже зарегистрирован. Если считаете что это ошибка, свяжитесь с нами"
        else:
            await orm_update_user_fid(session=session, msg=msg, fid=fid)
            answer = f"FID успешно добавлен"
    else:
        answer = f"Введите число, а не текст"

    await msg.answer(
        text=answer,
        reply_markup=rkb.create_kb(
            "Заработать токенсы",
            "Заказать накрутку",
            "Профиль",
            "Мои заказы",
            placeholder="Жмяк кряк",
            sizes=(2, 1, 1)
        )
    )
    await state.clear()


################################### EARN TOKEN ################################
#TODO: добавить проверку на FID чтоб обязательно заполняли его
# начало работы с заработком монет за действия
@user_private_router.message(F.text == "Заработать токенсы")
async def earn_buy_tokens(msg: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    # answer = "Выбери задания которые по душе и выполняй их"
    # await msg.answer(text=answer,reply_markup=ikb.create_callback_ikb(btns={"LIKE" : "TASK_LIKE",
    #                                                                         "RECAST": "TASK_RECAST",
    #                                                                         "FOLLOW": "TASK_FOLLOW",
    #                                                                         "КУПИТЬ ТОКЕНСЫ": "BUY_TOKENS"
    #                                                                         },
    #                                                                   sizes=(3,1,)
    #                                                                   )
    #                  )

    # TODO: по нажатию на кнопку "Заработать токенсы" на счёт падает 1 единица деняк. Проверить можно в профиле
    await orm_top_up_user_balance(session=session, msg=msg, balance=1)
    answer, reply_markup = await get_menu_content(session, level=0, menu_name="TASKS")
    await msg.answer(text=answer, reply_markup=reply_markup)


@user_private_router.callback_query(ikb.MenuEarnCallback.filter())
async def func_1(call: CallbackQuery, callback_data: ikb.MenuEarnCallback, session: AsyncSession):
    answer, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        task_type=callback_data.task_type,
        task_id=callback_data.task_id,
        page=callback_data.page,
        approve=callback_data.approve,

    )
    await call.message.edit_text(text=answer, reply_markup=reply_markup)
    await call.answer()

################################### CREATE TASK ################################
@user_private_router.message(F.text == "Заказать накрутку")
async def create_task(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(createTask.TASK_TYPE)
    answer = f"Выбери что будем накручивать?"
    await msg.answer(answer,
                     reply_markup=ikb.create_callback_ikb(btns={"LIKE": "TASK_LIKE",
                                                                "RECAST": "TASK_RECAST",
                                                                "FOLLOW": "TASK_FOLLOW",

                     }, sizes=(3,)))


@user_private_router.callback_query(createTask.TASK_TYPE)
async def get_type_of_task(call: CallbackQuery, state: FSMContext):
    answer = ''
    if call.data == "TASK_LIKE":
        answer = (f"Сколько лайков нужно накрутить?\n\n"
                  f"<i>*в бета тесте нельзя заказать более 20 лайков за 1 заказ</i>")
        await state.update_data(TASK_TYPE="LIKE")
    if call.data == "TASK_RECAST":
        answer = (f"Сколько рекастов нужно сделать?\n\n"
                  f"<i>*в бета тесте нельзя заказать более 20 рекастов за 1 заказ</i>")
        await state.update_data(TASK_TYPE="RECAST")
    if call.data == "TASK_FOLLOW":
        answer = (f"Сколько подписчиков нужно сделать?\n\n"
                  f"<i>*в бета тесте нельзя заказать более 50 подписчиков за 1 заказ</i>")
        await state.update_data(TASK_TYPE="FOLLOW")

    await state.set_state(createTask.NUMBER)
    await call.message.edit_text(text=answer)


#TODO: в бета сделаем ограничение на заказы, чтоб не было типов с заказми по 1000000000 из за ошибок
@user_private_router.message(createTask.NUMBER)
async def get_number_to_task(msg: Message, state: FSMContext):
    data = await state.get_data()
    task_type = data['TASK_TYPE']
    try:
        number = int(msg.text)
    except:
        await msg.answer(text="Введите корректное число")
    if number <= 0:
        await msg.answer(text="Введите число больше 0")
    else:
        if task_type == "FOLLOW":
            if number >= 50:
                await msg.answer(text="Введите число меньше 50")
            else:
                task_link = "профиль"
                answer = (f"Отправте ссылку на {task_link}\n"
                          f"Пример:<i> https://warpcast.com/vitalik.eth </i>")
                await state.update_data(NUMBER=number)
                await state.set_state(createTask.URL)
                await msg.answer(text=answer)
        else:
            if number >= 20 or number <= 0:
                await msg.answer(text="Введите число меньше 20")
            else:
                task_link = "пост"
                answer = (f"Отправте ссылку на {task_link}\n"
                          f"Пример: <i> https://warpcast.com/vitalik.eth/0xf2fb9ef7 </i>")
                await state.update_data(NUMBER=number)
                await state.set_state(createTask.URL)
                await msg.answer(text=answer)


#TODO: делать запись в DB с заданием
@user_private_router.message(createTask.URL)
async def get_link_to_task(msg: Message, state: FSMContext):
    data = await state.get_data()
    task_type = data['TASK_TYPE']
    url = msg.text
    if url.lower().startswith("https://warpcast.com/"):
        check_link = url[len("https://warpcast.com/"):]
        slash_index = check_link.find("/")
        if slash_index != -1:
            sub_text = check_link[slash_index + 1:]
            if len(sub_text) == 10 and is_hex_string(sub_text) and task_type != "FOLLOW":
                answer = (f"Задание создано:\n\n"
                          f"Заказ: {task_type}\n"
                          f"Количество: {data['NUMBER']}\n"
                          f"Ссылка: {url}")
                await state.clear()
                await msg.answer(text=answer)
            else:
                await msg.answer(text="Некорректная ссылка")
        elif len(check_link) != 0:
            if task_type == "FOLLOW":
                answer = (f"Задание создано:\n\n"
                          f"Заказ: {task_type}\n"
                          f"Количество: {data['NUMBER']}\n"
                          f"Ссылка: {url}")
                await state.clear()
                await msg.answer(text=answer)
            else:
                await msg.answer(text="Некорректная ссылка")
        else:
            await msg.answer(text="Некорректная ссылка")
    else:
        await msg.answer(text="Некорректная ссылка")



