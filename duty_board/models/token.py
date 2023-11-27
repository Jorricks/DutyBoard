from pendulum.datetime import DateTime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from duty_board.alchemy.settings import Base
from duty_board.alchemy.sqlalchemy_types import UtcDateTime


class Token(Base):
    __tablename__ = "token"
    token: Mapped[str] = mapped_column(String(50), unique=True, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    last_update_utc: Mapped[DateTime] = mapped_column(UtcDateTime(), nullable=False)

    def __repr__(self) -> str:
        return f"Token(token='{self.token}', last_update_utc='{self.last_update_utc}')"
