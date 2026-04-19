"""CLI commands for searching LaTeX project files."""
import click
from pathlib import Path
from texflow.search import search_files
from texflow.multi_file import project_files
from texflow.color_config import color_flag


@click.group("search")
def search_group() -> None:
    """Search across LaTeX source files."""


def _format_match(match, color: bool) -> str:
    """Format a single search match for display."""
    if color:
        return (
            click.style(str(match.file), fg="cyan")
            + ":"
            + click.style(str(match.line_number), fg="yellow")
            + ": "
            + match.line.strip()
        )
    return str(match)


@search_group.command("find")
@click.argument("query")
@click.argument("root", default="main.tex")
@click.option("--regex", is_flag=True, help="Treat QUERY as a regular expression.")
@click.option("--case-sensitive", is_flag=True, help="Case-sensitive search.")
@click.option("--color/--no-color", default=color_flag())
def find_cmd(query: str, root: str, regex: bool, case_sensitive: bool, color: bool) -> None:
    """Search for QUERY in all files reachable from ROOT."""
    root_path = Path(root)
    if not root_path.exists():
        click.echo(f"Root file not found: {root}", err=True)
        raise SystemExit(1)

    try:
        files = project_files(root_path)
    except Exception:
        files = [root_path]

    try:
        result = search_files(files, query, case_sensitive=case_sensitive, regex=regex)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)

    if not result.ok:
        click.echo(result.summary())
        return

    for match in result.matches:
        click.echo(_format_match(match, color))

    click.echo(result.summary())
