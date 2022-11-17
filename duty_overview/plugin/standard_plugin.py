from typing import Optional

from pendulum import DateTime
from sqlalchemy.orm import Session as SASession

from duty_overview.models.calendar import Calendar
from duty_overview.models.person import Person
from duty_overview.plugin.abstract_plugin import AbstractPlugin


class StandardPlugin(AbstractPlugin):
    def sync_person(self, person: Person, session: SASession) -> None:
        """This is to be implemented by our end user."""
        person.last_update_utc = DateTime.utcnow()

    def sync_calendar(self, calendar: Calendar, session: SASession) -> None:
        raise NotImplementedError()

    def location_to_company_logo(self) -> Optional[str]:
        pass

    async def admin_login_attempt(self, username: str, password: str) -> bool:
        return username == "admin" and password == "admin123"
