from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession
from colorama import Fore

import keyboard.reply as rkb
import keyboard.inline as ikb
import database.orm_query as q
from utils.check_hex import is_hex_string
from assets.FSMClass import AddFid, CreateTask
from database.orm_query import orm_top_up_user_balance
from handlers.menu_process import get_menu_content
from utils.functions import is_number, get_action_price
from warpcast import api

user_private_router = Router()

ActionsPrices = {
    'LIKE': 2,
    'RECAST': 4,
    'FOLLOW': 6,
}


# TODO метод проверки на int. Можно будет потом вынести в отдельную библиотечку проектную, если ещё где-то потребуется
def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


################################ USER COMMANDS ################################
@user_private_router.message(CommandStart())
async def start_cmd(msg: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    answer = (f"Хало, {msg.from_user.full_name}.\n\n"
              "Прокачаем твой WARPCAST ???\n\n"
              "LFG!!!")
    await msg.delete()
    try:
        user = await q.orm_get_user(session=session, msg=msg)
        print('Уже зареган')
        if user is None:
            user = await q.orm_add_user(session=session, msg=msg)
            print('Данные добавлены')
        print('Пользователь ' + user.username + ' в здании')
    except:
        print('Не работает нихуя')
    await msg.answer(text=answer, reply_markup=rkb.create_kb("Заработать токены",
                                                             "Заказать накрутку",
                                                             "Профиль",
                                                             "Мои заказы",
                                                             placeholder="Жмяк кряк",
                                                             sizes=(2, 1, 1)
                                                             )
                     )


@user_private_router.message(Command("faq"))
async def faq_cmd(msg: Message, state: FSMContext):
    await msg.delete()
    await state.clear()
    answer = (f"F.A.Q.\n\n"
              f"1. Выполняй задания и зарабатывай токены. После чего можешь заказать продвижение своего аккаунта.\n\n"
              f"2. Стоимость заданий:\n"
              f" ________________________________ \n"
              f" | Задание | Выполнение | Заказ | \n"
              f" |   Like  |     1      |   2   | \n"
              f" |  Recast |     2      |   4   | \n"
              f" |  Follow |     3      |   6   | \n"
              f" -------------------------------- \n\n"
              f"3. Время за которое начисляются токены (мин):\n"
              f" _______________________ \n"
              f" | Задание |   Время   | \n"
              f" |   Like  |    1 min  | \n"
              f" |  Recast |    2 min  | \n"
              f" |  Follow |    3 min  | \n"
              f" ----------------------- \n\n"
              f"4. В случае если вы выполнили задание и в течении 72 часов отменили его, вводится система штрафов.\n\n"
              f"5. Нажав кнопку выполнил, но не выполнили задание, не будут начислены токены, штрафы не предусмотрены.\n\n"
              f"6. Остались вопросы? Пишите на гос услуги @username \n\n"
              )
    await msg.answer(text=answer)


################################### PROFILE ###################################
#Профиль добавил кнопку Добавить FID если он отсутствует + добавление
@user_private_router.message(F.text == "Профиль")
async def show_profile_data(msg: Message, session: AsyncSession, state: FSMContext):
    await msg.delete()
    await state.clear()
    user = await q.orm_get_user(session=session, msg=msg)

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
    await state.set_state(AddFid.FID)
    answer = "Отправь свой WARPCAST FID"
    await call.message.edit_text(answer)


@user_private_router.message(AddFid.FID)
async def add_fid_data(msg: Message, session: AsyncSession, state: FSMContext):
    fid = msg.text
    if is_number(fid):
        fid = int(fid)
        if await q.orm_get_user(session=session, msg=msg, fid=fid) is not None:
            answer = f"Такой FID уже зарегистрирован. Если считаете что это ошибка, свяжитесь с нами"
        else:
            await q.orm_update_user_fid(session=session, msg=msg, fid=fid)
            answer = f"FID успешно добавлен"
    else:
        answer = f"Введите число, а не текст"

    await msg.answer(
        text=answer,
        reply_markup=rkb.create_kb(
            "Заработать токены",
            "Заказать накрутку",
            "Профиль",
            "Мои заказы",
            placeholder="Жмяк кряк",
            sizes=(2, 1, 1)
        )
    )
    await state.clear()


################################### EARN TOKEN ################################
@user_private_router.message(F.text == "Заработать токены")
async def earn_buy_tokens(msg: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    user = await q.orm_get_user(session=session, msg=msg)
    if user.fid is not None:
        await orm_top_up_user_balance(session=session, msg=msg, balance=1)
        answer, reply_markup = await get_menu_content(session, level=0)
        await msg.answer(text=answer, reply_markup=reply_markup)
    else:
        await msg.answer(text="Сначала укажи стой FID в Profile")


@user_private_router.callback_query(ikb.MenuEarnCallback.filter())
async def task_complete_page(call: CallbackQuery, callback_data: ikb.MenuEarnCallback, session: AsyncSession):
    user = await q.orm_get_user_by_tg_id(session=session, telegram_id=call.from_user.id)
    if callback_data.task_type is not None:
        tasks = await q.orm_get_tasks(session=session, task_type=callback_data.task_type)
        for task in tasks:
            print(Fore.WHITE + str(task.id) + ' ' + str(task.price) + ' ' + task.url)

        page = callback_data.page
        if page >= len(tasks):
            task_data = tasks[0]
            page = 0
        else:
            task_data = tasks[page]
        task_url = task_data.url
        task_id = task_data.id
        answer, reply_markup = await get_menu_content(
            session,
            level=callback_data.level,
            task_type=callback_data.task_type,
            task_id=task_id,
            user_id=user.id,
            page=page,
            url=f"https://warpcast.com/" + task_url,
            approve=callback_data.approve,
        )

        await call.message.edit_text(text=str(answer), reply_markup=reply_markup)
        await call.answer()
    else:
        answer = " Похожу что ты выполнил все задания. Выбери другую категорию."
        await call.message.edit_text(text=answer,
                                     reply_markup=await get_menu_content(session, level=0))
        await call.answer()


#TODO: вытащить в отдельный файл
def check_cast_from_user(casts, startHash):
    for value in casts:
        if value.startswith(startHash):
            return True, value
    return False


def get_username_from_url(url):
    username = url.rsplit('/', 1)[0]
    return username


def get_hash_from_url(url):
    cast_hash = url.rsplit('/', 1)[-1]
    return cast_hash


################################### CREATE TASK ################################
@user_private_router.message(F.text == "Заказать накрутку")
async def create_task(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(CreateTask.TASK_TYPE)
    answer = f"Выбери, что будем накручивать?"
    await msg.answer(answer,
                     reply_markup=ikb.create_callback_ikb(btns={"LIKE": "LIKE",
                                                                "RECAST": "RECAST",
                                                                "FOLLOW": "FOLLOW",

                                                                }, sizes=(3,)))


@user_private_router.callback_query(CreateTask.TASK_TYPE)
async def get_type_of_task(call: CallbackQuery, state: FSMContext):
    answer = ''
    action_price = get_action_price(call.data)
    await state.update_data(TASK_PRICE=action_price)
    if call.data == "LIKE":
        answer = (f"Сколько лайков нужно накрутить?\n\n"
                  f"Стоимость одного лайка = {action_price} токена\n\n"
                  f"<i>*в бета тесте нельзя заказать более 20 лайков за 1 заказ</i>")
        await state.update_data(TASK_TYPE="LIKE")
    if call.data == "RECAST":
        answer = (f"Сколько рекастов нужно сделать?\n\n"
                  f"Стоимость одного рекаста = {action_price} токена\n\n"
                  f"<i>*в бета тесте нельзя заказать более 20 рекастов за 1 заказ</i>")
        await state.update_data(TASK_TYPE="RECAST")
    if call.data == "FOLLOW":
        answer = (f"Сколько подписчиков нужно сделать?\n\n"
                  f"Стоимость одного подписчика = {action_price} токенов\n\n"
                  f"<i>*в бета тесте нельзя заказать более 50 подписчиков за 1 заказ</i>")
        await state.update_data(TASK_TYPE="FOLLOW")

    await state.set_state(CreateTask.TASK_ACTIONS_AMOUNT)
    await call.message.edit_text(text=answer)


@user_private_router.message(CreateTask.TASK_ACTIONS_AMOUNT)
async def get_number_to_task(msg: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    user = await q.orm_get_user(session=session, msg=msg)
    task_type = data['TASK_TYPE']
    actions_amount = msg.text
    if is_number(actions_amount):
        if user.balance >= int(actions_amount) * get_action_price(task_type):
            actions_amount = int(actions_amount)
            task_price = actions_amount * data['TASK_PRICE']
            await state.update_data(TASK_PRICE=task_price)
            if actions_amount <= 0:
                await msg.answer(text="Введите число больше 0")
            else:
                if task_type == "FOLLOW":
                    if actions_amount >= 50:
                        await msg.answer(text="Введите число меньше 50")
                    else:
                        task_link = "профиль"
                        answer = (f"Отправьте ссылку на {task_link}\n"
                                  f"Стоимость услуги составит {task_price} токена\n"
                                  f"Пример:<i> https://warpcast.com/vitalik.eth </i>")
                        await state.update_data(ACTIONS_AMOUNT=actions_amount)
                        await state.set_state(CreateTask.TASK_URL)
                        await msg.answer(text=answer)
                else:
                    if actions_amount >= 20 or actions_amount <= 0:
                        await msg.answer(text="Введите число меньше 20")
                    else:
                        task_link = "пост"
                        answer = (f"Отправьте ссылку на {task_link}\n"
                                  f"Стоимость услуги составит {task_price} токена\n"
                                  f"Пример: <i> https://warpcast.com/vitalik.eth/0xf2fb9ef7 </i>")
                        await state.update_data(ACTIONS_AMOUNT=actions_amount)
                        await state.set_state(CreateTask.TASK_URL)
                        await msg.answer(text=answer)
        else:
            await msg.answer(text="Недостаточно средств")
    else:
        await msg.answer(text="Введите корректное число")


@user_private_router.message(CreateTask.TASK_URL)
async def get_link_to_task(msg: Message, state: FSMContext, session: AsyncSession):
    user = await q.orm_get_user(session=session, msg=msg)
    data = await state.get_data()
    task_type = data['TASK_TYPE']
    actions_amount = data['ACTIONS_AMOUNT']
    task_price = data['TASK_PRICE']
    task_url = msg.text
    if task_url.lower().startswith("https://warpcast.com/"):
        check_link = task_url[len("https://warpcast.com/"):]
        slash_index = check_link.find("/")
        if slash_index != -1:
            sub_text = check_link[slash_index + 1:]
            if len(sub_text) == 10 and is_hex_string(sub_text) and task_type != "FOLLOW":
                username = get_username_from_url(check_link)
                cast_list = api.get_casts_from_user(username)
                cast_hash = check_cast_from_user(cast_list, sub_text)
                print(cast_hash)
                if cast_hash:
                    await q.orm_write_off_user_balance(session=session, msg=msg, balance_change=task_price)
                    await q.orm_add_task(
                        session=session,
                        user_id=user.id,
                        task_type=task_type,
                        url=task_url.replace("https://warpcast.com/", ""),
                        price=task_price,
                        actions_count=actions_amount,
                    )

                    answer = (f"Задание создано:\n\n"
                              f"Заказ: {task_type}\n"
                              f"Количество: {actions_amount}\n"
                              f"Стоимость: {task_price} токена\n"
                              f"Ссылка: {task_url}")
                    await state.clear()
                    await msg.answer(text=answer)
                else:
                    await msg.answer(text="Не нашел пост")

            else:
                await msg.answer(text="Некорректная ссылка")
        elif len(check_link) != 0:
            if task_type == "FOLLOW":

                await q.orm_write_off_user_balance(session=session, msg=msg, balance_change=task_price)
                await q.orm_add_task(
                    session=session,
                    user_id=user.id,
                    task_type=task_type,
                    url=task_url,
                    price=task_price,
                    actions_count=actions_amount,
                )

                answer = (f"Задание создано:\n\n"
                          f"Заказ: {task_type}\n"
                          f"Количество: {actions_amount}\n"
                          f"Стоимость: {task_price} токена\n"
                          f"Ссылка: {task_url}")
                await state.clear()
                await msg.answer(text=answer)
            else:
                await msg.answer(text="Некорректная ссылка")
        else:
            await msg.answer(text="Некорректная ссылка")
    else:
        await msg.answer(text="Некорректная ссылка")
