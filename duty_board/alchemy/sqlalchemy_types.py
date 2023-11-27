from datetime import datetime
from typing import Any, Optional

import pendulum
from sqlalchemy import DateTime, TypeDecorator

utc = pendulum.tz.timezone("UTC")


class UtcDateTime(TypeDecorator):  # type: ignore[type-arg]
    """
    Almost equivalent to :class:`~sqlalchemy.types.DateTime` with
    ``timezone=True`` option, but it differs from that by:

    - Never silently take naive :class:`~datetime.datetime`, instead it
      always raise :exc:`ValueError` unless time zone aware value.
    - :class:`~datetime.datetime` value's :attr:`~datetime.datetime.tzinfo`
      is always converted to UTC.
    - Unlike SQLAlchemy's built-in :class:`~sqlalchemy.types.DateTime`,
      it never return naive :class:`~datetime.datetime`, but time zone
      aware value, even with SQLite or MySQL.
    - Always returns DateTime in UTC

    """

    impl = DateTime(timezone=True)

    cache_ok = True

    def process_bind_param(self, value: Optional[datetime], dialect: Any) -> Optional[datetime]:  # noqa: ARG002
        if value is not None:
            if not isinstance(value, datetime):
                raise TypeError("expected datetime.datetime, not " + repr(value))
            if value.tzinfo is None:
                raise ValueError("naive datetime is disallowed")
            return value.astimezone(utc)
        return None

    def process_result_value(self, value: Optional[datetime], dialect: Any) -> Optional[datetime]:  # noqa: ARG002
        """
        Processes DateTimes from the DB making sure it is always returning UTC. Not using timezone.convert_to_utc as
        that converts to configured TIMEZONE while the DB might be running with some other setting. We assume UTC
        datetimes in the database.
        """
        if value is not None:
            value = value.replace(tzinfo=utc) if value.tzinfo is None else value.astimezone(utc)
        return value
