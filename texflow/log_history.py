"""Persist and retrieve build log history for a project."""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

HISTORY_FILE = ".texflow_history.json"
MAX_ENTRIES = 50


@dataclass
class BuildRecord:
    timestamp: float
    success: bool
    errors: int
    warnings: int
    source_file: str
    duration_ms: Optional[float] = None

    def formatted_time(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))


@dataclass
class BuildHistory:
    records: List[BuildRecord] = field(default_factory=list)

    def add(self, record: BuildRecord) -> None:
        self.records.append(record)
        if len(self.records) > MAX_ENTRIES:
            self.records = self.records[-MAX_ENTRIES:]

    def last(self, n: int = 5) -> List[BuildRecord]:
        return self.records[-n:]

    def success_rate(self) -> float:
        if not self.records:
            return 0.0
        return sum(1 for r in self.records if r.success) / len(self.records)


def load_history(directory: Path) -> BuildHistory:
    path = directory / HISTORY_FILE
    if not path.exists():
        return BuildHistory()
    try:
        data = json.loads(path.read_text())
        records = [BuildRecord(**r) for r in data.get("records", [])]
        return BuildHistory(records=records)
    except Exception:
        return BuildHistory()


def save_history(directory: Path, history: BuildHistory) -> None:
    path = directory / HISTORY_FILE
    path.write_text(json.dumps({"records": [asdict(r) for r in history.records]}, indent=2))
