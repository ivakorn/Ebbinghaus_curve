import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.base import Base
from database.requests import Database

import sys

#if you are working on the windows
if sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    engine = create_async_engine(url="postgresql+psycopg://superuser:superpassword@127.0.0.1/mydatabase",
                                 echo=True)



    async with engine.begin() as conn:
        # old version base drop
        await conn.run_sync(Base.metadata.drop_all)
        # new base create
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    db = Database(async_session)

    #insert all words to database
    await db.insert_objects()

    # for AsyncEngine created in function scope, close and clean-up pooled connections
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())