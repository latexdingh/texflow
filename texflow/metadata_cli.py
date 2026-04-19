"""CLI commands for document metadata inspection."""
from __future__ import annotations
from pathlib import Path
import click
from texflow.metadata import extract_metadata


@click.group("metadata")
def metadata_group() -> None:
    """Inspect LaTeX document metadata."""


@metadata_group.command("show")
@click.argument("tex_file", type=click.Path(exists=True))
def show_metadata(tex_file: str) -> None:
    """Show title, author, date, class and packages."""
    meta = extract_metadata(Path(tex_file))
    if not meta.ok() and not meta.document_class and not meta.packages:
        click.echo("No metadata found.")
        return
    click.echo(meta.summary())


@metadata_group.command("title")
@click.argument("tex_file", type=click.Path(exists=True))
def show_title(tex_file: str) -> None:
    """Print only the document title."""
    meta = extract_metadata(Path(tex_file))
    if meta.title:
        click.echo(meta.title)
    else:
        click.echo("No title found.", err=True)
        raise SystemExit(1)


@metadata_group.command("packages")
@click.argument("tex_file", type=click.Path(exists=True))
@click.option("--count", is_flag=True, help="Print only the package count.")
def list_packages(tex_file: str, count: bool) -> None:
    """List all \\usepackage declarations."""
    meta = extract_metadata(Path(tex_file))
    if count:
        click.echo(str(len(meta.packages)))
        return
    if not meta.packages:
        click.echo("No packages found.")
        return
    for pkg in meta.packages:
        click.echo(pkg)
