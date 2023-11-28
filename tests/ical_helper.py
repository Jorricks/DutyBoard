import random
import string
from datetime import timedelta
from pathlib import Path
from typing import Optional, Iterable, Tuple, Union

from pendulum import DateTime


def _get_icalender_event(
    username: Optional[str],
    email: Optional[str],
    delta_start: Union[timedelta, DateTime],
    delta_end: timedelta,
    relative_to: Optional[DateTime]
) -> str:
    start = ((relative_to or DateTime.now()) + delta_start) if isinstance(delta_start, timedelta) else delta_start
    end = start + delta_end
    attendee = f"ATTENDEE:{email}\n" if email else ""
    return f"""BEGIN:VEVENT
DTSTART;VALUE=DATE-TIME:{start.strftime("%Y%m%d")}T020000Z
DTEND;VALUE=DATE-TIME:{end.strftime("%Y%m%d")}T020000Z
{attendee}UID:{''.join(random.sample(string.ascii_lowercase, 14))}
URL:https://adyen.pagerduty.com/schedules#P5IHOP7
SUMMARY:{username}
END:VEVENT"""


def get_icalendar_response(
    events: Iterable[Tuple[Optional[str], Optional[str], timedelta, timedelta]],
    relative_to: Optional[DateTime] = None,
) -> str:
    start_text = """BEGIN:VCALENDAR
PRODID;X-RICAL-TZSOURCE=TZINFO:-//com.denhaven2/NONSGML ri_cal gem//EN
CALSCALE:GREGORIAN
VERSION:2.0
X-WR-CALNAME:On Call Schedule for Data-duty"""
    end_text = "END:VCALENDAR"
    events_str = [
        _get_icalender_event(
            username=username, email=email, delta_start=delta_start, delta_end=delta_end, relative_to=relative_to
        )
        for username, email, delta_start, delta_end in events
    ]
    event_text = "\n".join(events_str)
    return f"{start_text}\n{event_text}\n{end_text}"


def run_file_creation() -> None:
    path_to_data_folder = Path(__file__).resolve().parent.parent / ".data" / "ical_files"
    path_to_data_folder.mkdir(parents=False, exist_ok=True)

    (path_to_data_folder / "icalendar1.ics").write_text(
        get_icalendar_response(
            events=[
                ("jan", None, timedelta(hours=-1), timedelta(days=1)),
                ("jan", "mailto:jan@schoenmaker.nl", timedelta(days=1), timedelta(days=1)),
                ("henkietankie", "henk@tank.nl", timedelta(days=2), timedelta(days=20)),
                ("non-existing", None, timedelta(days=20), timedelta(days=20)),
            ]
        )
    )
    (path_to_data_folder / "icalendar2.ics").write_text(
        get_icalendar_response(
            events=[
                ("non-existing-user", None, timedelta(hours=-2), timedelta(days=2)),
                ("nope", "mailto:another@non-existing.user", timedelta(days=2), timedelta(days=5)),
            ]
        )
    )

    print(f"Created the 2 icalendar files.")


if __name__ == "__main__":
    run_file_creation()
