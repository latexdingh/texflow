"""CLI commands for hyperlink checking."""
import click
from pathlib import Path
from texflow.hyperlink import extract_hyperlinks


@click.group("hyperlink")
def hyperlink_group() -> None:
    """Inspect hyperlinks in LaTeX files."""


@hyperlink_group.command("list")
@click.argument("file", default="main.tex")
def list_cmd(file: str) -> None:
    """List all hyperlinks found in FILE."""
    result = extract_hyperlinks(Path(file))
    if not result.ok():
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)
    if not result.links:
        click.echo("No hyperlinks found.")
        return
    for item in result.links:
        click.echo(str(item))


@hyperlink_group.command("summary")
@click.argument("file", default="main.tex")
def summary_cmd(file: str) -> None:
    """Print a summary of hyperlinks in FILE."""
    result = extract_hyperlinks(Path(file))
    if not result.ok():
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)
    click.echo(result.summary())
    kinds: dict[str, int] = {}
    for lnk in result.links:
        kinds[lnk.kind] = kinds.get(lnk.kind, 0) + 1
    for kind, count in sorted(kinds.items()):
        click.echo(f"  {kind}: {count}")
