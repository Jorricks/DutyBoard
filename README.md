# DutyOverview
Overview of Duty calendars using iCalendar


## Development

### Installing
```shell
pip3 install -e ."[dev, test]"
```

### Database
Initial start
```shell
docker run -p 5432:5432 --name pgduty -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```
Stopping
```shell
docker stop pgduty
```
Starting a stopped instance
```shell
docker start pgduty
```
Starting over with a wiped database
```shell
docker stop pgduty; docker rm pgduty
```

### Starting application
```
docker start pgduty
export SQL_ALCHEMY_CONNECTION="postgresql://postgres:mysecretpassword@127.0.0.1:5432/postgres"
export DUTY_OVERVIEW_SECRET_KEY="RANDOM_SECRET_KEY"
export CREATE_DUMMY_RECORDS="1"
uvicorn duty_overview.server:app --reload
```

## Docker compose dev setup
Starting up
```shell
docker-compose -f docker-compose.dev.yaml up -d
```
Shutting down
```shell
docker-compose -f docker-compose.dev.yaml down
```

## @ToDos:
- [x] Parse iCalendars
- [x] Create calendar config for usage in Configs
- [x] Create calendar config to Database syncer
- [ ] Create docker image
- [ ] Create docker compose
- [ ] Create kustomize example
- [ ] Add extra pre-commit hooks
- [ ] (Optional) Implement announcement calendar

## Extra pre-commit hooks;
- [ ] Automated run of generate_typescript_api.py.
- [ ] Docker run to generate new compiled javascript files or other files?