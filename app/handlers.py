from datetime import datetime
from functools import lru_cache
from os import path

from aiomisc.io import async_open
from aiohttp import ClientSession
from aiohttp.web import View, HTTPNotFound
from aiohttp.web_response import Response
from aiomysql.sa import Engine

from app.calendar_creator import create_calendar
from app.models import CalendarFile


class EmptySchedule(Exception):
    pass


@lru_cache()
def get_dates():
    now = datetime.now()
    format = '%Y.%m.%d'
    if now.month < 8:
        return datetime(now.year, 1, 15).strftime(format), datetime(now.year, 6, 31).strftime(format)
    else:
        return datetime(now.year, 8, 15).strftime(format), datetime(now.year + 1, 1, 31).strftime(format)


class BaseView(View):
    @property
    def db(self) -> Engine:
        return self.request.app["db_write"]

    @property
    def ics_folder(self) -> str:
        return self.request.app["ics_folder"]


class CalendarView(BaseView):
    async def get(self):
        type = self.request.match_info['type']
        id = self.request.match_info['id']
        result = await self.db.execute(CalendarFile.find_file(id))
        if not result.rowcount:
            try:
                calendar = await self.download_calendar(id, type)
            except EmptySchedule:
                raise HTTPNotFound()
            await self.db.execute(CalendarFile.add_file(id))
            async with async_open(path.join(self.ics_folder, f'{id}.ics'), 'wb') as file:
                await file.write(calendar)
        else:
            async with async_open(path.join(self.ics_folder, f'{id}.ics'), 'rb') as file:
                calendar = await file.read()
                await self.db.execute(CalendarFile.use(id))
        return Response(body=calendar, content_type='text/calendar', charset='utf-8')

    @staticmethod
    async def download_calendar(id: int, type: str):
        date_start, date_end = get_dates()
        async with ClientSession() as client:
            async with client.get(
                    f'http://ruz.fa.ru/api/schedule/{type}/{id}?start={date_start}&finish={date_end}&lng=1') as request:
                pairs_list = await request.json()
                if not pairs_list:
                    raise EmptySchedule()
        return create_calendar(pairs_list)
