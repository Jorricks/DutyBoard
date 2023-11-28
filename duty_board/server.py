import logging
import sys
from pathlib import Path
from typing import Dict, Final, List, Set

import pytz
from fastapi import FastAPI, HTTPException
from pytz.exceptions import UnknownTimeZoneError
from pytz.tzinfo import BaseTzInfo
from sqladmin import Admin
from sqlalchemy import select
from sqlalchemy.orm.session import Session as SASession
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, HTMLResponse, Response
from starlette.staticfiles import StaticFiles
from tzlocal import get_localzone

from duty_board.alchemy import add_sqladmin, api_queries
from duty_board.alchemy.session import create_session
from duty_board.models.person_image import PersonImage
from duty_board.plugin.abstract_plugin import AbstractPlugin
from duty_board.plugin.helpers import plugin_fetcher
from duty_board.web_helpers.gzip_static_files import GZIPStaticFiles
from duty_board.web_helpers.response_types import CurrentSchedule, PersonResponse, _Calendar, _Config, _PersonEssentials

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M",
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

plugin: AbstractPlugin
admin: Admin

CURRENT_DIR: Final[Path] = Path(__file__).absolute().parent
logger.info(f"{CURRENT_DIR=}")

plugin = plugin_fetcher.get_plugin()
app.mount("/dist", GZIPStaticFiles(directory=CURRENT_DIR / "www" / "dist", check_dir=False), name="dist")
app.mount("/static", StaticFiles(directory=CURRENT_DIR / "www" / "static"), name="static")
# @ToDo(jorrick) Implement person image setup
admin = add_sqladmin.add_sqladmin(app=app, plugin=plugin)


def _parse_timezone_str(timezone_str: str) -> BaseTzInfo:
    try:
        return pytz.timezone(timezone_str)
    except UnknownTimeZoneError:
        return get_localzone()


def _get_config_object(timezone_object: BaseTzInfo) -> _Config:
    return _Config(
        text_color=plugin.text_color_hex,
        background_color=plugin.background_color_hex,
        categories=plugin.category_order,
        git_repository_url=plugin.git_repository_url,
        enable_admin_button=plugin.enable_admin_button,
        announcement_text_color=plugin.announcement_text_color_hex,
        announcement_background_color=plugin.announcement_background_color_hex,
        announcements=plugin.announcements,
        footer_html=plugin.footer_html,
        timezone=str(timezone_object),
    )


@app.get("/schedule", response_model=CurrentSchedule)
async def get_schedule(timezone: str) -> CurrentSchedule:
    timezone_object = _parse_timezone_str(timezone)
    config = _get_config_object(timezone_object)
    with create_session() as session:
        all_encountered_person_uids: Set[int] = set()
        calendars: List[_Calendar] = api_queries.get_calendars(
            session=session,
            all_encountered_person_uids=all_encountered_person_uids,
            timezone=timezone_object,
        )
        persons: Dict[int, _PersonEssentials] = api_queries.get_peoples_essentials(
            session=session,
            all_person_uids=all_encountered_person_uids,
        )
        return CurrentSchedule(config=config, calendars=calendars, persons=persons)


@app.get("/person", response_model=PersonResponse)
async def get_person(person_uid: int, timezone: str) -> PersonResponse:
    timezone_object = _parse_timezone_str(timezone)
    with create_session() as session:
        return api_queries.get_person(session=session, person_uid=person_uid, timezone=timezone_object)


@app.get("/person_img/{person_uid:int}", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
async def get_person_image(person_uid: int) -> Response:
    session: SASession
    with create_session() as session:
        person_image: PersonImage = session.scalars(select(PersonImage).where(PersonImage.uid == person_uid)).one()
        return Response(content=person_image.image_in_bytes, media_type="image/jpeg")


@app.get(
    "/company_logo.png",
    response_description="Returns a thumbnail image from a larger image",
    responses={200: {"description": "Company logo", "content": {"image/png": {}}}},
)
def company_logo() -> FileResponse:
    file_path = plugin.absolute_path_to_company_logo_png
    if file_path.is_file():
        return FileResponse(file_path, media_type="image/png", filename="company_logo.png")
    raise HTTPException(status_code=500, detail="Company logo could not be found.")


@app.get(
    "/favicon.ico",
    response_description="Returns the favicon",
    responses={200: {"description": "Favicon", "content": {"image/x-icon": {}}}},
)
def favicon_ico() -> FileResponse:
    file_path = plugin.absolute_path_to_favicon_ico
    if file_path.is_file():
        return FileResponse(file_path, media_type="image/x-icon", filename="favicon.ico")
    raise HTTPException(status_code=500, detail="Company logo could not be found.")


@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def accept_all() -> FileResponse:
    return FileResponse(CURRENT_DIR / "www" / "dist" / "index.html")
