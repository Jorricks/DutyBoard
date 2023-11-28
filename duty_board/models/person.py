from typing import TYPE_CHECKING, List, Optional

from pendulum.datetime import DateTime
from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from duty_board.alchemy.settings import Base
from duty_board.alchemy.sqlalchemy_types import UtcDateTime
from duty_board.models.person_image import PersonImage

if TYPE_CHECKING:
    from duty_board.models.on_call_event import OnCallEvent


class Person(Base):
    __table_args__ = (
        UniqueConstraint("image_uid", name="unique_image_uid"),  # To make sure it remains a one-to-one.
        UniqueConstraint("username", "email", name="username_email_unique"),
        CheckConstraint("NOT(username IS NULL AND email IS NULL)", name="user_email_not_both_none"),
    )  # To make sure it remains a one-to-one.
    __tablename__ = "person"
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    image_uid: Mapped[Optional[int]] = mapped_column(ForeignKey("person_image.uid", ondelete="RESTRICT"), nullable=True)
    image: Mapped[Optional[PersonImage]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    img_width: Mapped[Optional[int]]
    img_height: Mapped[Optional[int]]
    extra_attributes_json: Mapped[Optional[str]] = mapped_column(
        String(100000),
        nullable=True,
        comment="Extra attributes represented as a json.",
    )
    error_msg: Mapped[Optional[str]] = mapped_column(
        String(9999),
        nullable=True,
        comment="If any, the error of the latest sync attempt.",
    )
    last_update_utc: Mapped[DateTime] = mapped_column(UtcDateTime(), nullable=False)
    sync: Mapped[bool] = mapped_column(default=True)

    # We don't use this field, but still good to indicate this relationship exists
    upcoming_events: Mapped[List["OnCallEvent"]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Person(username='{self.username}', email='{self.email}')"
