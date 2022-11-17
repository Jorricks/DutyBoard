from typing import List, Set

from fastapi import FastAPI

from duty_overview.alchemy import add_sqladmin, queries, settings
from duty_overview.plugin import plugin_fetcher
from duty_overview.response_types import _Calendar, _Person, CurrentSchedule
from duty_overview.alchemy.session import create_session

settings.configure_orm()
plugin = plugin_fetcher.get_plugin()
app = FastAPI()
admin = add_sqladmin.add_sqladmin(app=app, plugin=plugin)


@app.get("/get_schedule/", response_model=CurrentSchedule)
async def get_schedule():
    with create_session() as session:
        all_encountered_person_uids: Set[int] = set()
        calendars: List[_Calendar] = queries.get_calendars(session, all_encountered_person_uids)
        persons: List[_Person] = queries.get_persons(session, all_encountered_person_uids)
        return CurrentSchedule(
            calendars=calendars,
            persons=persons
        )
