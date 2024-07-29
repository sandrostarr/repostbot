from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

import keyboard.inline as ikb
import database.orm_query as q
import logging

from assets.FSMClass import AdminTopUp, calcTokens

from utils.functions import summ_result

from bot_creator import bot

admin_route = Router()


# ################################## TOP UP USER ###################################
@admin_route.message(F.text == "Пополнить USER")
async def top_up_start(msg: Message, state: FSMContext):
    logging.info(f"{msg.from_user.id} - Админ пополняет кому то баланс")
    await msg.delete()
    await state.clear()

    answer = (f"Перешли сообщение пользователя кому пополняем")
    await msg.answer(text=answer)
    await state.set_state(AdminTopUp.GET_TG_ID)


@admin_route.message(AdminTopUp.GET_TG_ID)
async def top_up_get_id(msg: Message, session: AsyncSession, state: FSMContext):
    if msg.forward_from:
        logging.info(f"{msg.from_user.id} - Выбрал Юзера через отправленное сообщение")
        telegram_id = msg.forward_from.id
        try:
            await q.orm_get_user_by_tg_id(session=session, telegram_id=telegram_id)
            await state.update_data(USER_ID=telegram_id)
            answer = ("Сколько начислить?")
            await msg.answer(text=answer)
            await state.set_state(AdminTopUp.GET_TOP_UP)
        except:
            answer = "такой не найден юзер"
            await msg.answer(text=answer)

    #TODO: сделать проверку в БД по username
    elif msg.text.startswith("@"):
        username = msg.text.strip('@')
        try:
            user = await q.orm_get_user_by_username(session=session, username=username)
            print(user.id)
            await state.update_data(USER_ID=user.telegram_id)
            answer = ("Сколько начислить?")
            await msg.answer(text=answer)
            await state.set_state(AdminTopUp.GET_TOP_UP)
        except:
            answer = "такой не найден юзер по нику"
            await msg.answer(text=answer)
    else:
        answer = ("Ебалай шо то не то")
        await msg.answer(text=answer)


@admin_route.message(AdminTopUp.GET_TOP_UP)
async def top_up_get_value(msg: Message, state: FSMContext):
    logging.info(f"{msg.from_user.id} - Выбрал cумма пополнения")
    await state.update_data(TUP_UP_SUM=msg.text)
    answer = ("HASH транзакии или комментарий кто что и почему пополнил")
    await msg.answer(text=answer)
    await state.set_state(AdminTopUp.GET_APPROVE)


@admin_route.message(AdminTopUp.GET_APPROVE)
async def top_up_get_approve(msg: Message, session: AsyncSession, state: FSMContext):
    logging.info(f"{msg.from_user.id} - Апрув добавлен")
    data = await state.get_data()
    telegram_id = data["USER_ID"]
    top_up_sum = data["TUP_UP_SUM"]
    proof = msg.text
    answer = (f"Пополнил {telegram_id} на {top_up_sum} 🧲\n"
              f"PROOF: {proof}")
    await q.orm_top_up_user_balance_by_tg_id(
        session=session,
        telegram_id=int(telegram_id),
        balance_change=int(top_up_sum),
    )
    await msg.answer(text=answer)
    await state.clear()


# ################################## COUNT ###################################

@admin_route.message(F.text == "Посчитать токены")
async def calc_summ(msg: Message, state: FSMContext):
    logging.info(f"{msg.from_user.id} - Калькулятор токенов")
    await msg.delete()
    await state.clear()
    answer = (f"количество токенов")
    await msg.answer(text=answer)
    await state.set_state(calcTokens.GET_VALUE)


@admin_route.message(calcTokens.GET_VALUE)
async def calc_summ_get_value(msg: Message, state: FSMContext):
    logging.info(f"{msg.from_user.id} - get token value")
    await state.set_state(calcTokens.GET_CURRENCY)
    await state.update_data(VALUE=int(msg.text))
    answer = (f"В чем отправлять будут?")
    await msg.answer(text=answer, reply_markup=ikb.create_callback_ikb(btns={"USDT": "USDT",
                                                                             "ETH": "ETH",
                                                                             "MATIC": "MATIC"},
                                                                       sizes=(1, 1, 1,)
                                                                       ))


@admin_route.callback_query(calcTokens.GET_CURRENCY)
async def calc_summ_get_curr(call: CallbackQuery, state: FSMContext):
    logging.info(f"{call.from_user.id} - get currency")
    data = await state.get_data()
    value = data["VALUE"]
    sum = summ_result(tokens_value=value, currency=call.data)

    answer = (f"{value} 🧲 = {sum} {call.data}\n"
              f"Адрес для отправки: <i>0x000000000000000000000000000000000</i>")

    await call.message.edit_text(text=answer)
    await state.clear()


# ################################## ADMIN_CHAT ###################################






