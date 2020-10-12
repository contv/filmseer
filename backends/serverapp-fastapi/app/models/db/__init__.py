import importlib
import pkgutil
from types import ModuleType
from typing import Dict

from tortoise.models import Model


def _import_submodules(package: str, recursive: bool = True) -> Dict[str, ModuleType]:
    """
    Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(_import_submodules(full_name))
    return results


def _get_models(submodules: Dict[str, ModuleType]) -> Dict[str, Model]:
    models = {}
    for module in submodules.values():
        model_names = dir(module)
        if "__all__" in model_names:
            model_names = getattr(module, "__all__")
        for model_name in model_names:
            model = getattr(module, model_name)
            if issubclass(model, Model):
                models[model_name] = getattr(module, model_name)
    return models


_models = _get_models(_import_submodules(__name__))

globals().update(_models)

__all__ = list(_models.keys())
