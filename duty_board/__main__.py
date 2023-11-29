import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, List

import click
from alembic.config import CommandLine
from click import Context

from duty_board import worker_loop
from duty_board.alchemy import update_duty_calendars
from duty_board.alchemy.session import create_session
from duty_board.plugin.abstract_plugin import AbstractPlugin
from duty_board.plugin.helpers import plugin_fetcher

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M",
)
logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    pass


@cli.command(context_settings={"ignore_unknown_options": True, "help_option_names": []})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def db(args: List[Any]) -> None:
    path_to_alembic_ini = Path(__file__).resolve().parent / "alembic.ini"
    CommandLine(prog="DutyBoard db").main(argv=["-c", str(path_to_alembic_ini), *args])  # type: ignore[no-untyped-call]


@cli.command()
def update_calendars() -> None:
    logger.info("Updating plugin calendars in the database.")
    plugin: AbstractPlugin = plugin_fetcher.get_plugin()
    with create_session() as session:
        update_duty_calendars.sync_duty_calendar_configurations_to_postgres(
            session=session, duty_calendar_configurations=plugin.duty_calendar_configurations
        )
    logger.info("Updated the calendars you want to track.")


@cli.command()
def calendar_refresher() -> None:
    logger.info("Starting the worker to refresh the calendars.")
    plugin: AbstractPlugin = plugin_fetcher.get_plugin()
    worker_loop.enter_calendar_refresher_loop(plugin)


@cli.command()
def duty_officer_refresher() -> None:
    logger.info("Starting the worker to refresh the persons.")
    plugin: AbstractPlugin = plugin_fetcher.get_plugin()
    worker_loop.enter_duty_officer_refresher_loop(plugin)


@cli.command(name="webserver", context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option("--host", default="0.0.0.0", help="The IP address range to listen for.")  # noqa: S104
@click.option("--port", default="80", type=int, help="The port to listen for.")
@click.pass_context
def webserver(ctx: Context, host: str, port: int) -> None:
    command = f"uvicorn duty_board.server:app --host {host} --port {port}"
    if ctx.args:
        command += " " + " ".join(ctx.args)
    logger.info(f"Starting webserver with {command=}")

    cwd = str(Path(__file__).parent.absolute())
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        shell=True,  # noqa: S602
        text=True,
        cwd=cwd,
    ) as process:
        if process.stdout is None:
            raise ValueError("Something went wrong without opening the pipeline.")
        for line in iter(process.stdout.readline, ""):
            logger.info(line)
        return_code = process.wait()
        if return_code is not None and return_code != 0:
            raise ChildProcessError(f"Process ended with problems. {return_code=}.")


if __name__ == "__main__":
    cli()
