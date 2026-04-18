"""CLI commands for focus mode."""
from __future__ import annotations
from pathlib import Path
import click
from texflow.focus import find_focus
from texflow.color_config import color_flag


@click.group("focus")
def focus_group() -> None:
    """Inspect a specific section of a LaTeX file."""


@focus_group.command("show")
@click.argument("tex_file", type=click.Path(exists=True, path_type=Path))
@click.argument("label")
@color_flag
def show_focus(tex_file: Path, label: str, color: bool) -> None:
    """Show the content of the section matching LABEL."""
    result = find_focus(tex_file, label)
    if not result.ok():
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)

    r = result.region
    assert r is not None
    header = f"Section: {r.label}  ({r.line_count()} lines, {r.start_line}–{r.end_line})"
    if color:
        click.echo(click.style(header, fg="cyan", bold=True))
    else:
        click.echo(header)
    click.echo(r.content)


@focus_group.command("info")
@click.argument("tex_file", type=click.Path(exists=True, path_type=Path))
@click.argument("label")
def info_focus(tex_file: Path, label: str) -> None:
    """Print metadata about the section matching LABEL."""
    result = find_focus(tex_file, label)
    if not result.ok():
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)
    click.echo(str(result.region))
