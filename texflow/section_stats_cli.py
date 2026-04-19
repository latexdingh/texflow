"""CLI commands for per-section statistics."""
from pathlib import Path
import click
from texflow.section_stats import gather_section_stats


@click.group("secstats")
def section_stats_group() -> None:
    """Per-section word and equation statistics."""


@section_stats_group.command("show")
@click.argument("tex_file", type=click.Path(exists=True))
def show_cmd(tex_file: str) -> None:
    """Show per-section stats for TEX_FILE."""
    result = gather_section_stats(Path(tex_file))
    if not result.ok():
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)
    if not result.sections:
        click.echo("No sections found.")
        return
    for s in result.sections:
        click.echo(str(s))


@section_stats_group.command("summary")
@click.argument("tex_file", type=click.Path(exists=True))
def summary_cmd(tex_file: str) -> None:
    """Print a one-line summary of section stats for TEX_FILE."""
    result = gather_section_stats(Path(tex_file))
    click.echo(result.summary())
