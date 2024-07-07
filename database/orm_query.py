from typing import Type

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from database.models import UserInfo

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