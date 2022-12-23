import importlib
import importlib.machinery
import importlib.util
import logging
import os
import sys
from functools import lru_cache
from inspect import isclass
from typing import List, Optional, Type

from duty_board.exceptions import PluginLoadingException
from duty_board.plugin.abstract_plugin import AbstractPlugin
from duty_board.plugin.example.example_plugin import ExamplePlugin

logger = logging.getLogger(__name__)


def get_plugin() -> AbstractPlugin:
    loaded_plugin = _get_plugin()
    if loaded_plugin is None:
        logger.warning("Loading the ExamplePlugin as you did not specify a Plugin. This is probably not what you want!")
        return ExamplePlugin()
    return loaded_plugin


@lru_cache
def _get_plugin() -> Optional[AbstractPlugin]:
    if "DUTY_BOARD_PLUGIN_LOCATION" not in os.environ:
        return None

    file_path = os.environ["DUTY_BOARD_PLUGIN_LOCATION"]

    if not os.path.isfile(file_path):
        raise PluginLoadingException(f"{file_path=} is not a file. Please set the plugin location correctly.")
    mod_name, file_ext = os.path.splitext(os.path.split(file_path)[-1])
    if file_ext != ".py":
        raise PluginLoadingException(f"{file_path=} must be a Python file. Please set the plugin correctly.")
    try:
        loader = importlib.machinery.SourceFileLoader(mod_name, file_path)
        spec = importlib.util.spec_from_loader(mod_name, loader)  # type: ignore
        if spec is None:
            raise PluginLoadingException(f"Unable to import {mod_name}.")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        loader.exec_module(mod)
        logger.info("Importing plugin module %s", file_path)
        list_with_plugins: List[Type[AbstractPlugin]] = [
            m for m in mod.__dict__.values() if isclass(m) and issubclass(m, AbstractPlugin) and m != AbstractPlugin
        ]
        if not any(list_with_plugins):
            raise PluginLoadingException(f"{file_path} does not contain any classes that implement the AbstractPlugin.")
        if len(list_with_plugins) > 1:
            raise PluginLoadingException(f"{file_path} contains multiple AbstractPlugin implementations.")
        your_plugin = list_with_plugins[0]
        return your_plugin()
    except PluginLoadingException:
        raise
    except Exception as e:
        logger.exception("Failed to import plugin %s", file_path)
        raise PluginLoadingException(f"Unable to import plugin {file_path}") from e
