"""CLI commands for symbol checking."""
from __future__ import annotations

from pathlib import Path

import click

from texflow.symbol_check import check_symbols


@click.group("symbol")
def symbol_group() -> None:
    """Check LaTeX files for common symbol usage issues."""


@symbol_group.command("check")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--quiet", "-q", is_flag=True, help="Only print issues, no summary.")
def check_cmd(file: str, quiet: bool) -> None:
    """Check FILE for symbol issues."""
    result = check_symbols(Path(file))

    if result.error:
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)

    for issue in result.issues:
        click.echo(str(issue))

    if not quiet:
        click.echo(result.summary())

    if not result.ok():
        raise SystemExit(1)


@symbol_group.command("summary")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def summary_cmd(file: str) -> None:
    """Print a one-line summary of symbol issues in FILE."""
    result = check_symbols(Path(file))
    if result.error:
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)
    click.echo(result.summary())
