from sqlalchemy import Column, String, Boolean, Integer, Index, UniqueConstraint

from duty_overview.alchemy.settings import Base
from duty_overview.alchemy.sqlalchemy_types import UtcDateTime


class Person(Base):
    # @ToDo(jorrick) Make a unique constraint on the combination of ldap&email.
    __table_args__ = (
        Index("person_last_update_utc", "last_update_utc"),
        UniqueConstraint("ldap", "email", name="ldap_email_combination_must_be_unique"),
    )
    __tablename__ = "person"
    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    ldap = Column(String(50), nullable=True)
    email = Column(String(50), nullable=True)
    extra_attributes_json = Column(String(100000), nullable=True, comment="Extra attributes represented as a json.")
    error_msg = Column(String(9999), nullable=True, comment="If any, the error of the latest sync attempt.")
    last_update_utc = Column(UtcDateTime(), nullable=False)
    sync = Column(Boolean(), default=True, nullable=False)

    def __repr__(self) -> str:
        return f"Person(ldap='{self.ldap}', email='{self.email}')"
