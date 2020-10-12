from typing import Dict, Optional

import tldextract
from starlette.datastructures import Headers
from starlette.types import Scope

from app.core.config import settings


def get_cookie_kwargs(scope: Optional[Scope] = None, url: str = None) -> Dict[str, str]:
    kwargs = {
        "max_age": settings.COOKIE_DEFAULT_MAX_AGE,
        "expires": settings.COOKIE_DEFAULT_MAX_AGE,
        "path": settings.COOKIE_DEFAULT_PATH,
        "httponly": settings.COOKIE_DEFAULT_HTTP_ONLY,
        "samesite": settings.COOKIE_DEFAULT_SAME_SITE,
    }
    if settings.COOKIE_DEFAULT_SEPARATE_HTTPS:
        kwargs["secure"] = False
        if scope and scope["scheme"] in ("https", "wss"):
            kwargs["secure"] = True
        elif url:
            clean_url = url.lstrip().lower()
            if clean_url.startswith("https://") or clean_url.startswith("wss://"):
                kwargs["secure"] = True
    if settings.COOKIE_DEFAULT_DOMAIN != "auto":
        kwargs["domain"] = settings.COOKIE_DEFAULT_DOMAIN
    else:
        if scope:
            kwargs["domain"] = ".".join(
                [
                    x
                    for x in tldextract.extract(
                        Headers(scope=scope).get("host", "").split(":")[0]
                    )[1:]
                    if x
                ]
            ).lower()
        elif url:
            kwargs["domain"] = ".".join(
                [x for x in tldextract.extract(url)[1:] if x]
            ).lower()
        else:
            kwargs["domain"] = ""
    return kwargs


__all__ = ["get_cookie_kwargs"]
