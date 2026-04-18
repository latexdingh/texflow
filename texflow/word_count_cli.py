"""CLI commands for word count."""
from __future__ import annotations
from pathlib import Path
import click
from texflow.word_count import count_words


@click.group('wordcount')
def wordcount_group() -> None:
    """Word count tools for LaTeX files."""


@wordcount_group.command('count')
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--body-only', is_flag=True, default=False, help='Show body word count only.')
@click.option('--total', is_flag=True, default=False, help='Print grand total at the end.')
def count_cmd(files: tuple[str, ...], body_only: bool, total: bool) -> None:
    """Count words in one or more .tex FILES."""
    grand_total = 0
    for f in files:
        path = Path(f)
        if path.suffix != '.tex':
            click.echo(f"Skipping {f}: not a .tex file", err=True)
            continue
        result = count_words(path)
        words = result.body_words if body_only else result.total_words
        grand_total += words
        label = 'body words' if body_only else 'words'
        click.echo(f"{path.name}: {words} {label}  (math envs: {result.math_envs})")
    if total and len(files) > 1:
        click.echo(f"---\nTotal: {grand_total}")


@wordcount_group.command('summary')
@click.argument('file', type=click.Path(exists=True))
def summary_cmd(file: str) -> None:
    """Print a full summary for a single .tex FILE."""
    path = Path(file)
    if path.suffix != '.tex':
        click.echo(f"Error: {file} is not a .tex file", err=True)
        raise SystemExit(1)
    result = count_words(path)
    click.echo(result.summary())
