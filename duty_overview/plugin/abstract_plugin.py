from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session as SASession

from duty_overview.models.calendar import Calendar
from duty_overview.models.person import Person


class AbstractPlugin(ABC):
    admin_session_length: datetime.timedelta = datetime.timedelta(days=7)
    person_update_frequency: datetime.timedelta = datetime.timedelta(hours=1)
    calendar_update_frequency: datetime.timedelta = datetime.timedelta(days=1)
    company_color_hex: str = "3C9C2D"
    absolute_path_to_company_logo_png: Path | None = None

    @abstractmethod
    def sync_person(self, person: Person, session: SASession) -> None:
        pass

    @abstractmethod
    def sync_calendar(self, calendar: Calendar, prefix: Optional[str], session: SASession) -> None:
        pass

    @abstractmethod
    async def admin_login_attempt(self, username: str, password: str) -> bool:
        pass
