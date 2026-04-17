"""CLI commands for managing build profiles."""
from __future__ import annotations
import click
from texflow.profile import BuildProfile, load_profile, save_profile, DEFAULT_PROFILE_FILE


@click.group("profile")
def profile_group():
    """Manage texflow build profiles."""


@profile_group.command("show")
@click.option("--file", default=DEFAULT_PROFILE_FILE, show_default=True)
def show_profile(file: str):
    """Display the current build profile."""
    profile = load_profile(file)
    click.echo(f"Engine        : {profile.engine}")
    click.echo(f"Output dir    : {profile.output_dir}")
    click.echo(f"Extra args    : {' '.join(profile.extra_args) or '(none)'}")
    click.echo(f"Watch exts    : {', '.join(profile.watch_extensions)}")
    click.echo(f"Max runs      : {profile.max_runs}")


@profile_group.command("init")
@click.option("--engine", default="pdflatex", show_default=True)
@click.option("--output-dir", default=".", show_default=True)
@click.option("--max-runs", default=2, show_default=True)
@click.option("--file", default=DEFAULT_PROFILE_FILE, show_default=True)
def init_profile(engine: str, output_dir: str, max_runs: int, file: str):
    """Create or overwrite a build profile."""
    profile = BuildProfile(engine=engine, output_dir=output_dir, max_runs=max_runs)
    save_profile(profile, file)
    click.echo(f"Initialized profile with engine={engine}, output_dir={output_dir}, max_runs={max_runs}")


@profile_group.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--file", default=DEFAULT_PROFILE_FILE, show_default=True)
def set_profile(key: str, value: str, file: str):
    """Set a single profile field."""
    profile = load_profile(file)
    if key == "engine":
        profile.engine = value
    elif key == "output_dir":
        profile.output_dir = value
    elif key == "max_runs":
        try:
            profile.max_runs = int(value)
        except ValueError:
            raise click.ClickException(f"max_runs must be an integer, got: {value!r}")
    elif key == "extra_args":
        profile.extra_args = value.split()
    elif key == "watch_extensions":
        profile.watch_extensions = [ext.strip() for ext in value.split(",")]
    else:
        raise click.ClickException(f"Unknown profile key: {key}")
    save_profile(profile, file)
    click.echo(f"Set {key} = {value}")
