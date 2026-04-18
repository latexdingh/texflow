"""Build tagging — attach named tags to builds for quick reference."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_STORE = Path(".texflow_tags.json")


@dataclass
class BuildTag:
    label: str
    source: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    note: str = ""

    def to_dict(self) -> dict:
        return {"label": self.label, "source": self.source,
                "created_at": self.created_at, "note": self.note}

    @staticmethod
    def from_dict(d: dict) -> "BuildTag":
        return BuildTag(label=d["label"], source=d["source"],
                        created_at=d.get("created_at", ""), note=d.get("note", ""))

    def __str__(self) -> str:
        note_part = f"  # {self.note}" if self.note else ""
        return f"[{self.label}] {self.source} @ {self.created_at}{note_part}"


class TagStore:
    def __init__(self, store_path: Path = _DEFAULT_STORE) -> None:
        self._path = store_path
        self._tags: Dict[str, BuildTag] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            data = json.loads(self._path.read_text())
            self._tags = {k: BuildTag.from_dict(v) for k, v in data.items()}

    def _save(self) -> None:
        self._path.write_text(json.dumps({k: v.to_dict() for k, v in self._tags.items()}, indent=2))

    def add(self, tag: BuildTag) -> None:
        self._tags[tag.label] = tag
        self._save()

    def get(self, label: str) -> Optional[BuildTag]:
        return self._tags.get(label)

    def remove(self, label: str) -> bool:
        if label in self._tags:
            del self._tags[label]
            self._save()
            return True
        return False

    def all(self) -> List[BuildTag]:
        return list(self._tags.values())
