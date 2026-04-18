"""CLI commands for inspecting project file dependencies."""
import click
from pathlib import Path

from texflow.dependency import build_graph


@click.group(name="deps", help="Inspect LaTeX file dependencies.")
def dependency_group() -> None:
    pass


@dependency_group.command(name="tree")
@click.argument("root", default="main.tex", type=click.Path(exists=True))
def show_tree(root: str) -> None:
    """Print the dependency tree for ROOT (default: main.tex)."""
    path = Path(root)
    graph = build_graph(path)
    if graph.is_empty():
        click.echo("No dependencies found.")
        return
    click.echo(graph.summary())


@dependency_group.command(name="dependents")
@click.argument("file", type=click.Path(exists=True))
@click.option("--root", default="main.tex", show_default=True, help="Project root file.")
def show_dependents(file: str, root: str) -> None:
    """List files that include FILE."""
    root_path = Path(root)
    if not root_path.exists():
        click.echo(f"Root file '{root}' not found.", err=True)
        raise SystemExit(1)
    graph = build_graph(root_path)
    deps = graph.dependents_of(Path(file))
    if not deps:
        click.echo(f"No files depend on '{file}'.")
    else:
        click.echo(f"Files that include '{Path(file).name}':")
        for p in deps:
            click.echo(f"  {p}")
