"""CLI commands for environment balance checking."""
from __future__ import annotations

from pathlib import Path

import click

from texflow.environment_check import check_environments


@click.group("envcheck")
def env_check_group() -> None:
    """Check LaTeX environment begin/end balance."""


@env_check_group.command("check")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def check_cmd(file: str) -> None:
    """Check FILE for mismatched environments."""
    result = check_environments(Path(file))
    if result.missing:
        click.echo("Error: file not found.", err=True)
        raise SystemExit(1)
    if result.ok():
        click.echo(click.style(result.summary(), fg="green"))
    else:
        click.echo(click.style(result.summary(), fg="red"))
        for issue in result.issues:
            click.echo(f"  {issue}")
        raise SystemExit(1)


@env_check_group.command("summary")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def summary_cmd(file: str) -> None:
    """Print a one-line summary of environment balance for FILE."""
    result = check_environments(Path(file))
    color = "green" if result.ok() else "red"
    click.echo(click.style(result.summary(), fg=color))
