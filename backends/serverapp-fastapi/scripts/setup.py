# setup.py
# This is a set up script that is used to test connection and libraries,
# create database tables and so on.
import tortoise

from app.core.config import settings


async def init_database(drop_all: bool = False, if_not_exists: bool = True):
    await tortoise.Tortoise.init(
        db_url=settings.DATABASE_URI, modules={"models": ["app.models.db"]}
    )
    if drop_all:
        conn = tortoise.Tortoise.get_connection("default")
        command_items = await conn.execute_query_dict(
            "SELECT 'DROP TABLE IF EXISTS "
            "\"' || tablename || '\""
            " CASCADE;' AS cmd FROM pg_tables WHERE schemaname = current_schema();"
        )
        for command_item in command_items:
            await conn.execute_query(command_item["cmd"])
    await tortoise.Tortoise.generate_schemas(safe=if_not_exists)
    await tortoise.Tortoise.close_connections()


def setup_clean():
    tortoise.run_async(init_database(drop_all=True, if_not_exists=True))


def setup_noclean():
    tortoise.run_async(init_database(drop_all=False, if_not_exists=True))


def setup_nodrop():
    tortoise.run_async(init_database(drop_all=False, if_not_exists=False))
