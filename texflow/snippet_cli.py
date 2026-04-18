"""CLI commands for snippet management."""
from __future__ import annotations
import click
from pathlib import Path
from texflow.snippet import extract_snippets
from texflow.snippet_store import SnippetStore


@click.group(name="snippet")
def snippet_group() -> None:
    """Manage named LaTeX snippets."""


@snippet_group.command("extract")
@click.argument("tex_file", type=click.Path(exists=True))
@click.option("--save", is_flag=True, help="Persist snippets to store")
def extract_cmd(tex_file: str, save: bool) -> None:
    """Extract snippets from TEX_FILE."""
    result = extract_snippets(Path(tex_file))
    if not result.ok:
        for e in result.errors:
            click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if not result.snippets:
        click.echo("No snippets found.")
        return
    store = SnippetStore() if save else None
    for s in result.snippets:
        click.echo(str(s))
        if store:
            store.save(s)
    if save:
        click.echo(f"Saved {len(result.snippets)} snippet(s).")


@snippet_group.command("list")
def list_cmd() -> None:
    """List all saved snippets."""
    snippets = SnippetStore().all()
    if not snippets:
        click.echo("No snippets saved.")
        return
    for s in snippets:
        click.echo(f"  {s.label}  ({s.source_file}:{s.start_line})")


@snippet_group.command("show")
@click.argument("label")
def show_cmd(label: str) -> None:
    """Show a saved snippet by LABEL."""
    s = SnippetStore().get(label)
    if s is None:
        click.echo(f"Snippet '{label}' not found.", err=True)
        raise SystemExit(1)
    click.echo(str(s))


@snippet_group.command("remove")
@click.argument("label")
def remove_cmd(label: str) -> None:
    """Remove a saved snippet by LABEL."""
    removed = SnippetStore().remove(label)
    if removed:
        click.echo(f"Removed snippet '{label}'.")
    else:
        click.echo(f"Snippet '{label}' not found.", err=True)
        raise SystemExit(1)
