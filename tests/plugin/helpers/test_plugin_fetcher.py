import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import pytest

from duty_board.exceptions import PluginLoadingError
from duty_board.plugin.example import example_plugin
from duty_board.plugin.example.example_plugin import ExamplePlugin
from duty_board.plugin.helpers import plugin_fetcher
from tests.conftest import set_ldap_env_variables


class MyPlugin(ExamplePlugin):
    pass


@pytest.fixture(autouse=True)
def __clear_cache() -> None:
    plugin_fetcher._get_plugin.cache_clear()


@contextmanager
def with_set_example_plugin_location(load_my_plugin: bool) -> Generator[None, None, None]:
    try:
        with set_ldap_env_variables():
            if load_my_plugin:
                os.environ["DUTY_BOARD_PLUGIN_LOCATION"] = str(Path(__file__).resolve())
                os.environ["DUTY_BOARD_PLUGIN_CLASS_NAME"] = "MyPlugin"
            else:
                os.environ["DUTY_BOARD_PLUGIN_LOCATION"] = str(Path(example_plugin.__file__).resolve())
            yield
    finally:
        if "DUTY_BOARD_PLUGIN_LOCATION" in os.environ:
            del os.environ["DUTY_BOARD_PLUGIN_LOCATION"]
        if "DUTY_BOARD_PLUGIN_CLASS_NAME" in os.environ:
            del os.environ["DUTY_BOARD_PLUGIN_CLASS_NAME"]
        plugin_fetcher._get_plugin.cache_clear()


def test_get_plugin_with_and_without_env() -> None:
    # ExamplePlugin must be local to prevent double plugins.
    with with_set_example_plugin_location(load_my_plugin=True):
        plugin = plugin_fetcher.get_plugin()
        assert plugin.__class__.__name__ == "MyPlugin"

    with with_set_example_plugin_location(load_my_plugin=False):
        plugin = plugin_fetcher.get_plugin()
        assert plugin.__class__.__name__ == "ExamplePlugin"

    assert plugin_fetcher._get_plugin() is None

    with set_ldap_env_variables():
        plugin = plugin_fetcher.get_plugin()
        assert plugin.__class__.__name__ == "ExamplePlugin"


def test_errors(tmp_path: Path) -> None:
    os.environ["DUTY_BOARD_PLUGIN_LOCATION"] = "/some/non/existing/path"
    with pytest.raises(PluginLoadingError, match="is not a file. Please set the plugin location correctly."):
        plugin_fetcher._get_plugin()

    os.environ["DUTY_BOARD_PLUGIN_LOCATION"] = str(Path(__file__).parent.parent.parent.parent / "README.md")
    with pytest.raises(PluginLoadingError, match="must be a Python file."):
        plugin_fetcher._get_plugin()

    os.environ["DUTY_BOARD_PLUGIN_LOCATION"] = str(Path(__file__).resolve())
    with pytest.raises(PluginLoadingError, match="contains multiple AbstractPlugin implementations."):
        plugin_fetcher._get_plugin()

    os.environ["DUTY_BOARD_PLUGIN_LOCATION"] = str(Path(__file__).parent.resolve() / "__init__.py")
    with pytest.raises(PluginLoadingError, match="does not contain any classes that implement the AbstractPlugin."):
        plugin_fetcher._get_plugin()

    python_file = tmp_path / "some_file.py"
    python_file.write_text("import something-invalid")
    os.environ["DUTY_BOARD_PLUGIN_LOCATION"] = str(python_file)
    with pytest.raises(PluginLoadingError, match="Unable to import plugin."):
        plugin_fetcher._get_plugin()
