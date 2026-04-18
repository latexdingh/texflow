"""CLI commands for managing source bookmarks."""
import click
from pathlib import Path
from texflow.bookmark import Bookmark, BookmarkStore


@click.group("bookmark", help="Manage named bookmarks in .tex source files.")
def bookmark_group():
    pass


@bookmark_group.command("add")
@click.argument("label")
@click.argument("file")
@click.argument("line", type=int)
@click.option("--note", default="", help="Optional note for this bookmark.")
def add_bookmark(label: str, file: str, line: int, note: str):
    """Add a named bookmark at FILE:LINE."""
    if not Path(file).exists():
        click.echo(f"Error: file '{file}' not found.", err=True)
        raise SystemExit(1)
    store = BookmarkStore()
    bm = Bookmark(label=label, file=file, line=line, note=note)
    store.add(bm)
    click.echo(f"Bookmark '{label}' saved → {file}:{line}")


@bookmark_group.command("list")
def list_bookmarks():
    """List all saved bookmarks."""
    store = BookmarkStore()
    items = store.all()
    if not items:
        click.echo("No bookmarks saved.")
        return
    for bm in items:
        click.echo(str(bm))


@bookmark_group.command("remove")
@click.argument("label")
def remove_bookmark(label: str):
    """Remove a bookmark by label."""
    store = BookmarkStore()
    if store.remove(label):
        click.echo(f"Removed bookmark '{label}'.")
    else:
        click.echo(f"No bookmark named '{label}'.")
        raise SystemExit(1)


@bookmark_group.command("show")
@click.argument("label")
@click.option("--context", default=3, help="Lines of context to show.")
def show_bookmark(label: str, context: int):
    """Show source context around a bookmark."""
    store = BookmarkStore()
    bm = store.get(label)
    if bm is None:
        click.echo(f"No bookmark named '{label}'.")
        raise SystemExit(1)
    path = Path(bm.file)
    if not path.exists():
        click.echo(f"Source file '{bm.file}' not found.")
        raise SystemExit(1)
    lines = path.read_text().splitlines()
    start = max(0, bm.line - context - 1)
    end = min(len(lines), bm.line + context)
    click.echo(f"--- {bm} ---")
    for i, ln in enumerate(lines[start:end], start=start + 1):
        marker = ">>" if i == bm.line else "  "
        click.echo(f"{marker} {i:4}: {ln}")
