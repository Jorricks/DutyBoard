from pathlib import Path

from sqlalchemy.orm import Session as SASession

from duty_overview.models.calendar import Calendar
from duty_overview.models.person import Person
from duty_overview.plugin.abstract_plugin import AbstractPlugin


class ExamplePlugin(AbstractPlugin):
    absolute_path_to_company_logo_png = Path(__file__).resolve().parent / "example_logo.png"
    absolute_path_to_user_images_folder = Path(__file__).resolve().parent.parent.parent / "www" / "user_images"
    category_order = ["Big Data", "Infrastructure"]

    def sync_person(self, person: Person, session: SASession) -> Person:
        """This is to be implemented by our end user."""
        return person

    def sync_calendar(self, calendar: Calendar, event_prefix, session: SASession) -> Calendar:
        """This is to be implemented by our end user."""
        return calendar

    async def admin_login_attempt(self, username: str, password: str) -> bool:
        return username == "admin" and password == "admin123"
