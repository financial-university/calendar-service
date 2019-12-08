from datetime import datetime
from functools import lru_cache

from aiohttp import ClientSession
from aiohttp.web import View
from aiohttp.web_response import Response


@lru_cache()
def get_dates():
    now = datetime.now()
    format = '%Y.%m.%d'
    if now.month < 8:
        return datetime(now.year, 1, 15).strftime(format), datetime(now.year, 6, 31).strftime(format)
    else:
        return datetime(now.year, 8, 15).strftime(format), datetime(now.year + 1, 1, 31).strftime(format)


class CalendarView(View):
    async def get(self):
        type = self.request.match_info['type']
        id = self.request.match_info['id']
        date_start, date_end = get_dates()
        async with ClientSession() as client:
            async with client.get(
                    f'http://ruz.fa.ru/api/schedule/{type}/{id}.ics?start={date_start}&finish={date_end}&lng=1') as rasp:
                status = rasp.status
                text = await rasp.text(encoding='utf-8')
        return Response(text=text, content_type=rasp.content_type, status=status)
