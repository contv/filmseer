import importlib
import pkgutil
from types import ModuleType
from typing import Dict

from fastapi import APIRouter

__all__ = ["router"]


def import_submodules(package: str, recursive: bool = True):
    """Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package: ModuleType = importlib.import_module(package)
    results: Dict[str, ModuleType] = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name: str = package.__name__ + "." + name
        submodule: ModuleType = importlib.import_module(full_name)

        # Build URL Path
        url_path: str = ""
        if (
            hasattr(submodule, "override_prefix_all")
            and submodule.override_prefix_all is not None
        ):
            url_path = submodule.override_prefix_all
        elif (
            hasattr(submodule, "override_prefix")
            and submodule.override_prefix is not None
        ):
            url_path = "/".join(package.__name__.split(".")) + str(
                submodule.override_prefix
            )
        else:
            url_path = "/".join(full_name.split("."))
        url_path = "/" + url_path.replace("/".join(__name__.split(".")), "").lstrip("/")

        if hasattr(submodule, "router"):
            results[url_path] = submodule

        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


routes = import_submodules(__name__)
print(list(routes.keys()))

router = APIRouter()

for url_path, submodule in routes.items():
    router.include_router(
        submodule.router, prefix=url_path.rstrip("/"), tags=url_path.strip("/").split("/")
    )
