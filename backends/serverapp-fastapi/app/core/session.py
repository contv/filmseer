import base64
import binascii
import hashlib
import os
import random
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Type, Union

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from fastapi import FastAPI, Response
from starlette.applications import Starlette
from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection
from starlette.routing import Router
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.utils.dict_storage import DictStorageDriverBase
from app.utils.dict_storage.redis import RedisDictStorageDriver


def _urandom(num_bytes: int):
    try:
        return os.urandom(num_bytes)
    except NotImplementedError:
        return random.getrandbits(num_bytes << 3).to_bytes(num_bytes, byteorder="big")


class _UncopyableDict(dict):
    def __copy__(self):
        raise NotImplementedError("This dictionary should not be copied.")

    def __deepcopy__(self):
        raise NotImplementedError("This dictionary should not be copied.")


class AdvancedSessionMiddleware:
    app: ASGIApp
    driver: DictStorageDriverBase
    initalized: bool
    separate_https: bool
    server_ttl: int
    key_prefix: str
    renew_on_ttl: int
    cookie_secret: Optional[str]
    cookie_name: str
    cookie_domain: str
    cookie_path: str
    cookie_same_site: str
    cookie_max_age: int

    def __init__(
        self,
        app: ASGIApp,
        driver: Union[
            Type[DictStorageDriverBase], DictStorageDriverBase
        ] = DictStorageDriverBase,
        driver_args: Optional[List[Any]] = None,
        driver_kwargs: Optional[Dict[str, Any]] = None,
        separate_https: bool = settings.SESSION_SEPARATE_HTTPS,
        ttl: int = settings.SESSION_TTL,
        key_prefix: str = settings.SESSION_STORAGE_KEY_PREFIX,
        renew_time: int = settings.SESSION_RENEW_TIME,
        cookie_secret: Optional[str] = settings.SESSION_COOKIE_SECRET,
        cookie_name: str = settings.SESSION_COOKIE_NAME,
        cookie_domain: str = settings.SESSION_COOKIE_DOMAIN,
        cookie_path: str = settings.SESSION_COOKIE_PATH,
        cookie_same_site: str = settings.SESSION_COOKIE_SAME_SITE,
    ) -> None:
        self.app = app
        self.separate_https = separate_https
        self.server_ttl = int(max(60, ttl + 20))
        self.key_prefix = key_prefix
        self.renew_on_ttl = self.server_ttl - renew_time
        self.cookie_secret = (
            hashlib.sha512(cookie_secret.encode("utf-8")).digest()[:16]
            if cookie_secret
            else None
        )
        self.cookie_name = cookie_name
        self.cookie_domain = cookie_domain
        self.cookie_path = cookie_path
        self.cookie_same_site = cookie_same_site
        self.cookie_max_age = ttl
        if issubclass(driver, DictStorageDriverBase):
            self.driver = driver(
                *(driver_args or []),
                **{
                    **{
                        "key_prefix": self.key_prefix,
                        "ttl": self.server_ttl,
                        "renew_on_ttl": self.renew_on_ttl,
                    },
                    **(driver_kwargs or {}),
                },
            )
        elif isinstance(driver, DictStorageDriverBase):
            self.driver = driver
        else:
            raise TypeError(
                "The session driver should be a class"
                " or a object of DictStorageDriverBase."
            )
        self.initalized = self.driver.initialized

        async def terminate_driver():
            await self.driver.terminate_driver()

        if isinstance(app, (Router, Starlette)):
            app.add_event_handler(
                "shutdown",
                terminate_driver,
            )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return
        connection = HTTPConnection(scope)
        session_id: Optional[str] = (
            connection.cookies.get(settings.SESSION_COOKIE_NAME) or None
        )
        session: _UncopyableDict[str, Any] = {}
        ttl: int = 0
        if session_id and self.cookie_secret is not None:
            # Decrypt session_id
            try:
                blob = base64.b64decode(session_id, validate=True)
                iv = blob[:16]
                if len(iv) < 16:
                    raise IndexError
                crypted = blob[16:]
                if len(crypted) <= 0:
                    raise IndexError
                decryptor = Cipher(
                    algorithms.AES(self.cookie_secret), modes.CBC(iv)
                ).decryptor()
                session_id = bytes(
                    decryptor.update(crypted) + decryptor.finalize()
                ).decode("utf-8")
            except (binascii.Error, IndexError, UnicodeError):
                session_id = None
        elif session_id and len(session_id) != 26:
            session_id = None
        if not self.initalized:
            await self.driver.initialize_driver()
        if self.separate_https:
            await self.driver.set_key_prefix(self.key_prefix + scope["scheme"] + "-")
        if session_id:
            session, ttl = await self.driver.get(session_id)
            if not session:
                session_id = None
        session = _UncopyableDict(session)
        scope["session"] = session

        async def send_wrapper(message: Message):
            if message["type"] in ("http.response.start", "websocket.accept"):
                # Unfortunately, `headers` for `websocket.accept` in ASGI 2.1 and above
                # is not implemented in any ASGI servers and Starlette's `.accept()`.

                if scope["session"] is not session:
                    # [WARNING]: this is not a safe protection,
                    # you should NEVER make a copy of `scope` or `scope['session']`.
                    raise RuntimeError("scope['session'] should not be re-assigned.")

                headers = MutableHeaders(scope=message)
                if scope["session"]:
                    if session_id is None:
                        # Initialize a new session cookie
                        session_id_new = await self.driver.create()
                        # Store the current session
                        await self.driver.update(session_id_new, scope["session"])
                        if self.cookie_secret is not None:
                            iv = _urandom(16)
                            encryptor = Cipher(
                                algorithms.AES(self.cookie_secret), modes.CBC(iv)
                            ).encryptor()
                            session_id_new = base64.b64encode(
                                bytes(
                                    iv
                                    + encryptor.update(session_id)
                                    + encryptor.finalize()
                                )
                            ).decode("utf-8")
                        dummy = SimpleNamespace()
                        dummy.raw_headers = []
                        Response.set_cookie(
                            dummy,
                            settings.SESSION_COOKIE_NAME,
                            session_id_new,
                            max_age=self.cookie_max_age,
                            expires=self.cookie_max_age,
                            path=self.cookie_path,
                            domain=self.cookie_domain,
                            httponly=True,
                            samesite=self.cookie_same_site,
                            secure=self.separate_https
                            and scope["scheme"] in ("https", "wss"),
                        )
                        del session_id_new
                        headers.append(
                            "Set-Cookie", dummy.raw_headers[0][1].decode("utf-8")
                        )
                        del dummy
                    else:
                        # Store the current session
                        await self.driver.update(session_id, scope["session"])
                        # Handle renew
                        if ttl <= self.renew_on_ttl:
                            dummy = SimpleNamespace()
                            dummy.raw_headers = []
                            Response.set_cookie(
                                dummy,
                                settings.SESSION_COOKIE_NAME,
                                connection.cookies.get(settings.SESSION_COOKIE_NAME),
                                max_age=self.cookie_max_age,
                                expires=self.cookie_max_age,
                                path=self.cookie_path,
                                domain=self.cookie_domain,
                                httponly=True,
                                samesite=self.cookie_same_site,
                                secure=self.separate_https
                                and scope["scheme"] in ("https", "wss"),
                            )
                            headers.append(
                                "Set-Cookie", dummy.raw_headers[0][1].decode("utf-8")
                            )
                            del dummy
                else:
                    if session_id is None:
                        if settings.SESSION_COOKIE_NAME in connection.cookies:
                            # Revoke this invalid session cookie
                            dummy = SimpleNamespace()
                            dummy.raw_headers = []
                            Response.set_cookie(
                                dummy,
                                settings.SESSION_COOKIE_NAME,
                                "",
                                max_age=0,
                                expires=0,
                                path=self.cookie_path,
                                domain=self.cookie_domain,
                                httponly=True,
                                samesite=self.cookie_same_site,
                                secure=self.separate_https
                                and scope["scheme"] in ("https", "wss"),
                            )
                            headers.append(
                                "Set-Cookie", dummy.raw_headers[0][1].decode("utf-8")
                            )
                            del dummy
                        else:
                            # No session cookie, and the session is empty: do nothing
                            pass
                    else:
                        # Delete the current session
                        await self.driver.destroy(session_id)
                        # Revoke this invalid session cookie
                        dummy = SimpleNamespace()
                        dummy.raw_headers = []
                        Response.set_cookie(
                            dummy,
                            settings.SESSION_COOKIE_NAME,
                            "",
                            max_age=0,
                            expires=0,
                            path=self.cookie_path,
                            domain=self.cookie_domain,
                            httponly=True,
                            samesite=self.cookie_same_site,
                            secure=self.separate_https
                            and scope["scheme"] in ("https", "wss"),
                        )
                        headers.append(
                            "Set-Cookie", dummy.raw_headers[0][1].decode("utf-8")
                        )
                        del dummy
            await send(message)

        await self.app(scope, receive, send_wrapper)


def handle_session(app: FastAPI) -> FastAPI:
    app.add_middleware(
        AdvancedSessionMiddleware,
        driver=RedisDictStorageDriver,
        driver_kwargs={
            "redis_uri": settings.REDIS_URI,
            "redis_pool_min": settings.REDIS_POOL_MIN,
            "redis_pool_max": settings.REDIS_POOL_MAX,
        },
    )

    return app
