from sqlalchemy import Boolean, Column, Index, Integer, String

from duty_board.alchemy.settings import Base
from duty_board.alchemy.sqlalchemy_types import UtcDateTime


class Person(Base):
    __table_args__ = (Index("person_last_update_utc", "last_update_utc"),)
    __tablename__ = "person"
    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    username = Column(String(50), nullable=True, unique=True)
    email = Column(String(50), nullable=True, unique=True)
    img_filename = Column(String(100), nullable=True)
    extra_attributes_json = Column(String(100000), nullable=True, comment="Extra attributes represented as a json.")
    error_msg = Column(String(9999), nullable=True, comment="If any, the error of the latest sync attempt.")
    last_update_utc = Column(UtcDateTime(), nullable=False)
    sync = Column(Boolean(), default=True, nullable=False)

    def __repr__(self) -> str:
        return f"Person(username='{self.username}', email='{self.email}')"
