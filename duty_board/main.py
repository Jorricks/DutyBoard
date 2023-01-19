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


@cli.command(name="webserver", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.option("--host", default="0.0.0.0", help="The IP address range to listen for.")
@click.option("--port", default="80", type=int, help="The port to listen for.")
@click.pass_context
def webserver(ctx, host: str, port: int):
    command = f"uvicorn duty_board.server:app --host {host} --port {port}"
    if ctx.args:
        command += " " + " ".join(ctx.args)
    logger.info(f"Starting webserver with {command=}")

    cwd = str(Path(__file__).parent.absolute())
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
