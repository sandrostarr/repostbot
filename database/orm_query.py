from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from database.models import User, Task, TaskAction


async def orm_add_user(session: AsyncSession, msg: Message):
    obj = User(
        telegram_id=msg.from_user.id,
        username=msg.from_user.username,
    )
    session.add(obj)
    await session.commit()
    return await orm_get_user(session=session, msg=msg)


# TODO потом отрефакторить метод
async def orm_get_user(session: AsyncSession, msg: Message, fid: int = None):
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


async def orm_top_up_user_balance_by_user_id(session: AsyncSession, user_id: int, balance_change: int):
    user = await orm_get_user_by_id(session=session, user_id=user_id)
    query = update(User).where(User.id == user_id).values(
        balance=user.balance + balance_change)
    await session.execute(query)
    await session.commit()


async def orm_write_off_user_balance(session: AsyncSession, msg: Message, balance_change: int):
    user = await orm_get_user(session=session, msg=msg)
    query = update(User).where(User.telegram_id == msg.from_user.id).values(
        balance=user.balance - balance_change)
    await session.execute(query)
    await session.commit()


async def orm_get_tasks(session: AsyncSession, task_type: str, not_completed: bool = True):
    if not_completed:
        query = select(Task).where(
            (Task.type == task_type) &
            (Task.is_completed == False)
        )
    else:
        query = select(Task).where(Task.type == task_type)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_task(session: AsyncSession, user_id: int, task_type: str, url: str, price: int, actions_count: int):
    obj = Task(
        user_id=user_id,
        type=task_type,
        url=url,
        price=price,
        actions_count=actions_count,
    )
    session.add(obj)
    await session.commit()


async def orm_add_task_action(session: AsyncSession, user_id: int, task_id: int):
    obj = TaskAction(
        task_id=task_id,
        user_id=user_id,
        is_completed=True,
    )
    session.add(obj)
    await session.commit()
