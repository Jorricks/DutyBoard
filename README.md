<p align="center">
  <a href="https://github.com/Jorricks/DutyBoard"><img src="https://github.com/Jorricks/DutyBoard/raw/main/docs/duty_board.drawio.png" alt="DutyBoard" width="600px"></a>
</p>
<p align="center">
    <em>Provide a simple, yet extensive overview of your Duty calendars using <a href="https://www.ietf.org/rfc/rfc5545.txt">RFC 5545</a> compliant iCalendars.<br> Verified with PagerDuty, Google & Microsoft outlook Calendars.</em>
</p>
<p align="center">

[//]: # (<a href="https://pypi.org/project/DutyBoard" target="_blank">)

[//]: # (    <img src="https://img.shields.io/pypi/v/DutyBoard?color=%2334D058&label=pypi%20package" alt="Package version">)

[//]: # (</a>)

[//]: # (<a href="https://pypi.org/project/DutyBoard" target="_blank">)

[//]: # (    <img src="https://img.shields.io/pypi/pyversions/DutyBoard.svg?color=%2334D058" alt="Supported Python versions">)

[//]: # (</a>)
</p>


---

**Source Code**: [https://github.com/Jorricks/DutyBoard](https://github.com/Jorricks/DutyBoard)


## Features
- 🚀 Extendable Plugin structure allowing you to tune calendars & enrich duty officers information with for example LDAP.
- 📈 Full <a href="https://www.ietf.org/rfc/rfc5545.txt">RFC 5545</a> compliant iCalendar support, including recurring events, by using [iCal-library](https://jorricks.github.io/iCal-library/).
- ✨ ***Dynamic web-interface*** with the ability to tune using the plugin structure. Examples would be:
    1. Different color schemes.
    2. Your own company logo.
    3. Icons for extra user information.
    4. And much much more.
- 💪 React front-end is pre-compiled and served through FastAPI.
- 🆎 Fully typed code base.

## Requirements
Python 3.8+

DutyBoard runs using:
- [FastAPI](https://fastapi.tiangolo.com/) as web service.
- [iCal-library](https://jorricks.github.io/iCal-library/) for it's integration with iCalendars.

## Plugin structure
More on this later once it's fully deployed.

## Why this project?
Larger corporations often have many Duty schedules. This is often to shield team members from ad-hoc work during their work-week or to ensure the platform runs smoothly 24/7. However, exposing Duty schedules is easy at the start, but once you have three schedules, it becomes unclear who is on duty. Hence, a small front-end usually solves this, but that require manual intervention when the schedule changes. This projects aims to solve that by automatically fetching who is on duty from iCalendars

## Ideas for additional features
- Implement announcement calendar.
- Implement extra plugin sync functionality, e.g. Workday integration.
