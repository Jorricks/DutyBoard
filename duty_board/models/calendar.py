from typing import TYPE_CHECKING, List, Optional

from pendulum.datetime import DateTime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from duty_board.alchemy.settings import Base
from duty_board.alchemy.sqlalchemy_types import UtcDateTime

if TYPE_CHECKING:
    from duty_board.models.on_call_event import OnCallEvent


class Calendar(Base):
    __tablename__ = "calendar"
    uid: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    order: Mapped[int]
    icalendar_url: Mapped[str] = mapped_column(String(500), nullable=False)
    event_prefix: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_msg: Mapped[Optional[str]] = mapped_column(
        String(9999),
        nullable=True,
        comment="If any, the error of the latest sync attempt.",
    )
    last_update_utc: Mapped[DateTime] = mapped_column(UtcDateTime(), nullable=False)
    sync: Mapped[bool] = mapped_column(default=True)
    events: Mapped[List["OnCallEvent"]] = relationship(
        back_populates="calendar",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Calendar(uid={self.uid})"
