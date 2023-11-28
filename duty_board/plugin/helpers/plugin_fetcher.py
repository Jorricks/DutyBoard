import importlib
import importlib.machinery
import importlib.util
import logging
import os
import sys
from functools import lru_cache
from inspect import isclass
from pathlib import Path
from typing import List, Optional, Type

from duty_board.exceptions import PluginLoadingError
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

    file_path = Path(os.environ["DUTY_BOARD_PLUGIN_LOCATION"]).resolve()

    if not file_path.is_file():
        raise PluginLoadingError(f"{file_path=} is not a file. Please set the plugin location correctly.")
    if file_path.suffix != ".py":
        raise PluginLoadingError(f"{file_path=} must be a Python file. Please set the plugin correctly.")
    try:
        loader = importlib.machinery.SourceFileLoader(file_path.stem, str(file_path))
        spec = importlib.util.spec_from_loader(file_path.stem, loader)
        if spec is None:
            raise PluginLoadingError(f"Unable to import {file_path.stem}.")  # noqa: TRY301
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        loader.exec_module(mod)
        logger.info("Importing plugin module %s", file_path)
        list_with_plugins: List[Type[AbstractPlugin]] = [
            m for m in mod.__dict__.values() if isclass(m) and issubclass(m, AbstractPlugin) and m != AbstractPlugin
        ]
        if len(list_with_plugins) > 1:
            if (plugin_class_name := os.environ.get("DUTY_BOARD_PLUGIN_CLASS_NAME", None)) is not None:
                logger.info(f"Originally had {list_with_plugins=} but now filtering on {plugin_class_name=}.")
                list_with_plugins = [plugin for plugin in list_with_plugins if plugin.__name__ == plugin_class_name]
                logger.info(f"Left over with {list_with_plugins=}.")
            else:
                raise PluginLoadingError(f"{file_path} contains multiple AbstractPlugin implementations.")  # noqa: TRY301
        if not any(list_with_plugins):
            raise PluginLoadingError(f"{file_path} does not contain any classes that implement the AbstractPlugin.")  # noqa: TRY301
        your_plugin = list_with_plugins[0]
        return your_plugin()
    except PluginLoadingError:
        raise
    except Exception as e:
        logger.exception("Failed to import plugin %s", file_path)
        raise PluginLoadingError(f"Unable to import plugin {file_path}") from e
