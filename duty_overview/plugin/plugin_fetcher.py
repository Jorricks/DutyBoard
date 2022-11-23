import importlib
import importlib.machinery
import importlib.util
import logging
import os
import sys
from functools import lru_cache
from typing import List, Optional

from duty_overview.plugin.abstract_plugin import AbstractPlugin
from duty_overview.plugin.standard_plugin import StandardPlugin

logger = logging.getLogger(__file__)


def get_plugin() -> AbstractPlugin:
    return _get_plugin() or StandardPlugin()


@lru_cache
def _get_plugin() -> Optional[AbstractPlugin]:
    if "DUTY_OVERVIEW_PLUGIN_LOCATION" not in os.environ:
        return None

    file_path = os.environ["DUTY_OVERVIEW_PLUGIN_LOCATION"]

    if not os.path.isfile(file_path):
        return None
    mod_name, file_ext = os.path.splitext(os.path.split(file_path)[-1])
    if file_ext != ".py":
        return None
    try:
        loader = importlib.machinery.SourceFileLoader(mod_name, file_path)
        spec = importlib.util.spec_from_loader(mod_name, loader)  # type: ignore
        if spec is None:
            raise ImportError(f"Unable to import {mod_name}.")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        loader.exec_module(mod)
        logger.debug("Importing plugin module %s", file_path)
        list_with_plugins: List[AbstractPlugin] = [m for m in mod.__dict__.values() if isinstance(m, AbstractPlugin)]
        return list_with_plugins[0] if any(list_with_plugins) else None
    except Exception as e:
        logger.exception("Failed to import plugin %s", file_path)
        raise ValueError(f"Unable to import plugin {file_path}") from e
