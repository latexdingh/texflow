"""Compare current tex source against a pinned snapshot."""
from __future__ import annotations
from pathlib import Path
from texflow.pin import PinStore, PinnedBuild
from texflow.diff import compute_diff, DiffResult


def diff_against_pin(label: str, tex_file: Path, store: PinStore | None = None) -> tuple[PinnedBuild | None, DiffResult | None]:
    """Return (pin, diff) comparing tex_file content against pinned snapshot."""
    if store is None:
        store = PinStore()
    pin = store.get(label)
    if pin is None:
        return None, None
    current = tex_file.read_text(errors="replace") if tex_file.exists() else ""
    diff = compute_diff(pin.tex_snapshot, current)
    return pin, diff


def summarise_pin_diff(label: str, tex_file: Path, store: PinStore | None = None) -> str:
    """Return a human-readable one-line summary of changes since pin."""
    pin, diff = diff_against_pin(label, tex_file, store)
    if pin is None:
        return f"No pin with label '{label}'."
    if diff is None or not diff.has_changes:
        return f"No changes since pin '{label}'."
    return (
        f"Since pin '{label}': +{diff.added_count} line(s), "
        f"-{diff.removed_count} line(s)."
    )
