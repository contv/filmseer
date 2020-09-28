from typing import Any, Callable, Dict, Optional, Tuple, Union


class DictStorageDriverBase:
    key_prefix: str
    key_filter: Callable[[str], str]
    key_filter_regex: str = ""
    initialized: bool = False
    ttl: int
    renew_on_ttl: int

    def __init__(
        self,
        key_prefix: str = "",
        key_filter: Optional[Union[str, Callable[[str], str]]] = r"[^a-zA-Z0-9_-]+",
        ttl: int = 0,
        renew_on_ttl: int = 0,
    ) -> None:
        self.key_prefix = key_prefix
        self.ttl = ttl
        self.renew_on_ttl = renew_on_ttl
        if isinstance(key_filter, str):
            self.key_filter_regex = re.compile(key_filter)
            self.key_filter = lambda x: self.key_filter_regex.sub("", x)
        elif callable(key_filter):
            self.key_filter = key_filter
        elif key_filter is None:
            self.key_filter = lambda x: x

    async def set_key_prefix(self, new_key_prefix: str = "") -> None:
        self.key_prefix = new_key_prefix

    async def initialize_driver(self) -> None:
        # The driver must be initialized first.
        self.initialized = True

    async def create(self) -> str:
        return ""

    async def get(self, key: str) -> Tuple[Dict[str, Any], int]:
        return {}, 0

    async def update(self, key: str, value: Dict[str, Any]) -> None:
        pass

    async def destroy(self, key: str) -> None:
        pass

    async def terminate_driver(self) -> None:
        # The driver must be terminated correctly in the end.
        self.initialized = False
