from pathlib import Path
from typing import ClassVar, List

from duty_board.plugin.abstract_plugin import AbstractPlugin
from duty_board.plugin.helpers.duty_calendar_config import DutyCalendarConfig
from duty_board.plugin.ical_plugin_mixin import ICalPluginMixin
from duty_board.plugin.ldap_plugin_mixin import LDAPPluginMixin


class ExamplePlugin(ICalPluginMixin, LDAPPluginMixin, AbstractPlugin):
    absolute_path_to_favicon_ico = Path(__file__).resolve().parent / "favicon.ico"
    absolute_path_to_company_logo_png = Path(__file__).resolve().parent / "example_logo.png"
    category_order: ClassVar[List[str]] = ["Big Data", "Infrastructure"]
    # All required functions are implemented by ICalPluginMixin & LDAPPluginMixin

    duty_calendar_configurations: ClassVar[List[DutyCalendarConfig]] = [
        DutyCalendarConfig(
            uid="data_platform_duty",
            name="Data Platform Duty",
            description="If you have any issues with Spark, Airflow or Jupyterhub, contact these guys. "
            "They are available 24/7, however, they work in AMS hours. Only call them if there is an "
            "emergency.",
            icalendar_url="http://ical_server:8002/icalendar1.ics",
            category="Big Data",
            order=1,
            event_prefix=None,
        ),
        DutyCalendarConfig(
            uid="infrastructure_duty",
            name="Infrastructure",
            description="If you have any issues with Firewalls or critical tools such as Yarn, HDFS etc."
            "However, usually Data Platform Duty is your first point of contact for application "
            "issues.",
            icalendar_url="http://ical_server:8002/icalendar2.ics",
            category="Infrastructure",
            order=2,
            event_prefix=None,
        ),
        DutyCalendarConfig(
            uid="machine_learning",
            name="Machine learning",
            description="Do you have any issues with your machine learning tools? Ask these guys.",
            icalendar_url="http://ical_server:8002/icalendar3.ics",
            category="Big Data",
            order=3,
            event_prefix=None,
        ),
    ]
