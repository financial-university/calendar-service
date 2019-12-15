from os import getenv, getcwd, path

from aiomisc import entrypoint

from app.dependency import config_dependency
from app.services import CalendarService, CalendarUpdater, RuzGrabber

config = dict(
    db_host=getenv('DB_HOST') or 'localhost',
    db_port=int(getenv('DB_PORT') or '3306'),
    db_user=getenv('DB_USER') or 'root',
    db_pass=getenv('DB_PASS') or 'password',
    db_database=getenv('DB_DATABASE') or 'db',
    db_connect_timeout=int(getenv('DB_TIMEOUT') or '18000'),
    ics_folder=path.join(getcwd(), 'ics_folder'),
    files_folder=getenv('API_FILES_FOLDER') or r'c:\\1\\api'
)

if __name__ == '__main__':
    config_dependency(config)
    with entrypoint(
            CalendarService(address='localhost', port=4040, ics_folder=config['ics_folder']),
            CalendarUpdater(interval=60 * 60 * 4, ics_folder=config['ics_folder']),
            RuzGrabber(interval=60 * 60 * 24, files_folder=config['files_folder'])
    ) as loop:
        loop.run_forever()
