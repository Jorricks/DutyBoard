from sqlalchemy import Column, String, Boolean, Integer

from duty_overview.alchemy.settings import Base
from duty_overview.alchemy.sqlalchemy_types import UtcDateTime


class Person(Base):
    __tablename__ = "person"
    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    ldap = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    extra_attributes_json = Column(String(100000), nullable=True, comment="Extra attributes represented as a json.")
    error_msg = Column(String(9999), nullable=True, comment="If any, the error of the latest sync attempt.")
    last_update_utc = Column(UtcDateTime(), nullable=False)
    sync = Column(Boolean(), default=True, nullable=False)

    def __repr__(self) -> str:
        return f"Person(ldap='{self.ldap}', email='{self.email}')"
