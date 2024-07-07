from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

import keyboard.reply as rkb
from database.orm_query import orm_add_user_info

user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_cmd(msg: Message, session: AsyncSession):
    answer = (f"Хало, {msg.from_user.full_name}.\n\n"
              "Прокачаем твой WARPCAST ???\n\n"
              "LFG!!!")
    await msg.delete()
    try:
        await orm_add_user_info(session=session,msg=msg)
        print('Данные добавлены')
    except:
        print('Не работает нихуя')
    await msg.answer(text=answer)


@user_private_router.message(Command("faq"))
async def faq_cmd(msg: Message):
    print(msg.chat.type)
    answer = (f'Ну типо вопрос ответ для всякой хуиты')
    await msg.delete()
    await msg.answer(text=answer, reply_markup=rkb.create_kb("Заработать токенсы",
                                                             "Заказать накрутку",
                                                             "Профиль",
                                                             "Мои заказы",
                                                             "База данных тестирование",
                                                             placeholder="Жмяк кряк",
                                                             sizes=(2,1,1,1)
                                                             ),

                     )

@user_private_router.message(F.text == 'База данных тестирование')
async def baase_testing(msg: Message):
    await msg.answer("1 этам", reply_markup=rkb.create_kb("Кнопка 2 DB",
                                                                placeholder="Кряк кряк",
                                                                sizes=(1,)))



