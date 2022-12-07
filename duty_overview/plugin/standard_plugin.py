from pathlib import Path

from pendulum import DateTime
from sqlalchemy.orm import Session as SASession

from duty_overview.models.calendar import Calendar
from duty_overview.models.person import Person
from duty_overview.plugin.abstract_plugin import AbstractPlugin


class StandardPlugin(AbstractPlugin):
    absolute_path_to_company_logo_png = Path(__file__).resolve().parent / "example_logo.png"
    category_order = ["Big Data", "Infrastructure"]

    # @ToDo(jorrick) Create utility to merge two persons into one.
    # Thereby replacing all the person_uids in the OnCallEvent table.

    def sync_person(self, person: Person, session: SASession) -> None:
        """This is to be implemented by our end user."""
        person.last_update_utc = DateTime.utcnow()

    def sync_calendar(self, calendar: Calendar, event_prefix, session: SASession) -> None:
        raise NotImplementedError()

    async def admin_login_attempt(self, username: str, password: str) -> bool:
        return username == "admin" and password == "admin123"
