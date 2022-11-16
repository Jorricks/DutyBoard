import datetime

from fastapi import FastAPI
from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from sqladmin.fields import DateTimeField
from starlette.requests import Request

from duty_overview.alchemy import settings
from duty_overview.alchemy.settings import Base
from duty_overview.alchemy.sqlalchemy_types import utc
from duty_overview.models.calendar import Calendar
from duty_overview.models.on_call_event import OnCallEvent
from duty_overview.models.person import Person


class AppBuilderDateTimeAwareSelector(DateTimeField):
    """This is a DateTimePicker"""

    def process_formdata(self, valuelist):
        """This solves the issue with editing a record. Here the timezone would show up. We don't want that!"""
        super().process_formdata(valuelist)
        if self.data is not None:
            self.data = self.data.astimezone(utc)


class PersonAdmin(ModelView, model=Person):
    column_searchable_list = [Person.ldap, Person.email, Person.sync]
    column_sortable_list = [Person.uid, Person.ldap, Person.email, Person.last_update_utc, Person.sync]
    column_list = [Person.uid, Person.ldap, Person.email, Person.last_update_utc, Person.sync]
    form_overrides = dict(last_update_utc=AppBuilderDateTimeAwareSelector)

    def is_visible(self, request: Request) -> bool:
        return True

    def is_accessible(self, request: Request) -> bool:
        return True


class CalendarAdmin(ModelView, model=Calendar):
    column_searchable_list = [Calendar.uid, Calendar.name, Calendar.sync]
    column_sortable_list = [Calendar.uid, Calendar.name, Calendar.last_update_utc, Calendar.sync]
    column_list = [Calendar.uid, Calendar.name, Calendar.last_update_utc, Calendar.sync]
    form_columns = [  # Adds an order to it :)
        Calendar.uid,
        Calendar.name,
        Calendar.description,
        Calendar.icalendar_url,
        Calendar.error_msg,
        Calendar.last_update_utc,
        Calendar.sync,
    ]
    form_overrides = dict(last_update_utc=AppBuilderDateTimeAwareSelector)
    form_include_pk = True

    def is_visible(self, request: Request) -> bool:
        return True

    def is_accessible(self, request: Request) -> bool:
        return True


class OnCallEventAdmin(ModelView, model=OnCallEvent):
    column_searchable_list = [
        OnCallEvent.calendar_uid, OnCallEvent.start_event_utc, OnCallEvent.end_event_utc, OnCallEvent.person_uid
    ]
    column_sortable_list = [OnCallEvent.calendar_uid, OnCallEvent.start_event_utc, OnCallEvent.end_event_utc]
    column_list = [OnCallEvent.calendar, OnCallEvent.start_event_utc, OnCallEvent.end_event_utc, OnCallEvent.person]
    form_columns = [OnCallEvent.calendar, OnCallEvent.start_event_utc, OnCallEvent.end_event_utc, OnCallEvent.person]
    form_overrides = dict(
        start_event_utc=AppBuilderDateTimeAwareSelector, end_event_utc=AppBuilderDateTimeAwareSelector
    )
    form_include_pk = True
    form_ajax_refs = {
        "person": {
            "fields": ("ldap", "email"),
        }
    }

    def is_visible(self, request: Request) -> bool:
        return True

    def is_accessible(self, request: Request) -> bool:
        return True


def add_sqladmin(app: FastAPI) -> Admin:
    # Create the tables if that was not done already
    Base.metadata.create_all(settings.get_engine())

    authentication_backend = MyBackend(secret_key="...")
    admin = Admin(app=app, engine=settings.get_engine(), authentication_backend=authentication_backend)
    admin.add_view(PersonAdmin)
    admin.add_view(CalendarAdmin)
    admin.add_view(OnCallEventAdmin)
    return admin


class MyBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        # Validate username/password credentials
        # And update session
        request.session.update({"token": "..."})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token
        return True
