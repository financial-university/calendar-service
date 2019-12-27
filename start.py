from os import getenv, getcwd, path

from aiomisc import entrypoint

from app.services import CalendarService, RuzGrabber

config = dict(
    ics_folder=path.join(getcwd(), 'ics_folder'),
    files_folder=getenv('API_FILES_FOLDER') or r'c:\\1\\api'
)

if __name__ == '__main__':
    with entrypoint(
            CalendarService(address='localhost', port=4040, ics_folder=config['ics_folder']),
            RuzGrabber(interval=60 * 60 * 24, files_folder=config['files_folder']),
    ) as loop:
        loop.run_forever()
