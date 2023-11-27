from pathlib import Path
from typing import ClassVar, List

from duty_board.plugin.abstract_plugin import AbstractPlugin
from duty_board.plugin.ical_plugin_mixin import ICalPluginMixin
from duty_board.plugin.ldap_plugin_mixin import LDAPPluginMixin


class ExamplePlugin(ICalPluginMixin, LDAPPluginMixin, AbstractPlugin):
    absolute_path_to_favicon_ico = Path(__file__).resolve().parent / "favicon.ico"
    absolute_path_to_company_logo_png = Path(__file__).resolve().parent / "example_logo.png"
    category_order: ClassVar[List[str]] = ["Big Data", "Infrastructure"]
    # All required functions are implemented by ICalPluginMixin & LDAPPluginMixin
