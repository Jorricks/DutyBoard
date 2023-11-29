FROM registry.hub.docker.com/library/python:3.10-slim

WORKDIR /usr/src/app

COPY . .

RUN pip3 install --no-cache-dir .

CMD ["DutyBoard"]
