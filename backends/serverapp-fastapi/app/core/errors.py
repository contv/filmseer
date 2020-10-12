import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import FileResponse, JSONResponse
from starlette.types import Receive, Scope, Send

from app.core.config import settings
from app.utils.wrapper import ApiException, wrap

_status_codes_to_handle: List[int] = []


async def status_code_handler(
    response: Response, scope: Scope, receive: Receive, send: Send
) -> None:
    if (
        hasattr(response, "status_code")
        and int(response.status_code) in _status_codes_to_handle
    ):
        await FileResponse(
            Path(settings.ERROR_PAGES_ROOT) / str(response.status_code) / "index.html"
        )(scope, receive, send)
        return
    await response(scope, receive, send)


def handle_errors(app: FastAPI) -> FastAPI:
    global _status_codes_to_handle
    _status_codes_to_handle = [
        int(d)
        for d in os.listdir(Path(settings.ERROR_PAGES_ROOT))
        if os.path.isfile(
            os.path.join(Path(settings.ERROR_PAGES_ROOT) / d / "index.html")
        )
        and d.isdigit()
    ]

    @app.exception_handler(ApiException)
    async def api_exception_handler(request: Request, exc: ApiException) -> Response:
        return JSONResponse(
            headers={"X-Exception-Handled": "True"},
            status_code=ApiException.status,
            content=jsonable_encoder(wrap(error=exc)),
        )

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(
        request: Request, exc: HTTPException
    ) -> Response:
        if int(exc.status_code) in _status_codes_to_handle:
            return FileResponse(
                (Path(settings.ERROR_PAGES_ROOT) / str(exc.status_code) / "index.html"),
                status_code=exc.status_code,
                headers={"X-Exception-Handled": "True"},
            )
        return http_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def internal_error_exception_handler(
        request: Request, exc: Exception
    ) -> Response:
        if 500 in _status_codes_to_handle:
            return FileResponse(
                (Path(settings.ERROR_PAGES_ROOT) / str(500) / "index.html"),
                status_code=500,
                headers={"X-Exception-Handled": "True"},
            )
        raise exc

    @app.middleware("http")
    async def http_error_pages_middleware(request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        if (
            hasattr(response, "status_code")
            and int(response.status_code) in _status_codes_to_handle
            and (
                not hasattr(response, "headers")
                or "X-Exception-Handled" not in response.headers
            )
        ):
            error_page = (
                Path(settings.ERROR_PAGES_ROOT)
                / str(response.status_code)
                / "index.html"
            )
            return FileResponse(error_page)
        if hasattr(response, "headers"):
            del response.headers["X-Exception-Handled"]
        return response

    return app


__all__ = ["handle_errors", "status_code_handler"]
