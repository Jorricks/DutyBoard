from sqlalchemy import Column, Integer, ForeignKey, String, CheckConstraint
from sqlalchemy.orm import relationship, backref

from settings import Base
from sqlalchemy_types import UtcDateTime


class OnCallEvent(Base):
    __table_args__ = (CheckConstraint('NOT(ldap IS NULL AND email IS NULL)'))
    __tablename__ = "on_call_event"
    calendar_uid = Column(String(50), ForeignKey("Calendar.uid"), primary_key=True, nullable=False)
    start_event = Column(UtcDateTime(), primary_key=True, nullable=False)
    end_event = Column(UtcDateTime(), primary_key=True, nullable=False)
    person_uid = Column(Integer, ForeignKey("Person.uid"), nullable=False)
    person = relationship("Person")
