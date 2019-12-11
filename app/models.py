from datetime import datetime
from enum import Enum, unique

import sqlalchemy as sa
from sqlalchemy import MetaData, Column, DateTime, Integer, Enum as SaEnum, and_
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()


@unique
class Roles(Enum):
    group = 'group'
    lecturer = 'lecturer'


class CalendarFile(declarative_base(metadata=metadata)):
    __tablename__ = 'calendars'
    __table__: sa.sql.schema.Table

    _id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    id = Column(Integer, nullable=False)
    type = Column(SaEnum(Roles), nullable=False)
    last_update = Column(DateTime, nullable=False)
    last_use = Column(DateTime, nullable=False)

    @classmethod
    def add_file(cls, id: int, type: str) -> sa.sql:
        return cls.__table__.insert().values([
            dict(
                id=id,
                type=type,
                last_update=datetime.now(),
                last_use=datetime.now()
            )
        ])

    @classmethod
    def find_file(cls, id: int, type: str) -> sa.sql:
        return sa.select(
            [
                cls.id,
                cls.last_update,
                cls.last_use
            ]) \
            .where(and_(cls.id == id, cls.type == type))

    @classmethod
    def find_outdated(cls, age: datetime) -> sa.sql:
        return sa.select(
            [
                cls.id,
                cls.type
            ]) \
            .where(cls.last_update < age)

    @classmethod
    def find_unused(cls, age: datetime) -> sa.sql:
        print(type(cls.__table__))
        return sa.select(
            [
                cls.id,
                cls.type
            ]) \
            .where(cls.last_use < age)

    @classmethod
    def use(cls, id: int, type: str) -> sa.sql:
        return cls.__table__.update() \
            .values(last_use=datetime.now()) \
            .where(and_(cls.id == id, cls.type == type))

    @classmethod
    def update(cls, id: int, type: str) -> sa.sql:
        return cls.__table__.update() \
            .values(last_update=datetime.now()) \
            .where(and_(cls.id == id, cls.type == type))


calendar_table = CalendarFile.__table__
