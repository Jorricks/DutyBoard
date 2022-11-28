import os
from typing import Dict, List, Set

import pytz
from fastapi import FastAPI
from pytz.exceptions import UnknownTimeZoneError
from pytz.tzinfo import BaseTzInfo
from sqladmin import Admin
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from tzlocal import get_localzone

from duty_overview.alchemy import add_sqladmin, queries, settings
from duty_overview.alchemy.session import create_session
from duty_overview.models import generate_fake_data
from duty_overview.plugin import plugin_fetcher
from duty_overview.plugin.abstract_plugin import AbstractPlugin
from duty_overview.response_types import _Calendar, _Config, _Person, CurrentSchedule

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

plugin: AbstractPlugin
admin: Admin
if settings.SQL_ALCHEMY_CONN:
    settings.configure_orm()
    plugin = plugin_fetcher.get_plugin()
    admin = add_sqladmin.add_sqladmin(app=app, plugin=plugin)
    if os.environ.get("CREATE_DUMMY_RECORDS", "") == "1":
        generate_fake_data.create_fake_database_rows_if_not_present()


@app.get("/get_schedule", response_model=CurrentSchedule)
async def get_schedule(timezone: str):
    try:
        timezone_object: BaseTzInfo = pytz.timezone(timezone)
    except UnknownTimeZoneError:
        timezone_object = get_localzone()

    config = _Config(
        text_color=plugin.text_color_hex,
        background_color=plugin.background_color_hex,
        categories=plugin.category_order,
        timezone=timezone_object.zone,
    )
    with create_session() as session:
        all_encountered_person_uids: Set[int] = set()
        calendars: List[_Calendar] = queries.get_calendars(
            session=session, all_encountered_person_uids=all_encountered_person_uids, timezone=timezone_object
        )
        persons: Dict[int, _Person] = queries.get_persons(
            session=session, all_person_uids=all_encountered_person_uids, timezone=timezone_object
        )
        return CurrentSchedule(config=config, calendars=calendars, persons=persons)


@app.get(
    "/company_logo.png",
    response_description="Returns a thumbnail image from a larger image",
    responses={200: {"description": "Company logo", "content": {"image/png": {}}}},
)
def thumbnail_image():
    file_path = plugin.absolute_path_to_company_logo_png
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/jpeg", filename="company_logo.png")
    return {"error": f"{file_path=} not found!"}
