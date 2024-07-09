from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import Paginator
from keyboard.inline import get_main_inline_kb, complete_task_kb


# освное меню для заданий
#TODO: заменить TASKTYPE на подгрузку данных из БД и настрость пагинацию
async def task_menu(session, level, menu_name):
    answer = "Выбери задания которые по душе и выполняй их"
    task_type = {
        "LIKE": "TASKS",
        "RECAST": "TASKS",
        "FOLLOW": "TASKS",
    }
    kb = get_main_inline_kb(level=level, task_type=task_type, sizes=(3,1))
    return answer, kb


#TODO: task_id сделать как ссылки так номера заданий сделать из БД запросы
async def task_complete(
        session: AsyncSession,
        level: int,
        task_type: str,
        page: int,
        task_id: dict,
        link: str,
        approve: bool = False,
):
    task_id = {
        231242, "google.com",
        467823, "google.com",
        200727, "google.com",
        242873, "google.com",
        119283, "google.com",
    },

    paginator = Paginator(task_id, page=page)
    data = paginator.get_page()[0]

    answer = (f"Преходи по ссылке и {data.name}"
              f"{data.link}")

    pagination_btns = pages(paginator)

    kb = complete_task_kb(
        level=level,
        task_type=task_type,
        task_id=task_id,
    )

    return answer, kb


async def get_menu_content(
        session: AsyncSession,
        level: int,
        menu_name: str,
        task_type: str | None = None,
        page: int = 1,
        task_id: dict | None = None,
        approve: bool = False

):
    if level==0:
        return await task_menu(session,level,menu_name)
    elif level==1:
        return await task_complete(session,level,task_type,page,task_id,approve)