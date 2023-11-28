import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, List, Optional

from sqlalchemy.orm import Session as SASession

from duty_board.models.calendar import Calendar
from duty_board.models.person import Person
from duty_board.plugin.helpers.duty_calendar_config import DutyCalendarConfig


class AbstractPlugin(ABC):
    admin_session_length: ClassVar[datetime.timedelta] = datetime.timedelta(days=7)
    person_update_frequency: ClassVar[datetime.timedelta] = datetime.timedelta(hours=1)
    calendar_update_frequency: ClassVar[datetime.timedelta] = datetime.timedelta(days=1)
    background_color_hex: ClassVar[str] = "#3C9C2D"
    text_color_hex: ClassVar[str] = "white"
    absolute_path_to_favicon_ico: ClassVar[Path] = Path(__file__).resolve().parent / "example" / "favicon.ico"
    absolute_path_to_company_logo_png: ClassVar[Path] = Path(__file__).resolve().parent / "example" / "example_logo.png"
    category_order: ClassVar[List[str]] = []
    duty_calendar_configurations: ClassVar[List[DutyCalendarConfig]] = []
    enable_admin_button: ClassVar[bool] = False
    git_repository_url: ClassVar[Optional[str]] = "https://github.com/Jorricks/DutyBoard"
    footer_html: ClassVar[Optional[str]] = """
    Welcome to DutyBoard. <br>
    In case you want to know more check <a href="https://github.com/Jorricks/DutyBoard">here</a>.<br>
    Cheers!
    """

    announcement_background_color_hex: ClassVar[str] = "#FF0000"
    announcement_text_color_hex: ClassVar[str] = "#FFFFFF"
    announcements: ClassVar[List[str]] = [
        "This is a debug setup. Please disable this announcement in your plugin by overwriting announcements variable.",
    ]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def sync_person(self, person: Person, session: SASession) -> Person:
        pass

    @abstractmethod
    def sync_calendar(self, calendar: Calendar, session: SASession) -> Calendar:
        pass

    @abstractmethod
    async def admin_login_attempt(self, username: str, password: str) -> bool:
        pass
