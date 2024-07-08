from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

import keyboard.reply as rkb
import keyboard.inline as ikb
from database.orm_query import orm_add_user, orm_get_user, orm_top_up_user_balance
from handlers.menu_process import get_menu_content

user_private_router = Router()


#TODO: вынести в файл c обработчиками команд
@user_private_router.message(CommandStart())
async def start_cmd(msg: Message, session: AsyncSession):
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
async def faq_cmd(msg: Message):
    print(msg.chat.type)
    #TODO: написать мини промт как работает наш сервис
    answer = (f'Ну типо вопрос ответ для всякой хуиты')
    await msg.delete()
    await msg.answer(text=answer)


# начало работы с заработком монет за действия
@user_private_router.message(F.text == "Заработать токенсы")
async def earn_buy_tokens(msg: Message, session: AsyncSession):
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


@user_private_router.callback_query(ikb.MenuCallback.filter())
async def func_1(call: CallbackQuery, callback_data: ikb.MenuCallback, session: AsyncSession):
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

#все что ниже пока закомитил, тренировался с функциями
# #TODO: подшружать первый квест на LIKE действие и заменить переменные
# @user_private_router.callback_query(F.data.startswith("TASK_"))
# async def start_earn(call: CallbackQuery):
#     answer = ''
#     if call.data.endswith("LIKE"):
#         answer = 'Лайки лайки лайки лайки'
#     elif call.data.endswith("RECAST"):
#         answer = 'рекаст рекаст рекаст'
#     elif call.data.endswith("FOLLOW"):
#         answer = 'подсвинота подписечники фоловинги'
#     else:
#         await call.answer('ШО ЗА???')
#         return
#     await call.message.edit_text(text=answer,
#                                  reply_markup=ikb.create_mix_ikb(
#                                      btns={"ПЕРЕЙТИ НА CAST": f'http://google.com',  #TODO:Заменить на ссылки с DB
#                                            "ВЫПОЛНИЛ": f'DONE',
#                                            #TODO:Заменить на ответ в BD о выполнение и дальнейше проверке
#                                            "ПРОПУСТИТЬ": f'SKIP_TASK'},
#                                      #TODO: можно делать отметку о пропуске либо просто оставить как замена на следующий таск
#                                      sizes=(1, 1, 1)
#                                      )
#                                  )
#
#
# # TODO:Заменить на ответ в BD о выполнение и дальнейше проверке
# # заменяет клавиатуру прошлого выбора на клавиатуру после выполнения
# @user_private_router.callback_query(F.data == 'DONE')
# async def complete_task(call: CallbackQuery):
#     print(call.data)
#     answer = 'Like Like Like'
#     await call.message.edit_text(text=answer,
#                                  reply_markup=ikb.create_mix_ikb(
#                                      btns={"ПЕРЕЙТИ НА CAST": f'http://google.com',  #TODO:Заменить на ссылки с DB
#                                            "СЛЕДУЮЩЕЕ": f'SKIP_TASK'},
#                                      #TODO: можно делать отметку о пропуске либо просто оставить как замена на следующий таск
#                                      sizes=(1, 1)
#                                      )
#                                  )


@user_private_router.message(F.text == "Профиль")
async def show_profile_data(msg: Message, session: AsyncSession):
    user = await orm_get_user(session=session, msg=msg)
    await msg.answer(text="У вас накоплено " + str(user.balance) + " деняк")
