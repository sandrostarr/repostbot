import logging

from sqlalchemy.ext.asyncio import AsyncSession
from bot_creator import bot
from database.models import Task, User
import database.orm_query as q
from errors import DBRequiresException
from keyboard.inline import get_main_inline_kb, complete_task_kb, buy_token_kb
from utils.functions import get_action_earning


# основное меню для заданий
async def task_menu(session, level):
    answer = "Выбери задания которые по душе и выполняй их"
    kb = get_main_inline_kb(level=level, sizes=(3, 1))
    return answer, kb


async def task_complete(
        session: AsyncSession,
        level: int,
        task: Task,
        user: User,
        page: int = 0,
        url: str | None = None,
        approve: bool = False,
        is_last_task: bool = False,
):
    answer = (f"Переходи по ссылке и {task.type}\n\n"
              f"{url}")
    if approve:
        action_earning = get_action_earning(task.type)

        task_action = await q.orm_get_task_action(session=session, user_id=user.id, task_id=task.id)
        if task_action is None:
            await q.orm_add_task_action(
                session=session,
                user_id=user.id,
                task_id=task.id,
                telegram_id=user.telegram_id,
                user_fid=user.fid,
            )
        try:
            await q.orm_top_up_user_freeze_balance_by_user_id(
                session=session,
                user_id=user.id,
                balance_change=action_earning,
            )
            await q.orm_increase_task_actions_completed_count(session=session, task=task)
            if task_action.is_completed is False:
                await q.orm_set_complete_task_action(session=session, task_action=task_action)
        except DBRequiresException as e:
            logging.warning(e)

    kb = complete_task_kb(
        level=level,
        task_type=task.type,
        task_id=task.id,
        page=page,
        url=url,
        sizes=(1,),
        approve=approve,
        is_last_task=is_last_task,
    )

    return answer, kb


# покупка токенов пока заглушка
async def buy_token(
        session: AsyncSession,
        level: int,
        telegram_id: int = 0
):

    answer = f"Только в ручном режиме, напиши @warp_booster"
    # answer = f"не беси так и надо"
    kb = buy_token_kb(
        level=level,
    )

    return answer, kb


async def get_menu_content(
        session: AsyncSession,
        level: int,
        task: Task | None = None,
        user: User | None = None,
        telegram_id: int = 0,
        page: int = 0,
        url: str | None = None,
        approve: bool = False,
        is_last_task: bool = False,

):
    if level == 0:
        return await task_menu(session, level)
    elif level == 1:
        return await task_complete(session, level, task, user, page, url, approve, is_last_task)
    elif level == 7:
        return await buy_token(session, level, telegram_id)
