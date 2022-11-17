import datetime
from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.orm import Session as SASession

from duty_overview.models.calendar import Calendar
from duty_overview.models.person import Person


class AbstractPlugin(ABC):
    admin_session_length: datetime.timedelta = datetime.timedelta(days=7)
    person_update_frequency: datetime.timedelta = datetime.timedelta(hours=1)
    calendar_update_frequency: datetime.timedelta = datetime.timedelta(days=1)
    company_color_code: str = "3C9C2D"

    @abstractmethod
    def sync_person(self, person: Person, session: SASession) -> None:
        pass

    @abstractmethod
    def sync_calendar(self, calendar: Calendar, session: SASession) -> None:
        pass

    @abstractmethod
    def location_to_company_logo(self) -> Optional[str]:
        pass

    @abstractmethod
    async def admin_login_attempt(self, username: str, password: str) -> bool:
        pass
