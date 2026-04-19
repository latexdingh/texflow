"""CLI commands for abstract extraction."""
from __future__ import annotations

from pathlib import Path

import click

from texflow.abstract import extract_abstract


@click.group("abstract")
def abstract_group() -> None:
    """Inspect the abstract of a LaTeX document."""


@abstract_group.command("show")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def show_abstract(file: str) -> None:
    """Print the extracted abstract text."""
    result = extract_abstract(Path(file))
    if not result.ok:
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)
    click.echo(result.text)


@abstract_group.command("info")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def info_abstract(file: str) -> None:
    """Show word and character counts for the abstract."""
    result = extract_abstract(Path(file))
    if not result.ok:
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)
    click.echo(result.summary())
    click.echo(f"  Words : {result.word_count}")
    click.echo(f"  Chars : {result.char_count}")
