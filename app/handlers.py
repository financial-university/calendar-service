import logging
from datetime import datetime, timedelta
from os import path, stat

from aiomisc.io import async_open
from aiohttp.web import View, HTTPNotFound
from aiohttp.web_response import Response

from app.calendar_creator import download_calendar, EmptySchedule

log = logging.getLogger(__name__)


class BaseView(View):
    @property
    def ics_folder(self) -> str:
        return self.request.app["ics_folder"]


class CalendarView(BaseView):
    async def get(self):
        type = self.request.match_info['type']
        id = int(self.request.match_info['id'])
        file_path = path.join(self.ics_folder, f'{type}_{id}.ics')
        if path.exists(file_path) and \
                datetime.fromtimestamp(stat(file_path).st_atime) + timedelta(hours=4) > datetime.now():
            async with async_open(file_path, 'rb') as file:
                calendar = await file.read()
        else:
            try:
                calendar = await download_calendar(id, type)
            except EmptySchedule:
                raise HTTPNotFound()
            async with async_open(file_path, 'wb') as file:
                await file.write(calendar)
        return Response(body=calendar, content_type='text/calendar', charset='utf-8')
