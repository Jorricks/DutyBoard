from sqlalchemy import Column, Index, String

from duty_board.alchemy.settings import Base
from duty_board.alchemy.sqlalchemy_types import UtcDateTime


class Token(Base):
    __table_args__ = (Index("token_last_update_utc", "last_update_utc"),)
    __tablename__ = "token"
    token = Column(String(50), unique=True, primary_key=True)
    username = Column(String(50), unique=True)
    last_update_utc = Column(UtcDateTime(), nullable=False)

    def __repr__(self) -> str:
        return f"Token(token='{self.token}', last_update_utc='{self.last_update_utc}')"
