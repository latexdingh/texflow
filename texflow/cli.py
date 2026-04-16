"""CLI entry point for texflow."""

import signal
import sys
from pathlib import Path

import click

from texflow.watcher import LatexWatcher


def _build_callback(verbose: bool) -> callable:
    def on_change(path: Path) -> None:
        click.echo(f"[texflow] Change detected: {path}")
        # Future: trigger compilation pipeline here
        if verbose:
            click.echo(f"[texflow] Full path: {path.resolve()}")
    return on_change


@click.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--debounce", default=0.5, show_default=True, help="Debounce delay in seconds.")
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output.")
def watch(directory: Path, debounce: float, verbose: bool) -> None:
    """Watch DIRECTORY for .tex file changes and hot-reload PDF output."""
    click.echo(f"[texflow] Watching {directory.resolve()} for .tex changes...")
    callback = _build_callback(verbose)
    watcher = LatexWatcher(directory, callback, debounce_seconds=debounce)

    def _shutdown(sig, frame):
        click.echo("\n[texflow] Stopping watcher.")
        watcher.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    watcher.start()
    signal.pause()


def main() -> None:
    watch()


if __name__ == "__main__":
    main()
