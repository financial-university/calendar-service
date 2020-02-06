import logging
from datetime import datetime, timedelta
from os import path, stat

from aiomisc.io import async_open
from aiohttp.web import View, HTTPNotFound, HTTPServiceUnavailable
from aiohttp.web_response import Response
from multidict import MultiDict

from app.calendar_creator import download_calendar, EmptySchedule, ServiceUnavailable

log = logging.getLogger(__name__)


class BaseView(View):
    @property
    def ics_folder(self) -> str:
        return self.request.app["ics_folder"]


def params_handler(query: MultiDict):
    try:
        params = {k: v.replace(";", ",").split(",") for k, v in query.items()}
        params_string = "&".join(
            f"{k}={','.join(sorted(set(v)))}" for k, v in params.items()
        )
    except Exception:
        params = {}
        params_string = ""
    return params_string, params


class CalendarView(BaseView):
    async def get(self):
        type = self.request.match_info["type"]
        id = int(self.request.match_info["id"])
        params_string, params = params_handler(self.request.rel_url.query)
        if params_string:
            params_string = "_" + params_string

        file_path = path.join(self.ics_folder, f"{type}_{id}{params_string}.ics")
        if (
            path.exists(file_path)
            and datetime.fromtimestamp(stat(file_path).st_atime) + timedelta(hours=4)
            > datetime.now()
        ):
            async with async_open(file_path, "rb") as file:
                calendar = await file.read()
        else:
            try:
                calendar = await download_calendar(id, type, params)
                async with async_open(file_path, "wb") as file:
                    await file.write(calendar)
            except EmptySchedule:
                raise HTTPNotFound()
            except ServiceUnavailable:
                log.warning("Server was unavailable for %s %s", type, id)
                if path.exists(file_path):
                    async with async_open(file_path, "rb") as file:
                        calendar = await file.read()
                else:
                    raise HTTPServiceUnavailable()
        return Response(body=calendar, content_type="text/calendar", charset="utf-8")
