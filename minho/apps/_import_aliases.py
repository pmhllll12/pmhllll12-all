"""`secom.*` import 를 `friday13th` 패키지에 매핑."""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.util
import sys
from pathlib import Path


def _map_secom_name(fullname: str) -> str | None:
    if fullname == "secom":
        return "friday13th"
    if fullname.startswith("secom.schemas"):
        return "friday13th.secom" + fullname[5:]
    if fullname.startswith("secom."):
        return "friday13th" + fullname[5:]
    return None


class _AliasLoader(importlib.abc.Loader):
    def __init__(self, target_name: str) -> None:
        self._target_name = target_name

    def create_module(self, spec):  # noqa: ANN001
        return None

    def exec_module(self, module) -> None:  # noqa: ANN001
        target = importlib.import_module(self._target_name)
        module.__dict__.update(target.__dict__)
        module.__package__ = getattr(target, "__package__", None)
        module.__path__ = getattr(target, "__path__", [])
        module.__spec__ = importlib.util.spec_from_loader(
            module.__name__,
            self,
            is_package=bool(getattr(target, "__path__", None)),
        )
        sys.modules[module.__name__] = module


class _SecomAliasFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path, target=None):  # noqa: ANN001
        mapped = _map_secom_name(fullname)
        if mapped is None:
            return None
        target_spec = importlib.util.find_spec(mapped)
        if target_spec is None:
            return None
        return importlib.util.spec_from_loader(
            fullname,
            _AliasLoader(mapped),
            is_package=target_spec.submodule_search_locations is not None,
        )


def install_secom_aliases() -> None:
    apps_root = Path(__file__).resolve().parent
    apps_entry = str(apps_root)
    if apps_entry not in sys.path:
        sys.path.insert(0, apps_entry)
    if not any(isinstance(f, _SecomAliasFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _SecomAliasFinder())
