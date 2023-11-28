import logging
import os
import sys

os.environ["DUTY_BOARD_SECRET_KEY"] = "abcdef"
os.environ["SQL_ALCHEMY_CONNECTION"] = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M",
)
