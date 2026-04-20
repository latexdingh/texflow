"""CLI commands for word-wrap checking."""
import click
from pathlib import Path
from texflow.word_wrap import check_word_wrap


@click.group("wrap")
def wrap_group() -> None:
    """Check and report long-line wrap issues in LaTeX files."""


@wrap_group.command("check")
@click.argument("file", type=click.Path(exists=True))
@click.option("--max-len", default=100, show_default=True, help="Max line length.")
def check_cmd(file: str, max_len: int) -> None:
    """Report lines exceeding MAX_LEN characters."""
    result = check_word_wrap(Path(file), max_len=max_len)
    if result.error:
        click.echo(result.error, err=True)
        raise SystemExit(1)
    if result.ok():
        click.echo(result.summary())
        return
    for issue in result.issues:
        click.echo(str(issue))
    raise SystemExit(1)


@wrap_group.command("summary")
@click.argument("file", type=click.Path(exists=True))
@click.option("--max-len", default=100, show_default=True)
def summary_cmd(file: str, max_len: int) -> None:
    """Print a one-line summary of wrap issues."""
    result = check_word_wrap(Path(file), max_len=max_len)
    click.echo(result.summary())
    if not result.ok():
        raise SystemExit(1)
