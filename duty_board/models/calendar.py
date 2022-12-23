from sqlalchemy import Boolean, Column, Index, Integer, String
from sqlalchemy.orm import relationship

from duty_board.alchemy.settings import Base
from duty_board.alchemy.sqlalchemy_types import UtcDateTime


class Calendar(Base):
    __table_args__ = (Index("calendar_last_update_utc", "last_update_utc"),)
    __tablename__ = "calendar"
    uid = Column(String(50), primary_key=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(5000), nullable=True)
    category = Column(String(50), nullable=False)
    order = Column(Integer, nullable=False)
    icalendar_url = Column(String(500), nullable=True)
    event_prefix = Column(String(50), nullable=True)
    error_msg = Column(String(9999), nullable=True, comment="If any, the error of the latest sync attempt.")
    last_update_utc = Column(UtcDateTime(), nullable=False)
    sync = Column(Boolean(), default=True, nullable=False)
    events = relationship("OnCallEvent", back_populates="calendar", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Calendar(uid={self.uid})"
