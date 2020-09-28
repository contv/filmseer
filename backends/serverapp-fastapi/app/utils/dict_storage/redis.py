import json
import re
from asyncio import TimeoutError as AioTimeoutError
from typing import Any, Callable, Dict, Optional, Tuple, Union

import aioredis

from app.utils.unique_id import id, to_base32

from ..dict_storage import DictStorageDriverBase


class RedisDictStorageDriver(DictStorageDriverBase):
    key_prefix: str
    key_filter: Callable[[str], str]
    key_filter_regex: str = ""
    initialized: bool = False
    ttl: int
    renew_on_ttl: int
    redis_uri: str
    redis: aioredis.Redis
    redis_pool_min: int
    redis_pool_max: int

    def __init__(
        self,
        key_prefix: str = "",
        key_filter: Optional[Union[str, Callable[[str], str]]] = r"[^a-zA-Z0-9-_]+",
        ttl: int = 0,
        renew_on_ttl: int = 0,
        redis_uri: str = "",
        redis_pool_min: int = 1,
        redis_pool_max: int = 20,
    ) -> None:
        self.key_prefix = key_prefix
        self.ttl = ttl
        self.renew_on_ttl = renew_on_ttl
        self.redis_uri = redis_uri
        self.redis_pool_min = redis_pool_min
        self.redis_pool_max = redis_pool_max
        if isinstance(key_filter, str):
            self.key_filter_regex = re.compile(key_filter)
            self.key_filter = lambda x: self.key_filter_regex.sub(x, "")
        elif callable(key_filter):
            self.key_filter = key_filter
        elif key_filter is None:
            self.key_filter = lambda x: x

    async def set_key_prefix(self, new_key_prefix: str = "") -> None:
        self.key_prefix = new_key_prefix

    async def initialize_driver(self) -> None:
        # The driver must be initialized first.
        self.redis = await aioredis.create_redis_pool(
            self.redis_uri, minsize=self.redis_pool_min, maxsize=self.redis_pool_max
        )
        self.initialized = True

    async def create(self) -> str:
        new_id = to_base32(id())
        # Lazy approach: we don't create it here but in update
        return new_id.upper()

    async def get(self, key: str) -> Tuple[Dict[str, Any], int]:
        # [Note]: This action is not atomic, consider replacing with eval(Lua script).
        full_key = self.key_prefix + self.key_filter(key.strip().upper())
        ttl = 0
        try:
            result_s = await self.redis.get(full_key, encoding="utf-8")
            if not result_s:
                raise LookupError
            result = json.loads(result_s)
            if not isinstance(result, dict):
                raise TypeError
            if not result:
                raise ValueError
            if self.ttl:
                ttl = await self.redis.ttl(full_key)
                if -1 <= ttl <= self.renew_on_ttl:
                    await self.redis.expire(full_key, self.renew_on_ttl)
                ttl = max(0, ttl)
            else:
                ttl = 0
        except (
            LookupError,
            UnicodeError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
            AioTimeoutError,
        ) as error:
            if not isinstance(error, LookupError):
                await self.redis.unlink(full_key)
            result = {}
        return result, ttl

    async def update(self, key: str, value: Dict[str, Any]) -> None:
        full_key = self.key_prefix + self.key_filter(key.strip().upper())
        await self.redis.set(
            full_key,
            json.dumps(value),
            expire=self.ttl,
        )

    async def destroy(self, key: str) -> None:
        full_key = self.key_prefix + self.key_filter(key.strip().upper())
        await self.redis.unlink(full_key)

    async def terminate_driver(self) -> None:
        # The driver must be terminated correctly in the end.
        self.redis.close()
        await self.redis.wait_closed()
        self.initialized = False
