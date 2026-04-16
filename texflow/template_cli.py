"""CLI commands for LaTeX project templates."""
import click
from pathlib import Path
from texflow.template import list_templates, scaffold


@click.group("template")
def template_group():
    """Manage and scaffold LaTeX project templates."""


@template_group.command("list")
def list_cmd():
    """List available templates."""
    templates = list_templates()
    if not templates:
        click.echo("No templates available.")
        return
    click.echo("Available templates:")
    for name in templates:
        click.echo(f"  {name}")


@template_group.command("new")
@click.argument("template")
@click.argument("dest")
@click.option("--name", default=None, help="Project name (defaults to dest folder name).")
def new_cmd(template: str, dest: str, name: str | None):
    """Scaffold a new LaTeX project from a template."""
    dest_path = Path(dest)
    project_name = name or dest_path.name
    result = scaffold(template, dest_path, project_name)
    if result.success:
        click.echo(click.style(f"✔ Project created at {result.path}", fg="green"))
    else:
        click.echo(click.style(f"✘ {result.error}", fg="red"), err=True)
        raise SystemExit(1)
