from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import MetaData, Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()


class CalendarFile(declarative_base(metadata=metadata)):
    __tablename__ = 'calendars'

    id = Column(Integer, primary_key=True, unique=True)
    last_update = Column(DateTime, nullable=False)
    last_use = Column(DateTime, nullable=False)

    @classmethod
    def add_file(cls, id: int) -> sa.sql:
        return cls.__table__.insert().values([
            dict(
                id=id,
                last_update=datetime.now(),
                last_use=datetime.now()
            )
        ])

    @classmethod
    def find_file(cls, id: int) -> sa.sql:
        return sa.select(
            [
                cls.id,
                cls.last_update,
                cls.last_use
            ]) \
            .where(cls.id == id)

    @classmethod
    def find_outdated(cls, age: datetime) -> sa.sql:
        return sa.select(
            [
                cls.id
            ]) \
            .where(cls.last_update < age)

    @classmethod
    def find_unused(cls, age: datetime) -> sa.sql:
        return sa.select(
            [
                cls.id
            ]) \
            .where(cls.last_use < age)

    @classmethod
    def use(cls, id: int) -> sa.sql:
        return cls.__table__.update().values(last_use=datetime.now()).where(cls.id == id)


calendar_table = CalendarFile.__table__
