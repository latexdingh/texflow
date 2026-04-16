"""CLI commands for cleaning LaTeX auxiliary files."""
from __future__ import annotations

import click
from pathlib import Path

from texflow.clean import clean_aux_files, find_aux_files
from texflow.color_config import color_flag


@click.group("clean")
def clean_group() -> None:
    """Manage auxiliary LaTeX build files."""


@clean_group.command("run")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--dry-run", is_flag=True, default=False, help="List files without deleting.")
def run_clean(directory: str, dry_run: bool) -> None:
    """Remove auxiliary files from DIRECTORY."""
    use_color = color_flag()
    removed = clean_aux_files(directory, dry_run=dry_run)
    if not removed:
        click.echo("No auxiliary files found.")
        return
    verb = "Would remove" if dry_run else "Removed"
    for path in removed:
        name = click.style(str(path), fg="yellow") if use_color else str(path)
        click.echo(f"  {verb}: {name}")
    count = len(removed)
    summary = click.style(f"{count} file(s)", fg="cyan", bold=True) if use_color else f"{count} file(s)"
    action = "listed" if dry_run else "removed"
    click.echo(f"\n{summary} {action}.")


@clean_group.command("list")
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
def list_aux(directory: str) -> None:
    """List auxiliary files in DIRECTORY without removing them."""
    files = find_aux_files(directory)
    if not files:
        click.echo("No auxiliary files found.")
        return
    for path in files:
        click.echo(f"  {path}")
