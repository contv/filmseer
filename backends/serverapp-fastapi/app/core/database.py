import tortoise
from fastapi import FastAPI

from app.core.config import settings


def handle_database(app: FastAPI) -> FastAPI:
    @app.on_event("startup")
    async def init_session_driver():
        await tortoise.Tortoise.init(
            db_url=settings.DATABASE_URI, modules={"models": ["app.models.db"]}
        )

    @app.on_event("shutdown")
    async def terminate_session_driver():
        await tortoise.Tortoise.close_connections()

    return app


__all__ = ["handle_database"]
