# DutyBoard
Overview of Duty calendars using iCalendar


## Development

### Installing
```shell
pip3 install --upgrade pip
pip3 install -e ."[dev, test]"
```

### Docker compose setup
#### Docker dev setup
There are two docker compose files setups. The first is purely for development. Here we have a webpack-dev-server running the node.js code inside the container. The front-end automatically connects to the Python FastAPI container for API calls. In this case, you want to use the front-end provided by the node.js container at http://localhost:8080. This setup automatically reloads the FastAPI server on Python code changes and the node.js server on any typescript/css changes.

Note: The first run will create the python venv & install all node modules. This will take some time.

Starting up
```shell
docker-compose -f docker-compose.dev.yaml up -d
```
Shutting down
```shell
docker-compose -f docker-compose.dev.yaml down
```

#### Docker production setup
Once you are sure of your changes, you can test them out with the production setup. Here the node container only compiles the code into the `duty_board/www/dist` folder, which is then served through the Python FastAPI container.
Now you want to use the FastAPI url at http://localhost:8001.
Note: It might take some time for the `dist` folder to become present and thereby throw an error in the FastAPI before it is ready. Simply, restarting it should be enough.

Note: The first run will create the python venv. This will take some time.

Starting up
```shell
docker-compose -f docker-compose.prod.yaml up -d
```
Shutting down
```shell
docker-compose -f docker-compose.prod.yaml down
```

## @ToDos:
- [x] Parse iCalendars
- [x] Create calendar config for usage in Configs
- [x] Create calendar config to Database syncer
- [x] Create docker image
- [x] Create docker compose
- [x] Add extra pre-commit hooks
- [ ] Add improved GZIP handler
- [ ] Add Github pipelines
- [ ] (Optional) Create kustomize example
- [ ] (Optional) Implement announcement calendar

## Extra pre-commit hooks;
- [ ] Automated run of generate_typescript_api.py.
