"""CLI commands for citation style checking."""
from __future__ import annotations

from pathlib import Path

import click

from texflow.citation_style import check_citation_style


@click.group("citestyle")
def citation_style_group() -> None:
    """Check citation style and usage patterns."""


@citation_style_group.command("check")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--require-tilde/--no-require-tilde", default=True, show_default=True,
              help="Require non-breaking space before \\cite.")
@click.option("--disallow-multi-key", is_flag=True, default=False,
              help="Flag citations with multiple keys.")
def check_cmd(file: str, require_tilde: bool, disallow_multi_key: bool) -> None:
    """Check citation style in FILE."""
    result = check_citation_style(
        Path(file),
        require_tilde=require_tilde,
        disallow_multi_key=disallow_multi_key,
    )
    if result.missing:
        click.echo("File not found.", err=True)
        raise SystemExit(1)

    click.echo(result.summary())
    if result.styles_found:
        click.echo("  Styles used: " + ", ".join(f"\\{s}" for s in result.styles_found))
    for issue in result.issues:
        click.echo(str(issue))

    if not result.ok():
        raise SystemExit(1)


@citation_style_group.command("summary")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def summary_cmd(file: str) -> None:
    """Print a one-line citation style summary for FILE."""
    result = check_citation_style(Path(file))
    click.echo(result.summary())
    if not result.ok():
        raise SystemExit(1)
