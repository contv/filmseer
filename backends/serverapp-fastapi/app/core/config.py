from pathlib import Path
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, constr


class Settings(BaseSettings):
    # This can read environment variables from
    #  `/backends/serverapp-fastapi/.env`
    # Please create and change it to change config values.
    # There is a template called `.env.template` to get you started.
    # And please **DO NOT CHANGE ANYTHING HERE**.

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

    # CORS Settings
    CORS_ORIGINS: List[Union[AnyHttpUrl, constr(regex=r"^\*$")]] = []  # noqa: F722
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # Database Settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

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
    EMAIL_TEMPLATES_DIR: str = "/app/email-templates"
    EMAIL_TEST_USER: EmailStr = "test@example.com"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
