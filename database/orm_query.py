import math
from typing import Type

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from database.models import UserInfo


#TODO: класс для пагинации и работы с БД взял с урока надо посчмотреть и может адаптировать
class Paginator:
    def __init__(self, array: list | tuple, page: int = 1, per_page: int=1):
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








#TODO: запрос FID нужно убрать и вытсавить наальные значения в таблицк как null
async def orm_add_user_info(session: AsyncSession, msg: Message):
    obj = UserInfo(
            telegram_id=msg.from_user.id,
            username=msg.from_user.username,
            fid=10101010,
        )
    session.add(obj)
    await session.commit()


async def orm_get_data_from_db(session: AsyncSession, db_name: Type[object] ):
    query = select(db_name)
    result = await session.execute(query)
    return result.scalar().all()


async def orm_get_data_from_db(session: AsyncSession, db_name: Type[object], **filters):
    query = select(db_name).filter_by(**filters)
    result = await session.execute(query)
    return result.scalar()