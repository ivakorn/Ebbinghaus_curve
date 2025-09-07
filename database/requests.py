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
                        Word(text="go", last_review=days_ago(1), correct_count=10, wrong_count=1),
                        Word(text="come", last_review=days_ago(2), correct_count=21, wrong_count=2),
                        Word(text="see", last_review=days_ago(3), correct_count=30, wrong_count=3),
                        Word(text="circumstances", last_review=days_ago(4), correct_count=42, wrong_count=40),
                        Word(text="take", last_review=days_ago(5), correct_count=51, wrong_count=5),
                        Word(text="think", last_review=days_ago(6), correct_count=60, wrong_count=6),
                        Word(text="get", last_review=days_ago(7), correct_count=72, wrong_count=7),
                        Word(text="run", last_review=days_ago(8), correct_count=81, wrong_count=30),
                        Word(text="make", last_review=days_ago(9), correct_count=90, wrong_count=20),
                        Word(text="write", last_review=days_ago(10), correct_count=102, wrong_count=10),
                        Word(text="find", last_review=days_ago(11), correct_count=111, wrong_count=11),
                        Word(text="eat", last_review=days_ago(12), correct_count=120, wrong_count=42),
                        Word(text="give", last_review=days_ago(13), correct_count=132, wrong_count=23),
                        Word(text="know", last_review=days_ago(14), correct_count=141, wrong_count=14),
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


    async def fetch_object(self, limit=None):
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

            time_since_last_review_min = func.greatest(
                    func.extract('epoch', bindparam("now_time") - Word.last_review) / 60,
                    1
                )

            time_since_last_review_min_log = func.log(time_since_last_review_min)

            memory_decay_factor = func.pow(time_since_last_review_min_log, 1.25)

            priority_expr = 100 * (1.84 + coefficient_strength) / (
                    1.84 + coefficient_strength + memory_decay_factor
            )

            stmt = (
                select(Word,
                       coefficient_strength.label("coefficient_strength"),
                       time_since_last_review_min.label("time_since_last_review_min"),
                       time_since_last_review_min_log.label("time_since_last_review_min_log"),
                       memory_decay_factor.label("memory_decay_factor"),
                       priority_expr.label("priority_expr"),
                       )
                .order_by(priority_expr.asc())
                .limit(limit)
                .params(now_time=now_time_db)
            )

            result = await session.execute(stmt)

            base_words = result.all()

            await session.commit()

            return now_time_db, base_words



