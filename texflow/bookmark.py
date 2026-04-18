"""Named bookmarks for source positions in .tex files."""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

DEFAULT_STORE = Path(".texflow_bookmarks.json")


@dataclass
class Bookmark:
    label: str
    file: str
    line: int
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Bookmark":
        return Bookmark(**d)

    def __str__(self) -> str:
        note_part = f" — {self.note}" if self.note else ""
        return f"[{self.label}] {self.file}:{self.line}{note_part}"


class BookmarkStore:
    def __init__(self, path: Path = DEFAULT_STORE):
        self._path = path
        self._data: dict[str, Bookmark] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            raw = json.loads(self._path.read_text())
            self._data = {k: Bookmark.from_dict(v) for k, v in raw.items()}

    def _save(self) -> None:
        self._path.write_text(json.dumps({k: v.to_dict() for k, v in self._data.items()}, indent=2))

    def add(self, bm: Bookmark) -> None:
        self._data[bm.label] = bm
        self._save()

    def get(self, label: str) -> Optional[Bookmark]:
        return self._data.get(label)

    def remove(self, label: str) -> bool:
        if label in self._data:
            del self._data[label]
            self._save()
            return True
        return False

    def all(self) -> list[Bookmark]:
        return list(self._data.values())
