from sqlalchemy import Column, String, Boolean, PickleType, Integer

from settings import Base
from sqlalchemy_types import UtcDateTime


class Person(Base):
    __tablename__ = "person"
    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    ldap = Column(String(50), primary_key=True, unique=True)
    email = Column(String(50), primary_key=True, unique=True)
    attributes = Column(PickleType())
    last_update = Column(UtcDateTime())
    sync = Column(Boolean())
