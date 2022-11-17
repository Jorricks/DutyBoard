# DutyOverview
Overview of Duty calendars using iCalendar


## Development
Starting it up
```shell
docker run -p 5432:5432 --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres
export SQL_ALCHEMY_CONNECTION="postgresql://postgres:mysecretpassword@127.0.0.1:5432/postgres"
export DUTY_OVERVIEW_SECRET_KEY="RANDOM_SECRET_KEY"
uvicorn duty_overview.server:app --reload
```

Restarting it
```shell
docker stop pgduty; docker rm pgduty
```
