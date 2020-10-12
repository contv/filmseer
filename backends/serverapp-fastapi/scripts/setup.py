# setup.py
# This is a set up script that is used to test connection and libraries,
# create database tables and so on.
# It should provide an interactive way, and a silent way.
import sys

import tortoise

from app.core.config import settings


async def init_database():
    await tortoise.Tortoise.init(
        db_url=settings.DATABASE_URI, modules={"models": ["app.models.db"]}
    )
    await tortoise.Tortoise.generate_schemas()


def interactive():
    print("ERROR: Only the silent mode has been implemented now.")
    sys.exit(1)


def silent():
    tortoise.run_async(init_database())
