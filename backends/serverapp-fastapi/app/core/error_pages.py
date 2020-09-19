from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse

from app.core.config import settings


def handle_error_pages(app: FastAPI) -> FastAPI:
    @app.middleware("http")
    async def custom_http_errors(request: Request, call_next):
        response: Response = await call_next(request)
        if 400 <= response.status_code < 600:
            error_page = (
                Path(settings.ERROR_PAGES_ROOT)
                / str(response.status_code)
                / "index.html"
            )
            if error_page.is_file():
                return FileResponse(error_page)
        return response

    return app
