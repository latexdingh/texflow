"""CLI commands for viewing build history."""
from __future__ import annotations

from pathlib import Path

import click

from texflow.log_history import load_history


@click.group(name="history")
def history_group() -> None:
    """View build history for the current project."""


@history_group.command("show")
@click.option("--last", default=10, show_default=True, help="Number of entries to show.")
@click.option("--dir", "directory", default=".", show_default=True, help="Project directory.")
def show_history(last: int, directory: str) -> None:
    """Display recent build records."""
    history = load_history(Path(directory))
    records = history.last(last)
    if not records:
        click.echo("No build history found.")
        return
    click.echo(f"{'Time':<22} {'Status':<10} {'Errors':<8} {'Warnings':<10} {'Duration':>10}")
    click.echo("-" * 62)
    for r in reversed(records):
        status = click.style("OK", fg="green") if r.success else click.style("FAIL", fg="red")
        dur = f"{r.duration_ms:.0f}ms" if r.duration_ms is not None else "—"
        click.echo(f"{r.formatted_time():<22} {status:<10} {r.errors:<8} {r.warnings:<10} {dur:>10}")


@history_group.command("stats")
@click.option("--dir", "directory", default=".", show_default=True, help="Project directory.")
def show_stats(directory: str) -> None:
    """Show aggregate build statistics."""
    history = load_history(Path(directory))
    total = len(history.records)
    if total == 0:
        click.echo("No build history found.")
        return
    rate = history.success_rate() * 100
    avg_dur = (
        sum(r.duration_ms for r in history.records if r.duration_ms) /
        max(1, sum(1 for r in history.records if r.duration_ms))
    )
    click.echo(f"Total builds : {total}")
    click.echo(f"Success rate : {rate:.1f}%")
    click.echo(f"Avg duration : {avg_dur:.0f}ms")
