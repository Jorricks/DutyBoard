# Contributing
Happy to have you onboard and interested to develop DutyBoard to the next level.

## Commit messages
We follow [GitMoji](https://gitmoji.dev/) styled commit messages. This means, you start your commit message with an emoji and follow with a short description. Examples:
- 🎨 Restructured folder structure
- 🔥 Implemented GZIP support
- 🐛 Uncaught exception on /get_schedule endpoint 

## Local development
The entire development environment of node.js is containerized. It will still download the node.js modules to your hard drive as intermittent storage, but there is no need to execute anything directly from your computer.
The python virtual environment is both in the container and natively on your system for your IDE.

### Installing
Setting up the python virtual environment locally for your IDE.
```shell
python3.8 -m venv venv/
source pvenv/bin/activate
pip3 install --upgrade pip
pip3 install -e ."[dev, test]"
```

### Docker compose setup
#### Docker dev setup
There are two docker compose files setups. The first is purely for development. Here we have a webpack-dev-server running the node.js code inside the container. The front-end automatically connects to the Python FastAPI container for API calls. In this case, you want to use the front-end provided by the node.js container at http://localhost:8080. This setup automatically reloads the FastAPI server on Python code changes and the node.js server on any typescript/css changes.

Note: The first run will create the python venv & install all node modules. This will take some time.

Starting up
```shell
docker-compose -f docker-compose/docker-compose.dev.yaml up -d
```
Shutting down
```shell
docker-compose -f docker-compose/docker-compose.dev.yaml down
```

#### Docker production setup
Once you are sure of your changes, you can test them out with the production setup. Here the node container only compiles the code into the `duty_board/www/dist` folder, which is then served through the Python FastAPI container.
Now you want to use the FastAPI url at http://localhost:8001.
Note: It might take some time for the `dist` folder to become present and thereby throw an error in the FastAPI before it is ready. Simply, restarting it should be enough.

Note: The first run will create the python venv. This will take some time.

Starting up
```shell
docker-compose -f docker-compose/docker-compose.prod.yaml up -d
```
Shutting down
```shell
docker-compose -f docker-compose/docker-compose.prod.yaml down
```
