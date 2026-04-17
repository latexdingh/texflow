"""CLI commands for managing pinned builds."""
import click
from datetime import datetime, timezone
from pathlib import Path
from texflow.pin import PinStore, PinnedBuild


@click.group("pin")
def pin_group():
    """Pin and compare build snapshots."""


@pin_group.command("add")
@click.argument("label")
@click.argument("pdf", type=click.Path(exists=True))
@click.option("--note", default="", help="Optional note for this pin.")
def add_pin(label: str, pdf: str, note: str):
    """Pin a PDF build under a label."""
    pdf_path = Path(pdf)
    tex_files = list(pdf_path.parent.glob("*.tex"))
    snapshot = ""
    if tex_files:
        snapshot = tex_files[0].read_text(errors="replace")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    store = PinStore()
    store.add(PinnedBuild(label=label, pdf_path=str(pdf_path), tex_snapshot=snapshot, timestamp=ts, note=note))
    click.echo(f"Pinned '{label}' -> {pdf_path}")


@pin_group.command("list")
def list_pins():
    """List all pinned builds."""
    store = PinStore()
    pins = store.all()
    if not pins:
        click.echo("No pins found.")
        return
    for p in pins:
        note_str = f"  # {p.note}" if p.note else ""
        click.echo(f"  [{p.label}]  {p.pdf_path}  ({p.timestamp}){note_str}")


@pin_group.command("remove")
@click.argument("label")
def remove_pin(label: str):
    """Remove a pinned build by label."""
    store = PinStore()
    if store.remove(label):
        click.echo(f"Removed pin '{label}'.")
    else:
        click.echo(f"No pin with label '{label}'.")


@pin_group.command("show")
@click.argument("label")
def show_pin(label: str):
    """Show details of a pinned build."""
    store = PinStore()
    pin = store.get(label)
    if not pin:
        click.echo(f"No pin with label '{label}'.")
        return
    click.echo(f"Label   : {pin.label}")
    click.echo(f"PDF     : {pin.pdf_path}")
    click.echo(f"Time    : {pin.timestamp}")
    click.echo(f"Note    : {pin.note or '(none)'}")
    click.echo(f"Snapshot: {len(pin.tex_snapshot)} chars")
