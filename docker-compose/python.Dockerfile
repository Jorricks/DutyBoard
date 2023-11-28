FROM registry.hub.docker.com/library/python:3.10-slim

WORKDIR /code

COPY pyproject.toml .
RUN mkdir duty_board
RUN echo "__version__ = '0.0.1'" > duty_board/__init__.py

RUN pip3 install --no-cache-dir --upgrade pip && pip3 install --no-cache-dir -e ".[ldap]"
