#!/usr/bin/env -S uv run
"""withenv - run a command with environment variables loaded from a .env file.

Examples:
    withenv .env python -c 'import os; print(os.getenv("FOO"))'

Notes:
    - Arguments after ENVFILE are forwarded to the wrapped command.
    - This wrapper intentionally does not provide a ``--help`` option so that
      ``--help`` is forwarded to the wrapped command.
    - This wrapper is intetionally named withenv without a .py extension so that
      it doesn't with agent rules that specify that agents should always prefix
      python commands with uv (the shebang handles this for us).
"""

import os
from collections.abc import Mapping
from pathlib import Path
from typing import NoReturn, cast

import click
from dotenv import dotenv_values


def _exec_with_overrides(command: tuple[str, ...], overrides: Mapping[str, str | None]) -> NoReturn:
    env: dict[str, str] = dict(os.environ)
    env.update({k: v for k, v in overrides.items() if v is not None})
    os.execvpe(command[0], list(command), env)  # noqa: S606


@click.command(
    name="withenv",
    add_help_option=False,
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
    },
)
@click.argument(
    "envfile",
    type=click.Path(
        exists=True,
        dir_okay=False,
        file_okay=True,
        readable=True,
        path_type=Path,
    ),
)
@click.argument("command", nargs=-1, type=click.UNPROCESSED)
def cli(envfile: Path, command: tuple[str, ...]) -> None:
    """Run COMMAND with environment loaded from ENVFILE."""
    if not command:
        raise click.UsageError("Missing COMMAND to run.")

    # dotenv_values returns a dict WITHOUT touching os.environ.
    overrides = cast(Mapping[str, str | None], dotenv_values(str(envfile)))

    _exec_with_overrides(command, overrides)


if __name__ == "__main__":
    cli()