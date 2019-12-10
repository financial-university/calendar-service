from aiohttp.web import Application
from aiomisc.service.aiohttp import AIOHTTPService

from app.handlers import CalendarView


class CalendarService(AIOHTTPService):
    __dependencies__ = ("db_write", "ics_folder")

    async def create_application(self) -> Application:
        app = Application()
        app["db_write"] = self.db_write
        app["ics_folder"] = self.ics_folder
        app.router.add_view(r"/calendar/{type:(group|lecturer)}/{id:\d+}", CalendarView)

        return app
