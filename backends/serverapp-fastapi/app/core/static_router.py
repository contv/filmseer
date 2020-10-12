from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.routing import Match, Route
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings


class AdvancedStaticFilesMiddleware:
    app: ASGIApp
    exclude_routes: List[Route]
    spa_routes: List[Route]
    spa_app: Optional[ASGIApp]
    static_app: ASGIApp

    def __init__(
        self,
        app: ASGIApp,
        directory: str,
        packages: Optional[List[str]] = None,
        html: bool = False,
        check_dir: bool = True,
        exclude_paths: Optional[List[str]] = None,
        spa_paths: Optional[List[str]] = None,
        spa_entry_file: str = "",
    ) -> None:
        self.app = app
        self.exclude_routes: List[Route] = [
            Route(x, endpoint=lambda x: x, methods=None) for x in (exclude_paths or [])
        ]
        self.spa_routes: List[Route] = [
            Route(x, endpoint=lambda x: x, methods=None) for x in (spa_paths or [])
        ]

        if Path(spa_entry_file).is_file():

            async def spa_app(scope, receive, send):
                assert scope["type"] == "http"
                response = FileResponse(Path(spa_entry_file).resolve())
                await response(scope, receive, send)

            self.spa_app: ASGIApp = spa_app
        else:
            self.spa_app = None

        self.static_app = StaticFiles(
            directory=directory,
            packages=packages,
            html=html,
            check_dir=check_dir,
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        for route in self.exclude_routes:
            match, _ = route.matches(scope)
            if match != Match.NONE:
                await self.app(scope, receive, send)
                return
        for route in self.spa_routes:
            match, _ = route.matches(scope)
            if match != Match.NONE:
                await self.spa_app(scope, receive, send)
                return
        await self.static_app(scope, receive, send)
        return


def handle_static_routes(app: FastAPI) -> FastAPI:
    app.add_middleware(
        AdvancedStaticFilesMiddleware,
        directory=settings.STATIC_FILE_ROOT,
        html=True,
        check_dir=True,
        exclude_paths=[settings.API_URL_PATH + "{whatever:path}"],
        spa_paths=[
            "/search",
            "/movie/{whatever:path}",
            "/user",
            "/user/{whatever:path}",
            "/settings",
            "/settings/security",
            "/settings/reviews",
            "/settings/movies",
            "/settings/reports",
        ],
        spa_entry_file=settings.SPA_ENTRY_FILE,
    )

    return app
