from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def create_kb(
        *btns: str,
        placeholder: str = None,
        sizes: tuple[int] = (1,),
):
    """
        Example:
        create_kb(
                "Button 1",
                "Button 2",
                "Button 3",
                "Button 4",
                placeholder="Example text",
                sizes: (2,1,1)
        )
    """

    keyboard = ReplyKeyboardBuilder()

    for i, text in enumerate(btns, start=0):
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )
