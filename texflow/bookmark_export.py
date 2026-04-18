"""Export bookmarks to plain text or JSON for sharing."""
from __future__ import annotations
import json
from pathlib import Path
from texflow.bookmark import Bookmark, BookmarkStore


def export_bookmarks_json(store: BookmarkStore, dest: Path) -> int:
    """Write all bookmarks to *dest* as JSON. Returns count written."""
    items = store.all()
    dest.write_text(json.dumps([b.to_dict() for b in items], indent=2))
    return len(items)


def export_bookmarks_text(store: BookmarkStore, dest: Path) -> int:
    """Write all bookmarks to *dest* as human-readable text."""
    items = store.all()
    lines = [str(b) for b in items]
    dest.write_text("\n".join(lines) + ("\n" if lines else ""))
    return len(items)


def import_bookmarks_json(store: BookmarkStore, src: Path, overwrite: bool = False) -> int:
    """Import bookmarks from a JSON file. Returns count imported."""
    raw = json.loads(src.read_text())
    count = 0
    for entry in raw:
        bm = Bookmark.from_dict(entry)
        if store.get(bm.label) is None or overwrite:
            store.add(bm)
            count += 1
    return count


def bookmark_summary(store: BookmarkStore) -> str:
    """Return a one-line summary of the bookmark store."""
    items = store.all()
    if not items:
        return "No bookmarks."
    files = {b.file for b in items}
    return f"{len(items)} bookmark(s) across {len(files)} file(s)."
