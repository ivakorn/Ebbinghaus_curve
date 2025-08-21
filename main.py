import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.base import Base
from database.requests import Database


async def main_async():
    engine = create_async_engine(url="postgresql+psycopg://superuser:superpassword@127.0.0.1/mydatabase",
                                 echo=True)

    #old version base drop
    #new base create
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    db = Database(async_session)

    await db.insert_objects()

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main_async())