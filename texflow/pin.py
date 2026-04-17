"""Pin/bookmark specific build snapshots for later comparison."""
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

DEFAULT_PIN_FILE = Path(".texflow_pins.json")


@dataclass
class PinnedBuild:
    label: str
    pdf_path: str
    tex_snapshot: str  # content hash or raw content
    timestamp: str
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "PinnedBuild":
        return PinnedBuild(**d)


class PinStore:
    def __init__(self, pin_file: Path = DEFAULT_PIN_FILE):
        self._file = pin_file
        self._pins: dict[str, PinnedBuild] = {}
        self._load()

    def _load(self) -> None:
        if self._file.exists():
            data = json.loads(self._file.read_text())
            self._pins = {k: PinnedBuild.from_dict(v) for k, v in data.items()}

    def _save(self) -> None:
        self._file.write_text(json.dumps({k: v.to_dict() for k, v in self._pins.items()}, indent=2))

    def add(self, pin: PinnedBuild) -> None:
        self._pins[pin.label] = pin
        self._save()

    def get(self, label: str) -> Optional[PinnedBuild]:
        return self._pins.get(label)

    def remove(self, label: str) -> bool:
        if label in self._pins:
            del self._pins[label]
            self._save()
            return True
        return False

    def all(self) -> list[PinnedBuild]:
        return list(self._pins.values())
