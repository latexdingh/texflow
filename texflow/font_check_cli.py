"""CLI commands for font checking."""
from __future__ import annotations

from pathlib import Path

import click

from .font_check import check_fonts


@click.group("font")
def font_group() -> None:
    """Inspect and validate font usage in LaTeX files."""


@font_group.command("check")
@click.argument("root", default="main.tex")
def check_cmd(root: str) -> None:
    """Check for font issues in ROOT (default: main.tex)."""
    path = Path(root)
    result = check_fonts(path)

    if result.missing:
        click.echo(f"File not found: {path}")
        raise SystemExit(1)

    if result.fonts_declared:
        click.echo("Declared fonts:")
        for font in result.fonts_declared:
            click.echo(f"  • {font}")
    else:
        click.echo("No explicit font declarations found.")

    if result.issues:
        click.echo(f"\n{len(result.issues)} issue(s):")
        for issue in result.issues:
            click.echo(f"  [{issue.line or '—'}] {issue.message}")
        raise SystemExit(1)
    else:
        click.echo("\n" + result.summary())


@font_group.command("summary")
@click.argument("root", default="main.tex")
def summary_cmd(root: str) -> None:
    """Print a one-line font summary for ROOT."""
    path = Path(root)
    result = check_fonts(path)
    click.echo(result.summary())
    if not result.ok() and not result.missing:
        raise SystemExit(1)
