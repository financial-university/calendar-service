import logging
from datetime import datetime, timedelta
from os import path

from aiohttp.web import Application
from aiomisc.io import async_open
from aiomisc.service.aiohttp import AIOHTTPService
from aiomisc.service.periodic import PeriodicService

from app.calendar_creator import download_calendar, EmptySchedule
from app.dependency import connection
from app.handlers import CalendarView
from app.models import CalendarFile

log = logging.getLogger(__name__)


class CalendarService(AIOHTTPService):
    __dependencies__ = ("db_write", "ics_folder")

    db_write: connection
    ics_folder: str

    async def create_application(self) -> Application:
        app = Application()
        app["db_write"] = self.db_write
        app["ics_folder"] = self.ics_folder
        app.router.add_view(r"/calendar/{type:(group|lecturer)}/{id:\d+}", CalendarView)

        return app


class CalendarUpdater(PeriodicService):
    __dependencies__ = ("db_write", "ics_folder")

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
