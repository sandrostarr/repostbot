from aiogram.fsm.state import State, StatesGroup


class AddFid(StatesGroup):
    FID = State()


class CreateTask(StatesGroup):
    TASK_TYPE = State()
    TASK_ACTIONS_AMOUNT = State()
    TASK_URL = State()


class AdminTopUp(StatesGroup):
    GET_TG_ID = State()
    GET_TOP_UP = State()
    GET_APPROVE = State()


class calcTokens(StatesGroup):
    GET_VALUE = State()
    GET_CURRENCY = State()
