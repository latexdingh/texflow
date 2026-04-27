"""CLI commands for whitespace checking."""
from __future__ import annotations

from pathlib import Path

import click

from texflow.whitespace import check_whitespace


@click.group("whitespace")
def whitespace_group() -> None:
    """Check LaTeX files for whitespace issues."""


@whitespace_group.command("check")
@click.argument("root", default="main.tex")
@click.option("--no-trailing", is_flag=True, help="Skip trailing-space checks.")
@click.option("--no-tabs", is_flag=True, help="Skip tab checks.")
@click.option("--no-blank", is_flag=True, help="Skip multiple-blank-line checks.")
def check_cmd(
    root: str,
    no_trailing: bool,
    no_tabs: bool,
    no_blank: bool,
) -> None:
    """Report whitespace issues in ROOT (default: main.tex)."""
    result = check_whitespace(
        Path(root),
        check_trailing=not no_trailing,
        check_tabs=not no_tabs,
        check_multiple_blank=not no_blank,
    )
    if result.missing:
        click.echo(f"File not found: {root}")
        raise SystemExit(1)
    if result.ok():
        click.echo("No whitespace issues.")
        return
    for issue in result.issues:
        click.echo(str(issue))
    raise SystemExit(1)


@whitespace_group.command("summary")
@click.argument("root", default="main.tex")
def summary_cmd(root: str) -> None:
    """Print a one-line summary of whitespace issues in ROOT."""
    result = check_whitespace(Path(root))
    click.echo(result.summary())
    if not result.ok():
        raise SystemExit(1)
