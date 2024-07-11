import math
from typing import Type

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from database.models import User, Task


# TODO: класс для пагинации и работы с БД взял с урока надо посчмотреть и может адаптировать
class Paginator:
    def __init__(self, array: list | tuple, page: int = 1, per_page: int = 1):
        self.array = array
        self.per_page = per_page
        self.page = page
        self.len = len(self.array)

        self.pages = math.ceil(self.len / self.per_page)

    def __get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start * self.per_page
        return self.array[start:stop]

    def get_page(self):
        page_item = self.__get_slice()
        return page_item

    def has_next(self):
        if self.page < self.pages:
            return self.page + 1
        return False


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


# TODO в дальнейшем апдейт пользовательских данных можно будет собрать в один метод, сейчас пока похер
async def orm_update_user_fid(session: AsyncSession, msg: Message, fid: int):
    query = update(User).where(User.telegram_id == msg.from_user.id).values(
        fid=fid)
    await session.execute(query)
    await session.commit()


async def orm_top_up_user_balance(session: AsyncSession, msg: Message, balance: int):
    user = await orm_get_user(session=session, msg=msg)
    query = update(User).where(User.telegram_id == msg.from_user.id).values(
        balance=user.balance + balance)
    await session.execute(query)
    await session.commit()


async def orm_get_tasks(session: AsyncSession, task_type: str):
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
