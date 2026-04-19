"""CLI commands for TODO/FIXME scanning."""
from __future__ import annotations
from pathlib import Path
import click
from texflow.todo import scan_todos, scan_todos_multi
from texflow.multi_file import project_files


@click.group("todo")
def todo_group() -> None:
    """Scan LaTeX files for TODO/FIXME comments."""


@todo_group.command("scan")
@click.argument("root", default="main.tex")
@click.option("--kind", default=None, help="Filter by kind: TODO, FIXME, NOTE, etc.")
@click.option("--all-files", is_flag=True, default=False, help="Scan all included files.")
def scan_cmd(root: str, kind: str | None, all_files: bool) -> None:
    """List TODO comments in ROOT (default: main.tex)."""
    root_path = Path(root)
    if all_files:
        files = project_files(root_path)
        result = scan_todos_multi(files)
    else:
        result = scan_todos(root_path)

    items = result.items if kind is None else result.by_kind(kind)

    if not items:
        click.echo("No TODO items found.")
        return
    for item in items:
        click.echo(str(item))


@todo_group.command("summary")
@click.argument("root", default="main.tex")
@click.option("--all-files", is_flag=True, default=False)
def summary_cmd(root: str, all_files: bool) -> None:
    """Print a summary count of TODO items."""
    root_path = Path(root)
    if all_files:
        files = project_files(root_path)
        result = scan_todos_multi(files)
    else:
        result = scan_todos(root_path)
    click.echo(result.summary())
