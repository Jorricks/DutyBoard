from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from duty_board.alchemy.settings import Base
from duty_board.alchemy.sqlalchemy_types import UtcDateTime


class OnCallEvent(Base):
    """
    SQLAlchemy Model for on-call-events. Meaning, the time a person is on Duty.

    Note: Originally the uid was not added, however, sqladmin does not support composite keys. So this was added to be
    a singular primary key.
    """

    __tablename__ = "on_call_event"
    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    calendar_uid = Column(String(50), ForeignKey("calendar.uid"), nullable=False)
    start_event_utc = Column(UtcDateTime(), nullable=False)
    end_event_utc = Column(UtcDateTime(), nullable=False)
    person_uid = Column(Integer, ForeignKey("person.uid"), nullable=False)
    calendar = relationship("Calendar", back_populates="events")
    person = relationship("Person")

    def __repr__(self):
        return (
            f"OnCallEvent(calendar='{self.calendar_uid}', start_event='{self.start_event_utc}', "
            f"end_event='{self.end_event_utc}', person='{self.person_uid}')"
        )
