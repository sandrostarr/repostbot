import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base


engine = create_async_engine(os.getenv('DB_LITE'), echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


#создает все таблицы из models
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


#удалить все таблицы если нужно
async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
