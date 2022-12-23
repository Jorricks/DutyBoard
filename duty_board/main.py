import logging
import subprocess
import sys
from pathlib import Path

import click

from duty_board import worker_loop

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M",
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def worker():
    logger.info("Starting the worker")
    worker_loop.enter_loop()


@cli.command()
@click.option("--host", default="0.0.0.0", help="The IP address range to listen for.")
@click.option("--port", default="80", type=int, help="The port to listen for.")
@click.option("--reload", is_flag=True, type=bool, help="Auto reload when changes are made to the source repository.")
def webserver(host: str, port: int, reload: bool):
    logger.info("Starting the webserver")
    command = f"uvicorn duty_board.server:app --host {host} --port {port}"
    if reload:
        command += " --reload"

    cwd = str(Path(__file__).absolute())
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, shell=True, text=True, cwd=cwd
    ) as process:
        if process.stdout is None:
            raise ValueError("Something went wrong without opening the pipeline.")
        for line in iter(process.stdout.readline, ""):
            print(line, end="")
        return_code = process.wait()
        if return_code is not None and return_code != 0:
            raise ChildProcessError(f"Process ended with problems. {return_code=}.")


if __name__ == "__main__":
    cli()
