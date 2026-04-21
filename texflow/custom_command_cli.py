"""custom_command_cli.py – CLI group for user-defined build commands."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from texflow.custom_command import CommandStore, CustomCommand, run_command


@click.group("cmd", help="Manage and run custom build commands.")
def command_group() -> None:  # pragma: no cover
    pass


@command_group.command("add")
@click.argument("label")
@click.argument("command")
@click.option("--desc", default="", help="Short description of the command.")
@click.option("--store", default=".texflow_commands.json", show_default=True)
def add_command(label: str, command: str, desc: str, store: str) -> None:
    """Register a new custom command under LABEL."""
    s = CommandStore(Path(store))
    s.add(CustomCommand(label=label, command=command, description=desc))
    click.echo(f"Saved command '{label}'.")


@command_group.command("list")
@click.option("--store", default=".texflow_commands.json", show_default=True)
def list_commands(store: str) -> None:
    """List all registered custom commands."""
    s = CommandStore(Path(store))
    cmds = s.all()
    if not cmds:
        click.echo("No custom commands defined.")
        return
    for c in cmds:
        click.echo(str(c))


@command_group.command("remove")
@click.argument("label")
@click.option("--store", default=".texflow_commands.json", show_default=True)
def remove_command(label: str, store: str) -> None:
    """Remove a custom command by LABEL."""
    s = CommandStore(Path(store))
    if s.remove(label):
        click.echo(f"Removed command '{label}'.")
    else:
        click.echo(f"No command with label '{label}'.")
        sys.exit(1)


@command_group.command("run")
@click.argument("label")
@click.option("--store", default=".texflow_commands.json", show_default=True)
@click.option("--cwd", default=None, help="Working directory for the command.")
def run_cmd(label: str, store: str, cwd: str | None) -> None:
    """Execute the custom command identified by LABEL."""
    s = CommandStore(Path(store))
    cmd = s.get(label)
    if cmd is None:
        click.echo(f"Unknown command '{label}'.")
        sys.exit(1)
    result = run_command(cmd, cwd=Path(cwd) if cwd else None)
    if result.stdout:
        click.echo(result.stdout, nl=False)
    if result.stderr:
        click.echo(result.stderr, nl=False, err=True)
    if not result.ok:
        sys.exit(result.returncode)
