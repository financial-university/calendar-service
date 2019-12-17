import logging
from asyncio import sleep
from datetime import datetime, timedelta
from os import path

from aiohttp import ClientSession
from aiohttp.web import Application, view
from aiomisc.io import async_open
from aiomisc.service.aiohttp import AIOHTTPService
from aiomisc.service.periodic import PeriodicService
import sqlalchemy as sa
import ujson

from app.calendar_creator import download_calendar, EmptySchedule
from app.dependency import connection
from app.handlers import CalendarView
from app.models import CalendarFile
from app.schemas import GroupsListSchema, LecturersListSchema

log = logging.getLogger(__name__)


class CalendarService(AIOHTTPService):
    __dependencies__ = ("db_write",)

    db_write: connection
    ics_folder: str

    async def create_application(self) -> Application:
        app = Application()
        app["db_write"] = self.db_write
        app["ics_folder"] = self.ics_folder
        app.add_routes([
            view(r"/calendar/{type:(group|lecturer)}/{id:\d+}", CalendarView),
        ])

        return app


class CalendarUpdater(PeriodicService):
    __dependencies__ = ("db_write",)

    db_write: connection
    ics_folder: str

    async def callback(self):
        time = datetime.now() - timedelta(hours=4)
        async with self.db_write() as conn:
            ids_to_update_query = await conn.execute(CalendarFile.find_outdated(time))
            ids_to_update = [(i['id'], i['type'].value) for i in await ids_to_update_query.fetchall()]
            log.info('Updating %s groups', len(ids_to_update))
            for id, type in ids_to_update:
                try:
                    calendar = await download_calendar(id, type)
                except EmptySchedule:
                    log.warning('Error updating schedule for %s %r', type, id)
                    continue
                self.loop.create_task(conn.execute(CalendarFile.update(id, type)))
                async with async_open(path.join(self.ics_folder, f'{type}_{id}.ics'), 'wb') as file:
                    await file.write(calendar)


class RuzGrabber(PeriodicService):
    files_folder: str

    GROUPS_LIST = GroupsListSchema()
    LECTURERS_LIST = LecturersListSchema()

    @staticmethod
    async def get_from_api(client, type: str):
        groups = await client.get(f'https://ruz.fa.ru/api/dictionary/{type}')
        return await groups.json()

    async def callback(self):
        async with ClientSession() as client:
            groups = await self.get_from_api(client, 'groups')
            if not groups:
                await sleep(1)
                groups = await self.get_from_api(client, 'groups')
            groups = self.GROUPS_LIST.load(groups)
            async with async_open(path.join(self.files_folder, 'groups.json'), 'w') as file:
                await file.write(ujson.dumps(groups))

            lecturers = await self.get_from_api(client, 'lecturers')
            if not lecturers:
                await sleep(1)
                lecturers = await self.get_from_api(client, 'lecturers')
            lecturers = self.LECTURERS_LIST.load(lecturers)
            async with async_open(path.join(self.files_folder, 'lecturers.json'), 'w') as file:
                await file.write(ujson.dumps(lecturers))
            log.info('json files updated')


class Koctil(PeriodicService):
    """
    Обращения к базе раз в двадцать минут
    Вдруг поможет
    Лел 🙃
    """
    __dependencies__ = ("db_write",)

    db_write: connection

    async def callback(self):
        async with self.db_write() as conn:
            await conn.scalar(sa.select([1]))
