import logging
from asyncio import sleep
from os import path

import aioredis
from aiohttp import ClientSession
from aiohttp.web import Application, view
from aiomisc.io import async_open
from aiomisc.service.aiohttp import AIOHTTPService
from aiomisc.service.periodic import PeriodicService
import ujson

from app.cache import RedisCache, FileCache, NoCache
from app.handlers import CalendarView
from app.schemas import GroupsListSchema, LecturersListSchema

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


class RuzGrabber(PeriodicService):
    files_folder: str

    GROUPS_LIST = GroupsListSchema()
    LECTURERS_LIST = LecturersListSchema()

    @staticmethod
    async def get_from_api(client: ClientSession, type: str):
        groups = await client.get(f"https://ruz.fa.ru/api/dictionary/{type}")
        return await groups.json()

    async def callback(self):
        async with ClientSession() as client:
            groups = await self.get_from_api(client, "groups")
            if not groups:
                await sleep(1)
                groups = await self.get_from_api(client, "groups")
            groups = self.GROUPS_LIST.load(groups)
            async with async_open(
                path.join(self.files_folder, "groups.json"), "w"
            ) as file:
                await file.write(ujson.dumps(groups))

            lecturers = await self.get_from_api(client, "lecturers")
            if not lecturers:
                await sleep(1)
                lecturers = await self.get_from_api(client, "lecturers")
            lecturers = self.LECTURERS_LIST.load(lecturers)
            async with async_open(
                path.join(self.files_folder, "lecturers.json"), "w"
            ) as file:
                await file.write(ujson.dumps(lecturers))
            log.info("json files updated")
