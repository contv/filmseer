from typing import Any, Dict, Tuple


class DictStorageDriverBase:
    key_prefix: str
    ttl: int
    renew_on_ttl: int

    def __init__(
        self, key_prefix: str = "", ttl: int = 0, renew_on_ttl: int = 0
    ) -> None:
        self.key_prefix = key_prefix
        self.ttl = ttl
        self.renew_on_ttl = renew_on_ttl

    async def set_key_prefix(self, new_key_prefix: str = "") -> None:
        self.key_prefix = new_key_prefix

    async def initialize_driver(self) -> None:
        pass

    async def create(self) -> str:
        return ""

    async def get(self, key: str) -> Tuple[Dict[str, Any], int]:
        return {}, 0

    async def update(self, key: str, value: Dict[str, Any]) -> None:
        pass

    async def destroy(self, key: str) -> None:
        pass

    async def terminate_driver(self) -> None:
        pass
