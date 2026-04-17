"""CLI commands for exporting compiled PDFs."""
from __future__ import annotations

from pathlib import Path

import click

from texflow.export import export_pdf, list_exports


@click.group("export")
def export_group() -> None:
    """Export and manage compiled PDF outputs."""


@export_group.command("run")
@click.argument("source", type=click.Path(exists=True, dir_okay=False))
@click.option("--dest", default="exports", show_default=True, help="Destination directory.")
@click.option("--name", default=None, help="Override output filename stem.")
@click.option("--stamp", is_flag=True, help="Append timestamp to filename.")
def run_export(source: str, dest: str, name: str | None, stamp: bool) -> None:
    """Export SOURCE pdf to DEST directory."""
    result = export_pdf(Path(source), Path(dest), name=name, stamp=stamp)
    if result.success:
        click.echo(click.style(str(result), fg="green"))
    else:
        click.echo(click.style(str(result), fg="red"))
        raise SystemExit(1)


@export_group.command("list")
@click.option("--dest", default="exports", show_default=True, help="Exports directory.")
def list_cmd(dest: str) -> None:
    """List previously exported PDFs."""
    pdfs = list_exports(Path(dest))
    if not pdfs:
        click.echo("No exports found.")
        return
    for pdf in pdfs:
        mtime = pdf.stat().st_mtime
        from datetime import datetime
        ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        click.echo(f"  {ts}  {pdf}")
