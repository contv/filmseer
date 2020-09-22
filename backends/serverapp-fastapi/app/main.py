import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1.routers import router as api_router
from app.core.config import settings
from app.core.error_pages import handle_error_pages
from app.core.static_router import handle_static_routes

logging.config.fileConfig(
    Path(__file__).resolve().parent.parent / "logging.conf",
    disable_existing_loggers=False,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=settings.API_URL_PATH + "openapi.json"
)

if settings.FORCE_HTTPS:
    app.add_middleware(
        HTTPSRedirectMiddleware,
    )
    logger.info("HTTPSRedirectMiddleware loaded")

if settings.ALLOWED_HOSTS:
    if settings.ALLOWED_HOSTS == ["*"]:
        logger.warn('It is unsafe to set ALLOWED_HOSTS to "*"')
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    logger.info("TrustedHostMiddleware loaded")
else:
    logger.warn("No ALLOWED_HOSTS configuration has been found")

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=settings.CORS_CREDENTIALS
        if settings.CORS_ORIGINS != ["*"]
        else False,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    logger.info("CORSMiddleware loaded")

if settings.GZIP_ENABLED:
    app.add_middleware(
        GZipMiddleware,
        minimum_size=settings.GZIP_MIN_SIZE,
    )
    logger.info("GZipMiddleware loaded")

app = handle_error_pages(app)
app = handle_static_routes(app)

app.include_router(api_router, prefix=settings.API_URL_PATH)
