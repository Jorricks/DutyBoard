from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from settings import Base
from sqlalchemy_types import UtcDateTime


class Calendar(Base):
    __tablename__ = "calendar"
    uid = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String(5000), nullable=False)
    icalendar_url = Column(String(500), nullable=True)
    last_update = Column(UtcDateTime(), nullable=True)
    sync = Column(Boolean(), default=True, nullable=False)
    events = relationship("OnCallEvent", cascade="all, delete-orphan")
