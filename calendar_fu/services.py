import logging

import aioredis
from aiohttp.web import Application, view
from aiomisc.service.aiohttp import AIOHTTPService

from calendar_fu.cache import RedisCache, FileCache, NoCache
from calendar_fu.handlers import CalendarView

log = logging.getLogger(__name__)


class CalendarService(AIOHTTPService):
    cache_type: str
    cache_files_folder: str
    redis_url: str

    async def create_application(self) -> Application:
        app = Application()
        if self.cache_type == "redis":
            app["cache"] = RedisCache(await aioredis.create_redis(self.redis_url))
        elif self.cache_type == "file":
            app["cache"] = FileCache(self.cache_files_folder)
        else:
            app["cache"] = NoCache()
        app.add_routes(
            [
                view(
                    r"/calendar/{type:(group|lecturer)}/{id:\d+}{f:(.ics)?}",
                    CalendarView,
                ),
            ]
        )

        return app
