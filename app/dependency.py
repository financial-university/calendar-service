from typing import AsyncContextManager, Callable

from aiomysql.sa import create_engine, SAConnection
from aiomisc_dependency import dependency

connection = Callable[[], AsyncContextManager[SAConnection]]


def config_dependency(config):
    @dependency
    async def db_write() -> connection:
        engine = await create_engine(
            host=config['db_host'], user=config['db_user'], password=config['db_pass'],
            db=config['db_database'], port=config['db_port'], autocommit=True,
            connect_timeout=config['db_connect_timeout']
        )
        yield engine.acquire
        engine.close()
        await engine.wait_closed()

    @dependency
    async def ics_folder() -> str:
        yield config['ics_folder']
