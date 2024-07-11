from aiogram.fsm.state import State, StatesGroup


class AddFid(StatesGroup):
    FID = State()


class CreateTask(StatesGroup):
    TASK_TYPE = State()
    TASK_ACTIONS_AMOUNT = State()
    TASK_URL = State()
