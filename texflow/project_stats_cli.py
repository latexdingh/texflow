"""CLI commands for project statistics."""
import click
from pathlib import Path

from texflow.project_stats import gather_stats


@click.group("stats")
def stats_group() -> None:
    """Show aggregate statistics for the current project."""


@stats_group.command("show")
@click.argument("root", default=".", type=click.Path(exists=True))
@click.option("--bib", default=None, type=click.Path(), help="Path to .bib file.")
def show_stats(root: str, bib: str | None) -> None:
    """Display word count, outline depth, and reference health."""
    root_path = Path(root)
    tex_files = list(root_path.rglob("*.tex"))
    if not tex_files:
        click.echo("No .tex files found.")
        return

    # find root file heuristic: prefer main.tex
    main = root_path / "main.tex"
    entry = main if main.exists() else tex_files[0]

    bib_path = Path(bib) if bib else None
    stats = gather_stats(entry, bib_file=bib_path)
    click.echo(stats.summary())


@stats_group.command("words")
@click.argument("root", default=".", type=click.Path(exists=True))
def words_only(root: str) -> None:
    """Print only the total word count for the project."""
    root_path = Path(root)
    tex_files = list(root_path.rglob("*.tex"))
    if not tex_files:
        click.echo("0")
        return
    main = root_path / "main.tex"
    entry = main if main.exists() else tex_files[0]
    stats = gather_stats(entry)
    click.echo(str(stats.total_words))
