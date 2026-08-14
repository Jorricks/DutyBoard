import logging
import os
from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker
from sqlalchemy.orm import Session as SASession

log = logging.getLogger(__name__)
SQL_ALCHEMY_CONN: str = os.environ["SQL_ALCHEMY_CONNECTION"]
engine: Engine = create_engine(
    SQL_ALCHEMY_CONN,
    connect_args={},
    pool_size=10,
    pool_recycle=1800,
    pool_pre_ping=True,
    max_overflow=10,
)
Session: Callable[..., SASession] = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    ),
)


class Base(DeclarativeBase):
    pass
