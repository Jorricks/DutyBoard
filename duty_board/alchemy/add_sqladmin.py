import asyncio
import os
import secrets
import string
from typing import Any, ClassVar, Dict, List, Optional

from fastapi import FastAPI
from pendulum.datetime import DateTime
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqladmin.fields import DateTimeField
from sqlalchemy import select
from sqlalchemy.orm import Session as SASession
from starlette.requests import Request
from wtforms.fields.core import Field

from duty_board.alchemy import settings
from duty_board.alchemy.session import create_session
from duty_board.alchemy.sqlalchemy_types import utc
from duty_board.models.calendar import Calendar
from duty_board.models.on_call_event import OnCallEvent
from duty_board.models.person import Person
from duty_board.models.token import Token
from duty_board.plugin.abstract_plugin import AbstractPlugin

loop = asyncio.get_event_loop()


class AppBuilderDateTimeAwareSelector(DateTimeField):
    """This is a DateTimePicker"""

    def process_formdata(self, valuelist: List[Any]) -> None:
        """This solves the issue with editing a record. Here the timezone would show up. We don't want that!"""
        super().process_formdata(valuelist)
        if self.data is not None:  # type: ignore[has-type]
            self.data = self.data.astimezone(utc)  # type: ignore[has-type]


class PersonAdmin(ModelView, model=Person):
    column_searchable_list = [Person.username, Person.email, Person.sync]
    column_sortable_list = [Person.uid, Person.username, Person.email, Person.last_update_utc, Person.sync]
    column_list = [Person.uid, Person.username, Person.email, Person.last_update_utc, Person.sync]
    form_overrides: ClassVar[Dict[str, Field]] = {"last_update_utc": AppBuilderDateTimeAwareSelector}


class CalendarAdmin(ModelView, model=Calendar):
    column_searchable_list = [Calendar.uid, Calendar.name, Calendar.sync, Calendar.category]
    column_sortable_list = [
        Calendar.uid,
        Calendar.name,
        Calendar.last_update_utc,
        Calendar.sync,
        Calendar.category,
        Calendar.order,
        Calendar.error_msg,
    ]
    column_list = [Calendar.uid, Calendar.name, Calendar.last_update_utc, Calendar.sync]
    form_columns = [  # Adds an order to it :)
        Calendar.uid,
        Calendar.name,
        Calendar.description,
        Calendar.icalendar_url,
        Calendar.event_prefix,
        Calendar.category,
        Calendar.order,
        Calendar.error_msg,
        Calendar.last_update_utc,
        Calendar.sync,
    ]
    form_overrides: ClassVar[Dict[str, Field]] = {"last_update_utc": AppBuilderDateTimeAwareSelector}
    form_include_pk = True


class OnCallEventAdmin(ModelView, model=OnCallEvent):
    column_searchable_list = [
        OnCallEvent.calendar_uid,
        OnCallEvent.start_event_utc,
        OnCallEvent.end_event_utc,
        OnCallEvent.person_uid,
    ]
    column_sortable_list = [OnCallEvent.calendar_uid, OnCallEvent.start_event_utc, OnCallEvent.end_event_utc]
    column_list = [OnCallEvent.calendar, OnCallEvent.start_event_utc, OnCallEvent.end_event_utc, OnCallEvent.person]
    form_columns = [OnCallEvent.calendar, OnCallEvent.start_event_utc, OnCallEvent.end_event_utc, OnCallEvent.person]
    form_overrides: ClassVar[Dict[str, Field]] = {
        "start_event_utc": AppBuilderDateTimeAwareSelector,
        "end_event_utc": AppBuilderDateTimeAwareSelector,
    }
    form_include_pk = True
    form_ajax_refs = {
        "person": {
            "fields": ("username", "email"),
        },
    }


class TokenAdmin(ModelView, model=Token):
    can_create = False
    can_edit = False
    can_delete = True
    column_list = [Token.username, Token.token, Token.last_update_utc]


def add_sqladmin(app: FastAPI, plugin: AbstractPlugin) -> Admin:
    authentication_backend = MyBackend(plugin=plugin)
    admin = Admin(app=app, engine=settings.engine, authentication_backend=authentication_backend)
    admin.add_view(PersonAdmin)
    admin.add_view(CalendarAdmin)
    admin.add_view(OnCallEventAdmin)
    admin.add_view(TokenAdmin)
    return admin


class MyBackend(AuthenticationBackend):
    def __init__(self, plugin: AbstractPlugin, *_: Any, **__: Any):
        super().__init__(secret_key=os.environ["DUTY_BOARD_SECRET_KEY"])
        self.plugin = plugin

    @staticmethod
    def create_token(username: str) -> str:
        session: SASession
        with create_session() as session:
            stmt = select(Token).where(Token.username == username)
            current_token: Optional[Token] = session.scalar(stmt)
            if current_token is not None:
                current_token.token = "".join(secrets.choice(string.ascii_lowercase) for i in range(50))
                current_token.last_update_utc = DateTime.utcnow()
            else:
                current_token = Token(
                    token="".join(secrets.choice(string.ascii_lowercase) for i in range(50)),
                    username=username,
                    last_update_utc=DateTime.utcnow(),
                )
                session.merge(current_token)
        return current_token.token

    def verify_token(self, provided_token: str) -> bool:
        session: SASession
        with create_session() as session:
            stmt = select(Token).where(Token.token == provided_token)
            token: Optional[Token] = session.scalar(stmt)
            if not token:
                return False
            if token.last_update_utc < DateTime.utcnow() - self.plugin.admin_session_length:
                session.delete(token)
                return False
            return True

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form["username"]
        password = form["password"]
        if not isinstance(username, str) or not isinstance(password, str):
            raise TypeError(
                f"Got interesting types for {username=} and {password=}, {type(username)=}, {type(password)=}",
            )

        if not await self.plugin.admin_login_attempt(username=username, password=password):
            return False

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, MyBackend.create_token, username)
        request.session.update({"token": result})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not await loop.run_in_executor(None, self.verify_token, token):
            request.session.clear()
            return False
        return True
