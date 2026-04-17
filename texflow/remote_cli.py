"""CLI commands for managing remote push targets."""
import click
from pathlib import Path

from texflow.remote import RemoteTarget, push_to_target
from texflow.remote_store import RemoteStore
from texflow.compiler import find_output_pdf


@click.group("remote")
def remote_group():
    """Manage remote push targets."""


@remote_group.command("add")
@click.argument("name")
@click.argument("path")
@click.option("--kind", default="directory", show_default=True)
@click.option("--auto-push", is_flag=True, default=False)
def add_remote(name: str, path: str, kind: str, auto_push: bool):
    """Register a new remote target."""
    store = RemoteStore()
    target = RemoteTarget(name=name, kind=kind, path=path, auto_push=auto_push)
    if store.add(target):
        click.echo(f"Added remote '{name}' ({kind}) -> {path}")
    else:
        click.echo(f"Remote '{name}' already exists.", err=True)
        raise SystemExit(1)


@remote_group.command("list")
def list_remotes():
    """List registered remote targets."""
    targets = RemoteStore().all()
    if not targets:
        click.echo("No remotes configured.")
        return
    for t in targets:
        auto = " [auto]" if t.auto_push else ""
        click.echo(f"  {t.name}  {t.kind}  {t.path}{auto}")


@remote_group.command("remove")
@click.argument("name")
def remove_remote(name: str):
    """Remove a remote target."""
    if RemoteStore().remove(name):
        click.echo(f"Removed remote '{name}'.")
    else:
        click.echo(f"Remote '{name}' not found.", err=True)
        raise SystemExit(1)


@remote_group.command("push")
@click.argument("name")
@click.option("--pdf", "pdf_path", default=None, help="PDF to push")
def push_remote(name: str, pdf_path: str | None):
    """Push the compiled PDF to a remote target."""
    store = RemoteStore()
    target = store.get(name)
    if not target:
        click.echo(f"Remote '{name}' not found.", err=True)
        raise SystemExit(1)
    pdf = Path(pdf_path) if pdf_path else find_output_pdf(Path("."))
    if pdf is None:
        click.echo("No PDF found to push.", err=True)
        raise SystemExit(1)
    result = push_to_target(pdf, target)
    click.echo(str(result))
    if not result.success:
        raise SystemExit(1)
