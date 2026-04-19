"""CLI commands for table checking."""
from __future__ import annotations
from pathlib import Path
import click
from texflow.table_check import check_tables


@click.group("table")
def table_group() -> None:
    """Table structure checks."""


@table_group.command("check")
@click.argument("file", type=click.Path(exists=True))
def check_cmd(file: str) -> None:
    """Check a .tex file for table issues."""
    result = check_tables(Path(file))
    click.echo(f"Tables found: {result.table_count}")
    if result.ok():
        click.echo(click.style("No issues found.", fg="green"))
    else:
        for issue in result.issues:
            click.echo(click.style(str(issue), fg="red"))
        raise SystemExit(1)


@table_group.command("summary")
@click.argument("file", type=click.Path(exists=True))
def summary_cmd(file: str) -> None:
    """Print a one-line summary of table health."""
    result = check_tables(Path(file))
    color = "green" if result.ok() else "yellow"
    click.echo(click.style(result.summary(), fg=color))
