from aiomisc import entrypoint

from app.services import CalendarService

if __name__ == '__main__':
    with entrypoint(
            CalendarService(address='localhost', port=4040)
    ) as loop:
        loop.run_forever()
