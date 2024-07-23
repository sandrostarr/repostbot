import os

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from colorama import Fore

import keyboard.reply as rkb
import keyboard.inline as ikb
import database.orm_query as q
import logging

from errors.InsufficientFundsException import InsufficientFundsException
from utils.functions import is_hex_string
from assets.FSMClass import AddFid, CreateTask
from handlers.menu_process import get_menu_content
from utils.functions import is_number, get_action_price, get_username_from_url
from warpcast import api



load_dotenv(find_dotenv())
admins = [
    os.getenv('ADMIN_ID1'),
    os.getenv('ADMIN_ID2')
]
user_private_router = Router()


# ############################### USER COMMANDS ################################
@user_private_router.message(CommandStart())
async def start_cmd(msg: Message, session: AsyncSession, state: FSMContext):
    logging.info(f"{msg.from_user.id} - Запущен бот или перезагружен")
    await state.clear()
    print(admins)
    #админ панель
    if msg.from_user.id == 176536188:
       answer = (f"Что надо хозяин?")
       await msg.answer(text=answer, reply_markup=rkb.create_kb("Пополнить USER",
                                                                "Заказать накрутку",
                                                                "Посчитать токены",
                                                                sizes=(1,1)))
    else:
        answer = (f"Хало, {msg.from_user.full_name}.\n\n"
                  "Прокачаем твой WARPCAST ???\n\n"
                  "LFG!!!")
        await msg.delete()
        try:
            user = await q.orm_get_user(session=session, msg=msg)
            logging.info(f"{msg.from_user.id} - Уже зареган")
            if user is None:
                user = await q.orm_add_user(session=session, msg=msg)
                logging.info(f"Добавлен новый пользователь {msg.from_user.id}")
            logging.info(f"Пользователь {user.username} в здании")
        except:
            logging.warning("Не работает нихуя")
        await msg.answer(text=answer, reply_markup=rkb.create_kb("Заработать 🧲",
                                                                 "Заказать накрутку",
                                                                 "Профиль",
                                                                 "Мои заказы",
                                                                 placeholder="Жмяк кряк",
                                                                 sizes=(2, 1, 1)
                                                                 )
                         )


@user_private_router.message(Command("faq"))
async def faq_cmd(msg: Message, state: FSMContext):
    logging.info(f"{msg.from_user.id} - Читает FAQ")
    await msg.delete()
    await state.clear()
    answer = (f"F.A.Q.\n\n"
              f"1. Выполняй задания и зарабатывай 🧲. После чего можешь заказать продвижение своего аккаунта.\n\n"
              f"2. Стоимость заданий:\n"
              f" ________________________________ \n"
              f" | Задание | Выполнение | Заказ | \n"
              f" |  Like   |     1      |   2   | \n"
              f" |  Recast |     2      |   4   | \n"
              f" |  Follow |     3      |   6   | \n"
              f" -------------------------------- \n\n"
              f"3. Минимальный заказ каждой услуги от 5\n\n"
              f"4. Время за которое начисляются 🧲 (мин):\n"
              f" _______________________ \n"
              f" | Задание |   Время   | \n"
              f" |  Like   |    1 min  | \n"
              f" |  Recast |    2 min  | \n"
              f" |  Follow |    3 min  | \n"
              f" ----------------------- \n\n"
              f"5. В случае если вы выполнили задание и в течение 72 часов отменили его, вводится система штрафов.\n\n"
              f"6. Нажав кнопку выполнил, но не выполнили задание, не будут начислены 🧲, штрафы не предусмотрены.\n\n"
              f"7. Остались вопросы? Пишите на гос услуги @username \n\n"
              )
    await msg.answer(text=answer, parse_mode="HTML")


# ################################## PROFILE ###################################
@user_private_router.message(F.text == "Профиль")
async def show_profile_data(msg: Message, session: AsyncSession, state: FSMContext):
    logging.info(f"{msg.from_user.id} - Открыл профиль")
    await msg.delete()
    await state.clear()
    user = await q.orm_get_user(session=session, msg=msg)

    answer = (f"Hola {msg.from_user.full_name}\n\n"
              f"FID: {user.fid}\n\n"
              f"Баланс: {user.balance} 🧲")

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
    logging.info(f"{call.from_user.id} - Добавляет FID")
    await state.set_state(AddFid.FID)
    answer = "Отправь свой WARPCAST FID"
    await call.message.edit_text(answer)


@user_private_router.message(AddFid.FID)
async def add_fid_data(msg: Message, session: AsyncSession, state: FSMContext):
    logging.info(f"{msg.from_user.id} - FID ввод")
    fid = msg.text
    if is_number(fid):
        fid = int(fid)
        if await q.orm_get_user(session=session, msg=msg, fid=fid) is not None:
            answer = f"Такой FID уже зарегистрирован. Если считаете что это ошибка, свяжитесь с нами"
            logging.info(f"{msg.from_user.id} - FID существует")
        else:
            await q.orm_update_user_fid(session=session, msg=msg, fid=fid)
            answer = f"FID успешно добавлен"
            logging.info(f"{msg.from_user.id} - FID Добавлен успешно")

    else:
        answer = f"Введите число, а не текст"

    await msg.answer(
        text=answer,
        reply_markup=rkb.create_kb(
            "Заработать 🧲",
            "Заказать накрутку",
            "Профиль",
            "Мои заказы",
            placeholder="Жмяк кряк",
            sizes=(2, 1, 1)
        )
    )
    await state.clear()


# ################################## EARN TOKEN ################################
@user_private_router.message(F.text == "Заработать 🧲")
async def earn_buy_tokens(msg: Message, session: AsyncSession, state: FSMContext):
    logging.info(f"{msg.from_user.id} - меню заработать")
    await state.clear()
    user = await q.orm_get_user(session=session, msg=msg)
    if user.fid is not None:
        answer, reply_markup = await get_menu_content(session, level=0)
        await msg.answer(text=answer, reply_markup=reply_markup)
        logging.info(f"{msg.from_user.id} - переход к пагинации")
    else:
        await msg.answer(text="Сначала укажи свой FID в разделе «Профиль»")
        logging.info(f"{msg.from_user.id} - у пользователя нет FID")


@user_private_router.callback_query(ikb.MenuEarnCallback.filter())
async def task_complete_page(call: CallbackQuery, callback_data: ikb.MenuEarnCallback, session: AsyncSession):
    logging.info(f"{call.from_user.id} - пагинация")
    user = await q.orm_get_user_by_tg_id(session=session, telegram_id=call.from_user.id)
    tasks = await q.orm_get_tasks(session=session, task_type=callback_data.task_type, user_id=user.id)

    if callback_data.task_type == "BUY_TOKENS":
        logging.info(f"{call.from_user.id} - захотел прикупить токены")
        answer, reply_markup = await get_menu_content(
            session,
            level=callback_data.level
        )

        await call.message.edit_text(text=str(answer), reply_markup=reply_markup)
        await call.answer()

    elif callback_data.task_type is not None and tasks:
        for task in tasks:
            print(Fore.WHITE + str(task.id) + ' ' + str(task.price) + ' ' + task.url)

        page = callback_data.page
        if page >= len(tasks):
            task = tasks[0]
            page = 0
        else:
            task = tasks[page]
        answer, reply_markup = await get_menu_content(
            session,
            level=callback_data.level,
            task=task,
            user=user,
            page=page,
            url=f"https://warpcast.com/" + task.url,
            approve=callback_data.approve,
            is_last_task=len(tasks) == 1,
        )

        await call.message.edit_text(text=str(answer), reply_markup=reply_markup)
        await call.answer()
    elif not tasks:
        answer, reply_markup = await get_menu_content(session, level=0)
        answer = f" Похоже, что ты выполнил все задания {callback_data.task_type}. Выбери другую категорию."

        await call.message.edit_text(text=answer,
                                     reply_markup=reply_markup)
        await call.answer()
        logging.info(f"{call.from_user.id} - нет квестов")


# ################################## CREATE TASK ################################
@user_private_router.message(F.text == "Заказать накрутку")
async def create_task(msg: Message, state: FSMContext):
    logging.info(f"{msg.from_user.id} - меню заказа")
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
    logging.info(f"{call.from_user.id} - меню тип задания")
    answer = ''
    action_price = get_action_price(call.data)
    await state.update_data(TASK_PRICE=action_price)
    if call.data == "LIKE":
        answer = (f"Сколько лайков нужно накрутить?\n\n"
                  f"Стоимость одного лайка = {action_price} 🧲\n\n"
                  f"<i>*в бета тесте нельзя заказать менее 5 и более 20 лайков за 1 заказ</i>")
        await state.update_data(TASK_TYPE="LIKE")
    if call.data == "RECAST":
        answer = (f"Сколько рекастов нужно сделать?\n\n"
                  f"Стоимость одного рекаста = {action_price} 🧲\n\n"
                  f"<i>*в бета тесте нельзя заказать менее 5 и более 20 рекастов за 1 заказ</i>")
        await state.update_data(TASK_TYPE="RECAST")
    if call.data == "FOLLOW":
        answer = (f"Сколько подписчиков нужно сделать?\n\n"
                  f"Стоимость одного подписчика = {action_price} 🧲\n\n"
                  f"<i>*в бета тесте нельзя заказать менее 5 и более 20 подписчиков за 1 заказ</i>")
        await state.update_data(TASK_TYPE="FOLLOW")

    await state.set_state(CreateTask.TASK_ACTIONS_AMOUNT)
    await call.message.edit_text(text=answer)


@user_private_router.message(CreateTask.TASK_ACTIONS_AMOUNT)
async def get_number_to_task(msg: Message, state: FSMContext, session: AsyncSession):
    logging.info(f"{msg.from_user.id} - количество заказа")
    data = await state.get_data()
    user = await q.orm_get_user(session=session, msg=msg)
    task_type = data['TASK_TYPE']
    actions_amount = msg.text
    if is_number(actions_amount):
        actions_amount = int(actions_amount)
        if actions_amount < 5 or actions_amount > 20:
            await msg.answer(text="Введите число от 5 до 20")
        elif user.balance >= int(actions_amount) * get_action_price(task_type):
            task_price = actions_amount * data['TASK_PRICE']
            await state.update_data(TASK_PRICE=task_price)
            if task_type == "FOLLOW":
                task_link = "профиль"
                answer = (f"Отправьте ссылку на {task_link}\n"
                          f"Стоимость услуги составит {task_price} 🧲\n"
                          f"Пример:<i> https://warpcast.com/vitalik.eth </i>")
                await state.update_data(ACTIONS_AMOUNT=actions_amount)
                await state.set_state(CreateTask.TASK_URL)
                await msg.answer(text=answer)
            else:
                task_link = "пост"
                answer = (f"Отправьте ссылку на {task_link}\n"
                          f"Стоимость услуги составит {task_price} 🧲\n"
                          f"Пример: <i> https://warpcast.com/vitalik.eth/0xf2fb9ef7 </i>")
                await state.update_data(ACTIONS_AMOUNT=actions_amount)
                await state.set_state(CreateTask.TASK_URL)
                await msg.answer(text=answer)
        else:
            await msg.answer(text="Недостаточно 🧲")
            logging.info(f"{msg.from_user.id} - нет баланса")
    else:
        await msg.answer(text="Введите корректное число")


@user_private_router.message(CreateTask.TASK_URL)
async def get_link_to_task(msg: Message, state: FSMContext, session: AsyncSession):
    logging.info(f"{msg.from_user.id} - создаем заказ")
    user = await q.orm_get_user(session=session, msg=msg)
    data = await state.get_data()
    task_type = data['TASK_TYPE']
    actions_amount = data['ACTIONS_AMOUNT']
    task_price = data['TASK_PRICE']
    task_url = msg.text
    if task_url.lower().startswith("https://warpcast.com/"):
        check_link = task_url[len("https://warpcast.com/"):]
        slash_index = check_link.find("/")

        try:
            if slash_index != -1:
                hash_prefix = check_link[slash_index + 1:]
                if len(hash_prefix) == 10 and is_hex_string(hash_prefix) and task_type != "FOLLOW":
                    username = get_username_from_url(check_link)
                    cast_hash = api.get_cast_hash(username, hash_prefix)
                    if cast_hash:

                        await q.orm_write_off_user_balance(session=session, msg=msg, balance_change=task_price)
                        await q.orm_add_task(
                            session=session,
                            user_id=user.id,
                            task_type=task_type,
                            url=task_url.replace("https://warpcast.com/", ""),
                            price=task_price,
                            actions_count=actions_amount,
                            cast_hash=cast_hash,
                        )

                        answer = (f"Задание создано:\n\n"
                                  f"Заказ: {task_type}\n"
                                  f"Количество: {actions_amount}\n"
                                  f"Стоимость: {task_price} 🧲\n"
                                  f"Ссылка: {task_url}")
                        await state.clear()
                        await msg.answer(text=answer)
                    else:
                        await msg.answer(text="Не нашел пост")
                        logging.info(f"{msg.from_user.id} - указал кривую ссылку")

                else:
                    await msg.answer(text="Некорректная ссылка")
                    logging.info(f"{msg.from_user.id} - указал кривую ссылку")
            elif len(check_link) != 0:
                if task_type == "FOLLOW":

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
                              f"Стоимость: {task_price} 🧲\n"
                              f"Ссылка: {task_url}")
                    await state.clear()
                    await msg.answer(text=answer)
                else:
                    await msg.answer(text="Некорректная ссылка")
                    logging.info(f"{msg.from_user.id} - указал кривую ссылку")
            else:
                await msg.answer(text="Некорректная ссылка")
                logging.info(f"{msg.from_user.id} - указал кривую ссылку")
        except InsufficientFundsException:
            await msg.answer(text="Недостаточно 🧲")
    else:
        await msg.answer(text="Некорректная ссылка")
        logging.info(f"{msg.from_user.id} - указал кривую ссылку")


# ################################## TASK_LIST ###################################
@user_private_router.message(F.text == "Мои заказы")
async def show_orders_task_list(msg: Message, session: AsyncSession, state: FSMContext):
    logging.info(f"{msg.from_user.id} - Посмотреть заказы")
    await msg.delete()
    await state.clear()

    user = await q.orm_get_user(session=session, msg=msg)
    tasks = await q.orm_get_tasks_by_user_id(session, user.id)

    answer = f"Список заказов: \n\n"
    if tasks:
        for task in tasks:
            if task.is_completed:
                ind = "🟢"
            elif task.actions_completed > 0:
                ind = "🟡"
            else:
                ind = "🔴"
            answer = answer + f"{ind} {task.type} {task.actions_completed} / {task.actions_count} - <a href = '{task.url}'> ссылка </a>\n"
    else:
        answer = answer + f"Нет заказов"

    await msg.answer(text=answer)
