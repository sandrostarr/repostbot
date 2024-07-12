from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_tasks
from keyboard.inline import get_main_inline_kb, complete_task_kb, buy_token_kb


# освное меню для заданий
async def task_menu(session, level):
    answer = "Выбери задания которые по душе и выполняй их"
    kb = get_main_inline_kb(level=level, sizes=(3,1))
    return answer, kb



async def task_complete(
        session: AsyncSession,
        level: int,
        task_type: str,
        task_id: str | None = None,
        page: int = 1,
        url: str | None = None,
        approve: bool = False,
):

    answer = (f"Преходи по ссылке и {task_type}\n\n"
              f"{url}")
    if approve:
        answer = (f"Давай Следующий")
        #TODO: запись в БД

    kb = complete_task_kb(
        level=level,
        task_type=task_type,
        task_id=task_id,
        page=page,
        url=url,
        approve=approve,
        sizes=(1, )
    )

    return answer, kb


#покупка токенов пока заглушка
async def buy_token(
        sessioon: AsyncSession,
        level: int,
):
    answer = (f"Сорян пока нет такой возможности, но принимаем DONATION")
    kb = buy_token_kb(
        level = level
    )

    return answer, kb




async def get_menu_content(
        session: AsyncSession,
        level: int,
        task_type: str | None = None,
        task_id: str | None = None,
        page: int = 1,
        url: str | None = None,
        approve: bool = False

):
    if level==0:
        return await task_menu(session,level)
    elif level==1:
        return await task_complete(session,level,task_type,task_id,page,url,approve)
    elif level==7:
        return await buy_token(session,level)
