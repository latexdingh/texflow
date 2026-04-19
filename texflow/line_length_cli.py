"""CLI commands for line-length checking."""
from pathlib import Path
import click
from texflow.line_length import check_line_length, DEFAULT_MAX_LENGTH


@click.group("linelen")
def line_length_group() -> None:
    """Check line lengths in LaTeX source files."""


@line_length_group.command("check")
@click.argument("root", default="main.tex")
@click.option(
    "--max", "max_length", default=DEFAULT_MAX_LENGTH, show_default=True,
    help="Maximum allowed line length.",
)
@click.option(
    "--include-comments", is_flag=True, default=False,
    help="Also check comment-only lines.",
)
def check_cmd(root: str, max_length: int, include_comments: bool) -> None:
    """Report lines exceeding the length limit."""
    result = check_line_length(
        Path(root),
        max_length=max_length,
        skip_comments=not include_comments,
    )
    if result.error:
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)
    if result.ok():
        click.echo(result.summary())
        return
    for issue in result.issues:
        click.echo(str(issue))
    click.echo(result.summary())
    raise SystemExit(1)


@line_length_group.command("summary")
@click.argument("root", default="main.tex")
@click.option("--max", "max_length", default=DEFAULT_MAX_LENGTH, show_default=True)
def summary_cmd(root: str, max_length: int) -> None:
    """Print a one-line summary of line-length issues."""
    result = check_line_length(Path(root), max_length=max_length)
    click.echo(result.summary())
    if not result.ok() and not result.error:
        raise SystemExit(1)
