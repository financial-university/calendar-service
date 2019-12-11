import logging
from os import path

from aiomisc.io import async_open
from aiohttp.web import View, HTTPNotFound
from aiohttp.web_response import Response

from app.calendar_creator import download_calendar, EmptySchedule
from app.dependency import connection
from app.models import CalendarFile

log = logging.getLogger(__name__)


class BaseView(View):
    @property
    def db(self) -> connection:
        return self.request.app["db_write"]

    @property
    def ics_folder(self) -> str:
        return self.request.app["ics_folder"]


class CalendarView(BaseView):
    async def get(self):
        type = self.request.match_info['type']
        id = self.request.match_info['id']
        async with self.db() as conn:
            result = await conn.execute(CalendarFile.find_file(id, type))
            if not result.rowcount:
                try:
                    calendar = await download_calendar(id, type)
                except EmptySchedule:
                    raise HTTPNotFound()
                self.request.app._loop.create_task(conn.execute(CalendarFile.add_file(id, type)))
                async with async_open(path.join(self.ics_folder, f'{type}_{id}.ics'), 'wb') as file:
                    await file.write(calendar)
            else:
                async with async_open(path.join(self.ics_folder, f'{type}_{id}.ics'), 'rb') as file:
                    calendar = await file.read()
                    await conn.execute(CalendarFile.use(id, type))
            return Response(body=calendar, content_type='text/calendar', charset='utf-8')
