from aiomysql.sa import create_engine
from aiomysql.sa.engine import Engine
from aiomisc_dependency import dependency


def config_dependency(config):
    @dependency
    async def db_write() -> Engine:
        engine = await create_engine(
            host=config['db_host'], user=config['db_user'], password=config['db_pass'],
            db=config['db_database'], port=config['db_port'], autocommit=True,
            connect_timeout=config['db_connect_timeout']
        )
        # TODO Возможно тут косяк
        async with engine.acquire() as conn:
            yield conn
        engine.close()

    @dependency
    async def ics_folder() -> str:
        yield config['ics_folder']
