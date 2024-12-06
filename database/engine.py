import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

engine = create_async_engine(os.getenv('DB_URL'))

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# создает все таблицы из models
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# удалить все таблицы если нужно
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> AsyncSession:
    # TODO вот тут говнокод сделал, заебала эта сессия
    # Для работы с sqlite использовать вот такой конфиг: 'sqlite+aiosqlite:///../../db.db'
    encapsulated_engine = create_async_engine(os.getenv('DB_URL'), echo=True)

    encapsulated_session_maker = async_sessionmaker(
        bind=encapsulated_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with encapsulated_session_maker() as session:
        return session
