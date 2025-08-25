import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models import Word
from database.requests import Database

import sys

#if you are working on the windows
if sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    engine = create_async_engine(url="postgresql+psycopg://superuser:superpassword@127.0.0.1/mydatabase",
                                 echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    db = Database(async_session)


    time_now, list_objs = await db.fetch_object()

    for i, obj in enumerate(list_objs, start=1):
        obj_word: Word = obj[0]

        priority = f"{obj.priority_expr:.2f}%"

        #time difference
        delta = time_now - obj_word.last_review
        #In minutes and hours/days
        minutes = int(delta.total_seconds() // 60)
        hours = minutes // 60
        days = hours // 24

        if days > 0:
            since = f"{days}d {hours % 24}h"
        elif hours > 0:
            since = f"{hours}h {minutes % 60}m"
        else:
            since = f"{minutes}m"

        print(f"#{i:<2} "
              f"{obj_word.text:<12} "  # word text
              f"{obj.coefficient_strength:<6}" #coefficient strength
              f"{obj_word.last_review:%d-%m-%Y %H:%M:%S}  "  # last time repetition
              f"{priority:<8} " 
              f"⏳ {since}")


    # for AsyncEngine created in function scope, close and clean-up pooled connections
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())