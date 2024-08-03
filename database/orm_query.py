from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from database.models import User, Task, TaskAction
from errors.InsufficientFundsException import InsufficientFundsException


async def orm_add_user(session: AsyncSession, msg: Message):
    try:
        inviter = msg.text.split('ref', 1)[1].strip()
    except:
        inviter = ''

    obj = User(
        telegram_id=msg.from_user.id,
        username=msg.from_user.username,
        inviter=inviter
    )
    session.add(obj)
    await session.commit()
    return await orm_get_user(session=session, msg=msg)


# TODO потом отрефакторить метод
async def orm_get_user(session: AsyncSession, msg: Message = None, fid: int = None):
    if fid is not None:
        query = select(User).where(User.fid == fid)
    else:
        query = select(User).where(User.telegram_id == msg.from_user.id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_user_by_id(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_user_by_tg_id(session: AsyncSession, telegram_id: int):
    query = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_user_by_username(session: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await session.execute(query)
    return result.scalar()


# TODO в дальнейшем апдейт пользовательских данных можно будет собрать в один метод, сейчас пока похер
async def orm_update_user_fid(session: AsyncSession, msg: Message, fid: int):
    query = update(User).where(User.telegram_id == msg.from_user.id).values(
        fid=fid)
    await session.execute(query)
    await session.commit()


async def orm_top_up_user_balance(session: AsyncSession, msg: Message, balance_change: int):
    user = await orm_get_user(session=session, msg=msg)
    query = update(User).where(User.telegram_id == msg.from_user.id).values(
        balance=user.balance + balance_change)
    await session.execute(query)
    await session.commit()


async def orm_top_up_user_balance_by_tg_id(session: AsyncSession, telegram_id: int, balance_change: int):
    user = await orm_get_user_by_tg_id(session=session, telegram_id=telegram_id)
    query = update(User).where(User.telegram_id == telegram_id).values(
        balance=user.balance + balance_change)
    await session.execute(query)
    await session.commit()


async def orm_top_up_user_balance_by_user_id(session: AsyncSession, user_id: int, balance_change: int):
    user = await orm_get_user_by_id(session=session, user_id=user_id)
    query = update(User).where(User.id == user_id).values(
        balance=user.balance + balance_change)
    await session.execute(query)
    await session.commit()


async def orm_top_up_user_freeze_balance_by_user_id(session: AsyncSession, user_id: int, balance_change: int):
    user = await orm_get_user_by_id(session=session, user_id=user_id)
    query = update(User).where(User.id == user_id).values(
        freeze_balance=user.freeze_balance + balance_change)
    await session.execute(query)
    await session.commit()


async def orm_write_off_user_balance(session: AsyncSession, msg: Message, balance_change: int):
    user = await orm_get_user(session=session, msg=msg)

    if user.balance < balance_change:
        raise InsufficientFundsException

    query = update(User).where(User.telegram_id == msg.from_user.id).values(
        balance=user.balance - balance_change)
    await session.execute(query)
    await session.commit()


async def orm_write_off_user_freeze_balance(session: AsyncSession, telegram_id: int, balance_change: int):
    user = await orm_get_user_by_tg_id(session=session, telegram_id=telegram_id)

    if user.freeze_balance < balance_change:
        raise InsufficientFundsException

    query = update(User).where(User.telegram_id == telegram_id).values(
        freeze_balance=user.freeze_balance - balance_change)
    await session.execute(query)
    await session.commit()


# TODO можно разделить метод на 2 (получение всех заданий и получение заданий с фильтрами на выполнение, user_id и т.д.)
async def orm_get_tasks(session: AsyncSession, task_type: str, user_id: int, not_completed: bool = True):
    if not_completed:
        query = (select(Task).join(
            TaskAction,
            (TaskAction.task_id == Task.id) & (TaskAction.user_id == user_id),
            isouter=True,
        ).where(
            (Task.type == task_type) &
            (Task.user_id != user_id) &
            (Task.is_completed == False) &
            (
                    (TaskAction.id == None) |
                    (
                            (TaskAction.is_verified == False) &
                            (TaskAction.is_completed == False)
                    )
            )
        ))
    else:
        query = select(Task).where(Task.type == task_type)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_tasks_by_user_id(session: AsyncSession, user_id: int):
    query = select(Task).where(Task.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_tasks_by_id(session: AsyncSession, task_ids: list):
    query = select(Task).where(Task.id.in_(task_ids))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_task(
        session: AsyncSession,
        user_id: int,
        telegram_id: int,
        creator_fid: int,
        task_type: str,
        url: str,
        price: int,
        actions_count: int,
        cast_hash: str = None,
):
    obj = Task(
        user_id=user_id,
        telegram_id=telegram_id,
        creator_fid=creator_fid,
        type=task_type,
        url=url,
        cast_hash=cast_hash,
        price=price,
        actions_count=actions_count,
    )
    session.add(obj)
    await session.commit()


async def update_task(
        session: AsyncSession,
        cast_hash: str,
        actions_count: int,
):
    task = await orm_get_task_by_hash(session=session,cast_hash=cast_hash)
    query = update(Task).where(Task.cast_hash == cast_hash).values(
        actions_count=task.actions_count + actions_count)
    await session.execute(query)
    await session.commit()


async def update_task_follow(
        session: AsyncSession,
        url: str,
        actions_count: int,
):
    task = await orm_get_task_by_link(session=session,url=url)
    query = update(Task).where(Task.url == url).values(
        actions_count=task.actions_count + actions_count)
    await session.execute(query)
    await session.commit()


async def orm_increase_task_actions_completed_count(session: AsyncSession, task: Task):
    actions_completed = task.actions_completed + 1
    task.actions_completed = actions_completed

    if actions_completed > task.actions_count:
        task.is_completed = True

    session.add(task)
    await session.commit()


async def orm_decrease_task_actions_completed_count(session: AsyncSession, task: Task):
    actions_completed = task.actions_completed - 1
    task.actions_completed = actions_completed

    if actions_completed >= task.actions_count:
        task.is_completed = True
    else:
        task.is_completed = False

    session.add(task)
    await session.commit()


async def orm_add_task_action(session: AsyncSession, user_id: int, task_id: int, telegram_id: int,
                              user_fid: int = None):
    obj = TaskAction(
        task_id=task_id,
        user_id=user_id,
        telegram_id=telegram_id,
        user_fid=user_fid,
        is_completed=True,
    )
    session.add(obj)
    await session.commit()
    return obj


async def orm_get_task_action(session: AsyncSession, user_id: int, task_id: int):
    query = select(TaskAction).where(
        (TaskAction.user_id == user_id) &
        (TaskAction.task_id == task_id)
    )
    result = await session.execute(query)
    return result.scalar()


async def orm_get_task_actions_for_verification(session: AsyncSession):
    query = select(TaskAction).where(
        (TaskAction.is_verified == False) &
        (TaskAction.is_completed == True)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def orm_verify_task_action(session: AsyncSession, task_action: TaskAction):
    task_action.is_verified = True
    session.add(task_action)
    await session.commit()


async def orm_set_complete_task_action(session: AsyncSession, task_action: TaskAction):
    task_action.is_completed = True
    session.add(task_action)
    await session.commit()


async def orm_remove_complete_task_action(session: AsyncSession, task_action: TaskAction):
    task_action.is_completed = False
    session.add(task_action)
    await session.commit()


async def orm_get_task_by_hash(
        session: AsyncSession,
        cast_hash: str
):
    query = select(Task).where(Task.cast_hash == cast_hash)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_task_by_link(
        session: AsyncSession,
        url: str
):
    query = select(Task).where(Task.url == url)
    result = await session.execute(query)
    return result.scalars().all()

