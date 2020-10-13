from pathlib import Path
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, EmailStr, constr


class Settings(BaseSettings):
    # This can read environment variables from
    #  `/backends/serverapp-fastapi/.env`
    # Please create and change it to change config values.
    # There is a template called `.env.template` to get you started.
    # And please **DO NOT CHANGE ANYTHING HERE**.

    # Server Settings
    SERVER_INSTANCE_NAME: Optional[str] = None
    # Other settings will be handled by start.py

    # HTTPS Settings will be handled by start.py

    # General Settings
    PROJECT_NAME: str = "App"
    DEV_MODE: bool = True
    API_URL_PATH: str = "/api/v1"
    # Base URL should not be configured here,
    # it should be generated using the Request body.
    ALLOWED_HOSTS: List[str] = ["*"]
    GZIP_ENABLED: bool = True
    GZIP_MIN_SIZE: int = 500
    FORCE_HTTPS: bool = False
    STATIC_FILE_ROOT: str = str(
        (Path(__file__).resolve().parents[4] / "public").resolve()
    )
    ERROR_PAGES_ROOT: str = str(
        (Path(__file__).resolve().parents[4] / "error-pages").resolve()
    )
    SPA_ENTRY_FILE: str = str(
        (Path(__file__).resolve().parents[4] / "public" / "index.html").resolve()
    )

    # CORS Settings
    CORS_ORIGINS: List[Union[AnyHttpUrl, constr(regex=r"^\*$")]] = []  # noqa: F722
    CORS_ORIGIN_REGEX: str = ""
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # Password Hash Settings
    HASH_ITERATION: int = 2
    HASH_RAM_USAGE: int = 100 * 1024
    HASH_THREADS_PER_CORE: float = 0.8
    HASH_PRESERVE_CPU_CORE: int = 1
    HASH_LENGTH: int = 16
    HASH_SALT_LENGTH: int = 16
    HASH_TYPE: str = ("argon2id", "argon2i", "argon2d")[0]

    # Session Settings
    SESSION_SEPARATE_HTTPS: bool = True
    SESSION_TTL: int = 1800
    SESSION_STORAGE_KEY_PREFIX: str = "session:"
    SESSION_RENEW_TIME: int = 0
    SESSION_COOKIE_SECRET: Optional[str] = None
    SESSION_COOKIE_NAME: str = "app_session"
    SESSION_COOKIE_DOMAIN: str = ""
    SESSION_COOKIE_PATH: str = "/"
    SESSION_COOKIE_MAX_AGE: int = 0
    SESSION_COOKIE_SAME_SITE: str = ("strict", "lax", "none")[1]

    # Cookie Default Settings
    COOKIE_DEFAULT_SEPARATE_HTTPS: bool = True
    COOKIE_DEFAULT_PREFIX: str = ""
    COOKIE_DEFAULT_DOMAIN: str = ""
    COOKIE_DEFAULT_PATH: str = "/"
    COOKIE_DEFAULT_MAX_AGE: int = 1800
    COOKIE_DEFAULT_SAME_SITE: str = ("strict", "lax", "none")[1]
    COOKIE_DEFAULT_HTTP_ONLY: bool = False

    # Database Settings
    DATABASE_URI: AnyUrl
    REDIS_URI: AnyUrl
    REDIS_POOL_MIN: int = 1
    REDIS_POOL_MAX: int = 20
    ELASTICSEARCH_URI: AnyUrl

    # Email Settings
    EMAIL_ENABLED: bool = False

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM_ADDRESS: Optional[EmailStr] = None
    EMAIL_FROM_NAME: Optional[str] = None

    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_TEMPLATES_DIR: str = str(
        (Path(__file__).resolve().parents[2] / "templates" / "emails").resolve()
    )
    EMAIL_TEST_USER: EmailStr = "test@example.com"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

__all__ = ["settings"]
