from database.models import Word

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

class Database:
    def __init__(self, async_session: async_sessionmaker[AsyncSession]):
        self.session = async_session

    async def insert_objects(self) -> None:
        async with self.session() as session:
            async with session.begin():
                session.add_all(
                    [
                        Word(text='hello'),
                        Word(text='rabbit'),
                        Word(text='redis'),
                        Word(text='asyncio'),
                        Word(text='welcome'),
                    ]
                )
