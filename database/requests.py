from database.models import Word

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, bindparam, text
from datetime import datetime

def days_ago(days: int):
    """
    Returns a SQL expression to shift the database time back by the specified number of days.

    :param days: Number of days to subtract from the current database time
    :return: SQL expression func.now() - interval 'x days'
    """
    return func.now() - text(f"interval '{days} days'")


class Database:
    def __init__(self, async_session: async_sessionmaker[AsyncSession]):
        self.session = async_session

    async def insert_objects(self) -> None:
        async with self.session() as session:
            async with session.begin():
                session.add_all(
                    [
                        Word(text='hello', last_review=days_ago(2), correct_count=5),
                        Word(text='rabbit'),
                        Word(text='redis'),
                        Word(text='asyncio'),
                        Word(text='django'),
                        Word(text='fastapi'),
                        Word(text='math'),
                        Word(text='flask'),
                        Word(text='aiohttp'),
                        Word(text='pytest'),
                        Word(text='unittest'),
                        Word(text='scrapy'),
                        Word(text='world'),
                        Word(text='python'),
                    ]
                )

    async def get_now_time(self):
        # Get current time from the database
        async with self.session() as session:
            stmt = select(func.now())
            now_time_result = await session.execute(stmt)

            now_time_db: datetime = now_time_result.scalar_one()
            now_time_db = now_time_db.replace(tzinfo=None)
            await session.commit()
            return now_time_db


    async def fetch_object(self):
        async with self.session() as session:

            # Get current time from the database
            stmt = select(func.now())
            now_time_result = await session.execute(stmt)
            now_time_db: datetime = now_time_result.scalar_one()
            now_time_db = now_time_db.replace(tzinfo=None)

            coefficient_strength = func.greatest(
                Word.correct_count * 0.8 - Word.wrong_count * 0.5,
                0
            )

            time_since_last_review_min = func.log(
                func.greatest(
                    func.extract('epoch', bindparam("now_time") - Word.last_review) / 60,
                    1
                )
            )

            memory_decay_factor = func.pow(time_since_last_review_min, 1.25)

            priority_expr = 100 * (1.84 + coefficient_strength) / (
                    1.84 + coefficient_strength + memory_decay_factor
            )

            stmt = (
                select(Word,
                       coefficient_strength.label("coefficient_strength"),
                       time_since_last_review_min.label("time_since_last_review_min"),
                       priority_expr.label("priority_expr"),
                       )
                .order_by(priority_expr.asc())
                #.limit(5)
                .params(now_time=now_time_db)
            )

            result = await session.execute(stmt)

            base_words = result.all()

            await session.commit()

            return now_time_db, base_words



