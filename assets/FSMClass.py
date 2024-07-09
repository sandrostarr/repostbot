from aiogram.fsm.state import State, StatesGroup


class addFID(StatesGroup):
    FID = State()

class createTask(StatesGroup):
    TASK_TYPE = State()
    NUMBER = State()
    URL = State()