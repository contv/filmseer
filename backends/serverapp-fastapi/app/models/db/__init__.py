import importlib
import pkgutil


def import_submodules(package, recursive=True):
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
            results.update(import_submodules(full_name))
    return results


_submodules = import_submodules(__name__)

_models = {}
for module in _submodules.values():
    model_names = dir(module)
    for model_name in model_names:
        _models[model_name] = getattr(module, model_name)

globals().update(_models)

__all__ = list(_models.keys())
print("DB", __all__)
