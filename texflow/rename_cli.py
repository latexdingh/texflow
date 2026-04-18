"""CLI commands for renaming .tex files with reference updates."""
from __future__ import annotations

from pathlib import Path

import click

from texflow.rename import rename_tex_file


@click.group("rename")
def rename_group() -> None:
    """Rename .tex files and update cross-file references."""


@rename_group.command("file")
@click.argument("source", type=click.Path(exists=True, dir_okay=False))
@click.argument("new_name")
@click.option(
    "--root",
    default=None,
    type=click.Path(exists=True, file_okay=False),
    help="Project root to search for references (default: source directory).",
)
@click.option("--dry-run", is_flag=True, help="Preview changes without modifying files.")
def rename_file(source: str, new_name: str, root: str | None, dry_run: bool) -> None:
    """Rename SOURCE to NEW_NAME and update \\input/\\include references."""
    old_path = Path(source)
    project_root = Path(root) if root else None

    if dry_run:
        new_path = old_path.with_name(
            new_name if new_name.endswith(".tex") else new_name + ".tex"
        )
        click.echo(f"[dry-run] Would rename: {old_path} -> {new_path}")
        r = project_root or old_path.parent
        refs = [
            p for p in r.rglob("*.tex")
            if p != old_path and old_path.stem in p.read_text(encoding="utf-8", errors="ignore")
        ]
        if refs:
            click.echo("[dry-run] Would update references in:")
            for ref in refs:
                click.echo(f"  {ref}")
        else:
            click.echo("[dry-run] No references found.")
        return

    result = rename_tex_file(old_path, new_name, project_root)
    if not result.ok:
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)
    click.echo(str(result))
