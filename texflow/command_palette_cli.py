"""CLI surface for the texflow command palette."""
from __future__ import annotations

import click

from texflow.command_palette import search_palette, _REGISTRY


@click.group("palette")
def palette_group() -> None:
    """Browse and search available texflow commands."""


@palette_group.command("search")
@click.argument("query", default="", required=False)
@click.option(
    "--group", "-g",
    default=None,
    help="Restrict results to a specific command group (e.g. 'check').",
)
def search_cmd(query: str, group: str | None) -> None:
    """Search the command palette with an optional QUERY string.

    Leave QUERY empty to list all commands.

    Examples:

    \b
      texflow palette search
      texflow palette search cite
      texflow palette search --group check
    """
    result = search_palette(query, group_filter=group)
    if not result.ok:
        click.echo(result.summary())
        raise SystemExit(1)
    for entry in result.entries:
        click.echo(str(entry))
    click.echo()
    click.echo(result.summary())


@palette_group.command("list")
@click.option(
    "--group", "-g",
    default=None,
    help="Filter by command group.",
)
def list_cmd(group: str | None) -> None:
    """List all registered commands, optionally filtered by group."""
    groups: dict[str, list] = {}
    for entry in _REGISTRY:
        if group and entry.group.lower() != group.lower():
            continue
        groups.setdefault(entry.group, []).append(entry)

    if not groups:
        click.echo("No commands found.")
        raise SystemExit(1)

    for grp_name, entries in sorted(groups.items()):
        click.echo(f"[{grp_name}]")
        for e in entries:
            line = f"  {e.name:20s}  {e.description}"
            click.echo(line)
        click.echo()
