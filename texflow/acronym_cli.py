"""CLI commands for acronym checking."""
from __future__ import annotations
from pathlib import Path
import click
from texflow.acronym import check_acronyms


@click.group("acronym")
def acronym_group() -> None:
    """Acronym definition and usage checks."""


@acronym_group.command("check")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def check_cmd(file: str) -> None:
    """Check for undefined or unused acronyms in FILE."""
    result = check_acronyms(Path(file))
    if result.ok():
        click.echo(click.style(result.summary(), fg="green"))
    else:
        for issue in result.issues:
            colour = "red" if issue.kind == "undefined" else "yellow"
            click.echo(click.style(str(issue), fg=colour))
        click.echo(result.summary())
        raise SystemExit(1)


@acronym_group.command("list")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--defined", "mode", flag_value="defined", default=True, help="List defined acronyms")
@click.option("--used", "mode", flag_value="used", help="List used acronyms")
def list_cmd(file: str, mode: str) -> None:
    """List defined or used acronyms in FILE."""
    result = check_acronyms(Path(file))
    items = result.defined if mode == "defined" else result.used
    if not items:
        click.echo(f"No {mode} acronyms found.")
        return
    for key, lineno in sorted(items.items()):
        click.echo(f"  {key:<20} line {lineno}")
