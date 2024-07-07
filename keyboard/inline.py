from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

#обработка callback и создание меню
class MenuCallback(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    task_type: str | None = None
    page: int = 1
    task_id: int | None = None
    link: str | None = None
    approve: bool = False




#TODO: заменить TASKTYPE на подгрузку данных из БД
#меню при нажатии на кнопку заработать
def get_main_inline_kb(
        *,
        level: int,
        task_type,
        sizes: tuple[int] = (1,),
):
    keyboard = InlineKeyboardBuilder()

    for name, data in task_type.items():
        keyboard.add(InlineKeyboardButton(text=name,
                                          callback_data=MenuCallback(level=level+1, menu_name=data, task_type=name).pack()))

    keyboard.add(InlineKeyboardButton(text="КУПИТЬ ТОКЕНСЫ",
                                      callback_data=MenuCallback(level=777, menu_name="BUY_TOKENS").pack()))

    return keyboard.adjust(*sizes).as_markup()



#меню для выполнения заданий после выбора типа заданий
def complete_task_kb(
        *,
        level: int,
        menu_name: str | None = None,
        task_type: int,
        page: int,
        task_id: int,
        sizes: tuple[int] = (1,),
        link: str | None = None,
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='ПЕРЕЙТИ НА CAST',
                                      url=link))
    keyboard.add(InlineKeyboardButton(text='ВЫПОЛНИЛ',
                                      callbacl_data=MenuCallback(level=level,
                                                                 task_type=task_type,
                                                                 task_id=task_id,
                                                                 approve=True).pack()))


    keyboard.add(InlineKeyboardButton(text='СЛЕД. ЗАДАНИЕ',
                                      callbacl_data=MenuCallback(level=level,
                                                                 task_type=task_type,
                                                                 page=page+1,
                                                                 approve=False,
                                                                 ).pack()))


    keyboard.add(InlineKeyboardButton(text='НАЗАД',
                                      callbacl_data=MenuCallback(level=level,
                                                                 menu_name="BUY_TOKENS",
                                                                 task_type=task_type,
                                                                 task_id=task_id,
                                                                 approve=True).pack()))

    return keyboard.adjust(1,1,1,1).as_markup()



# #все что нижу под снос
# # создать клавиатуру с callback_data
# def create_callback_ikb(
#         *,
#         btns: dict[str, str],
#         sizes: tuple[int] = (1,)
# ):
#     keyboard = InlineKeyboardBuilder()
#
#     for text, data in btns.items():
#         keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
#     return keyboard.adjust(*sizes).as_markup()
#
#
# # создать клавиатуру с URL кнопкой
# def create_url_ikb(
#         *,
#         btns: dict[str, str],
#         sizes: tuple[int] = (1,)
# ):
#     keyboard = InlineKeyboardBuilder()
#
#     for text, url in btns.items():
#         keyboard.add(InlineKeyboardButton(text=text, url=url))
#     return keyboard.adjust(*sizes).as_markup()
#
#
#
#
# def create_mix_ikb(
#         *,
#         btns: dict[str,str],
#         sizes: tuple[int] = (1,)
# ):
#     keyboard = InlineKeyboardBuilder()
#
#     for text, value in btns.items():
#         if '://' in value:
#             keyboard.add(InlineKeyboardButton(text=text,url=value))
#         else:
#             keyboard.add(InlineKeyboardButton(text=text,callback_data=value))
#
#     return keyboard.adjust(*sizes).as_markup()