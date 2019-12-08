from aiohttp.web import Application
from aiomisc.service.aiohttp import AIOHTTPService

from app.handlers import CalendarView


class CalendarService(AIOHTTPService):
    async def create_application(self) -> Application:
        app = Application()
        app.router.add_view("/calendar/{type}/{id}", CalendarView)

        return app
