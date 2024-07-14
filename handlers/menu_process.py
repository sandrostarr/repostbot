from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_task_action, orm_top_up_user_balance_by_user_id
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
        task_type: str,
        task_id: int,
        user_id: int,
        page: int = 0,
        url: str | None = None,
        approve: bool = False,
):
    answer = (f"Переходи по ссылке и {task_type}\n\n"
              f"{url}")
    if approve:
        action_earning = get_action_earning(task_type)
        await orm_add_task_action(
            session=session,
            user_id=user_id,
            task_id=task_id,
        )
        # TODO сделано для тестов. Перед начислением токенов необходимо добавить проверку на наличие лайка и пр.
        await orm_top_up_user_balance_by_user_id(session=session, user_id=user_id, balance_change=action_earning)
        answer = f"Давай Следующий"

    kb = complete_task_kb(
        level=level,
        task_type=task_type,
        task_id=task_id,
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
    answer = (f"Сорян пока нет такой возможности, но принимаем DONATION")
    kb = buy_token_kb(
        level=level
    )

    return answer, kb


async def get_menu_content(
        session: AsyncSession,
        level: int,
        task_type: str | None = None,
        task_id: int | None = None,
        user_id: int | None = None,
        page: int = 0,
        url: str | None = None,
        approve: bool = False

):
    if level == 0:
        return await task_menu(session, level)
    elif level == 1:
        return await task_complete(session, level, task_type, task_id, user_id, page, url, approve)
    elif level == 7:
        return await buy_token(session, level)
