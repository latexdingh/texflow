"""CLI commands for macro checking."""
import click
from pathlib import Path
from texflow.macro import check_macros


@click.group("macro")
def macro_group() -> None:
    """Inspect and validate LaTeX macro definitions."""


@macro_group.command("check")
@click.argument("file", type=click.Path(exists=True))
def check_cmd(file: str) -> None:
    """Check macros in FILE for duplicates and unused definitions."""
    result = check_macros(Path(file))
    click.echo(f"Macros defined: {', '.join(result.defined) if result.defined else 'none'}")
    if result.ok():
        click.echo(click.style("No macro issues found.", fg="green"))
    else:
        for issue in result.issues:
            colour = "yellow" if issue.kind == "unused" else "red"
            click.echo(click.style(str(issue), fg=colour))
        click.echo(result.summary())


@macro_group.command("list")
@click.argument("file", type=click.Path(exists=True))
def list_cmd(file: str) -> None:
    """List all macro definitions found in FILE."""
    result = check_macros(Path(file))
    if not result.defined:
        click.echo("No macros defined.")
        return
    for name in result.defined:
        click.echo(f"  \\{name}")
