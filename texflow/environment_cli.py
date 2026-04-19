"""CLI commands for inspecting the project environment."""
import click
from texflow.environment_summary import gather_environment


@click.group("env")
def env_group() -> None:
    """Inspect the build environment and project metadata."""


@env_group.command("show")
@click.argument("tex_file")
@click.option("--profile", default=None, help="Path to profile JSON file.")
def show_env(tex_file: str, profile: str | None) -> None:
    """Show a full environment summary for TEX_FILE."""
    summary = gather_environment(tex_file, profile)
    click.echo(summary.summary())
    if not summary.ok():
        raise SystemExit(1)


@env_group.command("check")
@click.argument("tex_file")
def check_env_cmd(tex_file: str) -> None:
    """Exit non-zero if required LaTeX tools are missing."""
    summary = gather_environment(tex_file)
    missing = summary.env.missing_required()
    if missing:
        click.echo("Missing required tools:")
        for t in missing:
            click.echo(f"  - {t.name}")
        raise SystemExit(1)
    click.echo("All required tools found.")
