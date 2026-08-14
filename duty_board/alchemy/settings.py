import logging
import os
from typing import Callable, Dict

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker
from sqlalchemy.orm import Session as SASession

log = logging.getLogger(__name__)
SQL_ALCHEMY_CONN: str = os.environ["SQL_ALCHEMY_CONNECTION"]
# Safety net so a stray open transaction self-heals instead of blocking autovacuum. Defaults to 5
# minutes, well above the workers' expected sub-second transactions.
IDLE_IN_TRANSACTION_TIMEOUT_MS: int = int(os.environ.get("IDLE_IN_TRANSACTION_SESSION_TIMEOUT_MS", 5 * 60 * 1000))


def _connect_args(connection_string: str) -> Dict[str, str]:
    # Only libpq (PostgreSQL) understands the `options` parameter; other drivers would reject it.
    if not connection_string.startswith(("postgresql", "postgres")):
        return {}
    return {"options": f"-c idle_in_transaction_session_timeout={IDLE_IN_TRANSACTION_TIMEOUT_MS}"}


engine: Engine = create_engine(
    SQL_ALCHEMY_CONN,
    connect_args=_connect_args(SQL_ALCHEMY_CONN),
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
