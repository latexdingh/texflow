"""CLI commands for the cross-reference map feature."""
import click
from pathlib import Path
from texflow.cross_ref import build_cross_ref_map, CrossRefMap
from texflow.multi_file import project_files


@click.group("xref")
def cross_ref_group() -> None:
    """Cross-reference map commands."""


@cross_ref_group.command("list")
@click.argument("root", default="main.tex")
def list_labels(root: str) -> None:
    """List all \\label definitions in the project."""
    root_path = Path(root)
    if not root_path.exists():
        click.echo(f"File not found: {root}", err=True)
        raise SystemExit(1)
    files = project_files(root_path)
    xmap = build_cross_ref_map(files)
    if not xmap.ok():
        click.echo("No labels found.")
        return
    for entry in xmap.entries:
        click.echo(str(entry))


@cross_ref_group.command("find")
@click.argument("label")
@click.argument("root", default="main.tex")
def find_label(label: str, root: str) -> None:
    """Find where a specific label is defined."""
    root_path = Path(root)
    if not root_path.exists():
        click.echo(f"File not found: {root}", err=True)
        raise SystemExit(1)
    files = project_files(root_path)
    xmap = build_cross_ref_map(files)
    entry = xmap.get(label)
    if entry is None:
        click.echo(f"Label '{label}' not found.")
        raise SystemExit(1)
    click.echo(str(entry))


@cross_ref_group.command("summary")
@click.argument("root", default="main.tex")
def summary_cmd(root: str) -> None:
    """Print a summary of the cross-reference map."""
    root_path = Path(root)
    if not root_path.exists():
        click.echo(f"File not found: {root}", err=True)
        raise SystemExit(1)
    files = project_files(root_path)
    xmap = build_cross_ref_map(files)
    click.echo(xmap.summary())
