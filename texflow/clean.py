"""Utilities for cleaning LaTeX auxiliary files."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

AUX_EXTENSIONS = [
    ".aux", ".log", ".out", ".toc", ".lof", ".lot",
    ".fls", ".fdb_latexmk", ".synctex.gz", ".bbl",
    ".blg", ".nav", ".snm", ".vrb",
]


def find_aux_files(directory: str | Path) -> List[Path]:
    """Return all auxiliary files found in *directory* (non-recursive)."""
    root = Path(directory)
    found: List[Path] = []
    for ext in AUX_EXTENSIONS:
        found.extend(root.glob(f"*{ext}"))
    return sorted(found)


def clean_aux_files(directory: str | Path, dry_run: bool = False) -> List[Path]:
    """Delete auxiliary files in *directory*.

    Returns the list of files that were (or would be) removed.
    If *dry_run* is True the files are not actually deleted.
    """
    targets = find_aux_files(directory)
    if not dry_run:
        for path in targets:
            try:
                path.unlink()
            except OSError:
                pass
    return targets
