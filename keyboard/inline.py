from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# обработка callback и создание меню
class MenuEarnCallback(CallbackData, prefix="menu_earn"):
    level: int
    task_type: str | None = None
    task_id: int | None = None
    page: int = 0
    url: str | None = None
    approve: bool = False


# меню при нажатии на кнопку заработать
def get_main_inline_kb(
        *,
        level: int,
        sizes: tuple[int] = (1,),
):
    task_type = {
        "LIKE": "TASK",
        "RECAST": "TASKS",
        "FOLLOW": "TASKS",
    }
    keyboard = InlineKeyboardBuilder()

    for name, data in task_type.items():
        keyboard.add(InlineKeyboardButton(text=name,
                                          callback_data=MenuEarnCallback(level=level + 1, menu_name=data,
                                                                         task_type=name).pack()))

    keyboard.add(InlineKeyboardButton(text="КУПИТЬ ТОКЕНСЫ",
                                      callback_data=MenuEarnCallback(level=7, menu_name="BUY_TOKENS").pack()))

    return keyboard.adjust(*sizes).as_markup()


# меню для выполнения заданий после выбора типа заданий
def complete_task_kb(
        *,
        level: int,
        task_type: str,
        task_id: int,
        page: int,
        url: str,
        sizes: tuple[int] = (1,),
        approve: bool = False
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text="ПЕРЕЙТИ НА CAST",
                                      url=url))
    if not approve:
        keyboard.add(InlineKeyboardButton(text="ВЫПОЛНИЛ",
                                          callback_data=MenuEarnCallback(level=level,
                                                                         task_type=task_type,
                                                                         page=page,
                                                                         task_id=task_id,
                                                                         approve=True).pack()))

    keyboard.add(InlineKeyboardButton(text='СЛЕД. ЗАДАНИЕ',
                                      callback_data=MenuEarnCallback(level=1,
                                                                     task_type=task_type,
                                                                     page=page + 1,
                                                                     approve=False,
                                                                     ).pack()))

    keyboard.add(InlineKeyboardButton(text='НАЗАД',
                                      callback_data=MenuEarnCallback(level=0,
                                                                     task_type=task_type).pack()))

    return keyboard.adjust(*sizes).as_markup()


def buy_token_kb(
        *,
        level: int,
        task_type: str | None = None
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='НАЗАД', callback_data=MenuEarnCallback(level=0,
                                                                                   task_type=task_type).pack()))

    return keyboard.adjust().as_markup()


# создать клавиатуру с callback_data
def create_callback_ikb(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


# создать клавиатуру с URL кнопкой
def create_url_ikb(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))
    return keyboard.adjust(*sizes).as_markup()


def create_mix_ikb(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (1,)
):
    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()
