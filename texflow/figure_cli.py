"""CLI commands for figure inventory."""
from __future__ import annotations
from pathlib import Path
import click
from texflow.figure import check_figures


@click.group("figures")
def figure_group() -> None:
    """Figure inventory commands."""


@figure_group.command("check")
@click.argument("tex_file", type=click.Path(exists=True))
@click.option("--base-dir", default=None, help="Directory to resolve figure paths against.")
def check_cmd(tex_file: str, base_dir: str | None) -> None:
    """Check for missing figures referenced in TEX_FILE."""
    path = Path(tex_file)
    base = Path(base_dir) if base_dir else None
    result = check_figures(path, base)
    if not result.figures:
        click.echo("No \\includegraphics references found.")
        return
    click.echo(result.summary())
    for issue in result.issues:
        click.echo(f"  ✗ {issue}")
    if result.ok():
        raise SystemExit(0)
    raise SystemExit(1)


@figure_group.command("list")
@click.argument("tex_file", type=click.Path(exists=True))
@click.option("--base-dir", default=None)
def list_cmd(tex_file: str, base_dir: str | None) -> None:
    """List all figures referenced in TEX_FILE."""
    path = Path(tex_file)
    base = Path(base_dir) if base_dir else None
    result = check_figures(path, base)
    if not result.figures:
        click.echo("No figures found.")
        return
    for fig in result.figures:
        click.echo(f"  {fig}")
