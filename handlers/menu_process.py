from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Task, User
from database.orm_query import (orm_add_task_action, orm_top_up_user_balance_by_user_id, orm_verify_task_action,
                                increase_task_actions_completed_count)
from keyboard.inline import get_main_inline_kb, complete_task_kb, buy_token_kb
from utils.functions import get_action_earning
from handlers.action_checker import check_like_existence, check_recast_existence, check_follow_existence


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
):
    answer = (f"Переходи по ссылке и {task.type}\n\n"
              f"{url}")
    if approve:
        action_earning = get_action_earning(task.type)
        task_action = await orm_add_task_action(
            session=session,
            user_id=user.id,
            task_id=task.id,
        )

        check_success = False
        if task.type == 'LIKE':
            if await check_like_existence(cast_hash=task.cast_hash, fid=user.fid):
                check_success = True
        elif task.type == 'RECAST':
            if await check_recast_existence(cast_hash=task.cast_hash, fid=user.fid):
                check_success = True
        elif task.type == 'FOLLOW':
            # TODO доделать
            if await check_follow_existence(cast_hash=task.cast_hash, fid=user.fid):
                check_success = True

        if check_success:
            await orm_top_up_user_balance_by_user_id(session=session, user_id=user.id, balance_change=action_earning)
            await orm_verify_task_action(session=session, task_action=task_action)
            await increase_task_actions_completed_count(session=session, task=task)
        else:
            # TODO пока такую заглушку сделал. Возможно, надо как-то иначе сделать
            answer = f"Задание не выполнено. Перейти к следующему"

    kb = complete_task_kb(
        level=level,
        task_type=task.type,
        task_id=task.id,
        page=page,
        url=url,
        approve=approve,
        sizes=(1,)
    )

    return answer, kb


# покупка токенов пока заглушка
async def buy_token(
        sessioon: AsyncSession,
        level: int,
):
    answer = f"Только в ручном режиме, напиши @username"
    kb = buy_token_kb(
        level=level
    )

    return answer, kb


async def get_menu_content(
        session: AsyncSession,
        level: int,
        task: Task | None = None,
        user: User | None = None,
        page: int = 0,
        url: str | None = None,
        approve: bool = False

):
    if level == 0:
        return await task_menu(session, level)
    elif level == 1:
        return await task_complete(session, level, task, user, page, url, approve)
    elif level == 7:
        return await buy_token(session, level)
