# React front-end with FastAPI back-end

It is highly encouraged you use the docker-compose setup for local development.

## Adding a dependency using the docker-compose.dev setup.

```shell
(venv) ➜  DutyBoard git:(main) ✗ docker ps
CONTAINER ID   IMAGE                                                  COMMAND                  CREATED        STATUS        PORTS                    NAMES
dc14c6d027b1   registry.hub.docker.com/library/node:18-slim           "docker-entrypoint.s…"   13 hours ago   Up 13 hours   0.0.0.0:8080->8080/tcp   duty_frontend
ffd5949d1da1   registry.hub.docker.com/library/python:3.10-slim       "/bin/bash -c 'pytho…"   13 hours ago   Up 13 hours   0.0.0.0:8000->8000/tcp   duty_backend
32dfb3484317   registry.hub.docker.com/library/postgres:13.3-alpine   "docker-entrypoint.s…"   13 hours ago   Up 13 hours   0.0.0.0:5432->5432/tcp   duty_database
(venv) ➜  DutyBoard git:(main) ✗ docker exec -it duty_frontend /bin/bash
root@dc14c6d027b1:/code# npm install --save-dev html-webpack-plugin

up to date, audited 995 packages in 2s

155 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

## Analyzing the size of the packages you drag into the build

1. In webpack.config.js, uncomment the `BundleAnalyzerPlugin`.
2. Restart docker-compose with `docker-compose -f docker-compose.dev.yaml up -d`.
3. Wait for the dist folder to be filled with `report.html`
4. Open the `report.html` in your favorite browser.

## Improvement ideas
- [ ] (Optional) Ability to add heads up notification.
- [ ] (Optional) Create loader icon on page load.
