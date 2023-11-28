from typing import TYPE_CHECKING

from pendulum.datetime import DateTime
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from duty_board.alchemy.settings import Base
from duty_board.alchemy.sqlalchemy_types import UtcDateTime
from duty_board.models.calendar import Calendar

if TYPE_CHECKING:
    from duty_board.models.person import Person


class OnCallEvent(Base):
    """
    SQLAlchemy Model for on-call-events. Meaning, the time a person is on Duty.

    Note: Originally the uid was not added, however, sqladmin does not support composite keys. So this was added to be
    a singular primary key.
    """

    __tablename__ = "on_call_event"
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    start_event_utc: Mapped[DateTime] = mapped_column(UtcDateTime(), nullable=False)
    end_event_utc: Mapped[DateTime] = mapped_column(UtcDateTime(), nullable=False)

    calendar_uid: Mapped[str] = mapped_column(String(50), ForeignKey("calendar.uid", ondelete="CASCADE"))
    calendar: Mapped["Calendar"] = relationship(back_populates="events")

    person_uid: Mapped[int] = mapped_column(Integer, ForeignKey("person.uid", ondelete="CASCADE"), nullable=False)
    person: Mapped["Person"] = relationship(back_populates="upcoming_events")

    def __repr__(self) -> str:
        return (
            f"OnCallEvent(calendar='{self.calendar_uid}', start_event='{self.start_event_utc}', "
            f"end_event='{self.end_event_utc}', person='{self.person_uid}')"
        )
