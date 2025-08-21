from database.base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from datetime import datetime

from typing import List


class Word(Base):
    __tablename__ = 'dict_mean_link'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String)
    wrong_count: Mapped[int] = mapped_column(Integer, default='0')
    correct_count: Mapped[int] = mapped_column(Integer, default='0')
    last_review: Mapped[datetime] = mapped_column(server_default=func.now(),
                                                  onupdate=func.now())

