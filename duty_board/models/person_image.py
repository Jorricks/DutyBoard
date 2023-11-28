from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from duty_board.alchemy.settings import Base

if TYPE_CHECKING:
    from duty_board.models.person import Person


class PersonImage(Base):
    __tablename__ = "person_image"
    uid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    image_in_bytes: Mapped[bytes] = mapped_column(nullable=False)  # LargeBinary
    person: Mapped["Person"] = relationship(
        back_populates="image",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"PersonImage(uid='{self.uid}')"
