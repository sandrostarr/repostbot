import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base

engine = create_async_engine(os.getenv('DB_LITE'), echo=True)

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
    encapsulated_engine = create_async_engine('sqlite+aiosqlite:///../../db.db', echo=True)

    encapsulated_session_maker = async_sessionmaker(
        bind=encapsulated_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with encapsulated_session_maker() as session:
        return session
