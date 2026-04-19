"""Cross-reference map: builds a document-wide map of labels to their context."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Dict, List, Optional


@dataclass
class CrossRefEntry:
    label: str
    file: str
    line: int
    context: str  # surrounding text snippet

    def __str__(self) -> str:
        return f"{self.label} ({self.file}:{self.line}) — {self.context[:60]}"


@dataclass
class CrossRefMap:
    entries: List[CrossRefEntry] = field(default_factory=list)

    def ok(self) -> bool:
        return len(self.entries) > 0

    def get(self, label: str) -> Optional[CrossRefEntry]:
        for e in self.entries:
            if e.label == label:
                return e
        return None

    def summary(self) -> str:
        return f"{len(self.entries)} label(s) indexed"

    def as_dict(self) -> Dict[str, CrossRefEntry]:
        return {e.label: e for e in self.entries}


_LABEL_RE = re.compile(r"\\label\{([^}]+)\}")


def build_cross_ref_map(files: List[Path]) -> CrossRefMap:
    """Scan a list of .tex files and build a map of all \\label definitions."""
    entries: List[CrossRefEntry] = []
    for path in files:
        if not path.exists():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for lineno, text in enumerate(lines, start=1):
            for m in _LABEL_RE.finditer(text):
                entries.append(
                    CrossRefEntry(
                        label=m.group(1),
                        file=str(path),
                        line=lineno,
                        context=text.strip(),
                    )
                )
    return CrossRefMap(entries=entries)
