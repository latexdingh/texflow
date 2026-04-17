"""Export compiled PDF to a named destination with optional stamping."""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class ExportResult:
    success: bool
    source: Path
    destination: Path
    message: str = ""

    def __str__(self) -> str:
        if self.success:
            return f"Exported {self.source.name} → {self.destination}"
        return f"Export failed: {self.message}"


def export_pdf(
    source: Path,
    dest_dir: Path,
    name: str | None = None,
    stamp: bool = False,
) -> ExportResult:
    """Copy *source* PDF into *dest_dir*, optionally renaming and stamping."""
    if not source.exists():
        return ExportResult(False, source, dest_dir, f"Source not found: {source}")

    dest_dir.mkdir(parents=True, exist_ok=True)

    stem = name or source.stem
    if stamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = f"{stem}_{ts}"

    destination = dest_dir / f"{stem}.pdf"
    shutil.copy2(source, destination)
    return ExportResult(True, source, destination)


def list_exports(dest_dir: Path) -> list[Path]:
    """Return PDFs in *dest_dir* sorted newest-first by mtime."""
    if not dest_dir.exists():
        return []
    pdfs = list(dest_dir.glob("*.pdf"))
    return sorted(pdfs, key=lambda p: p.stat().st_mtime, reverse=True)
