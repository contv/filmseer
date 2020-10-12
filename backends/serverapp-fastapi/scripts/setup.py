# setup.py
# This is a set up script that is used to test connection and libraries,
# create database tables and so on.
# It should provide an interactive way, and a silent way.
import asyncio
import sys

import tortoise

from app.core.config import settings


async def init_database():
    pass


def interactive():
    print("ERROR: Only the silent mode has been implemented now.")
    sys.exit(1)


def silent():
    pass
