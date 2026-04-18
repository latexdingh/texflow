"""Check for undefined and unused \label/\ref pairs in LaTeX source."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set


@dataclass
class RefCheckResult:
    undefined_refs: list[str] = field(default_factory=list)
    unused_labels: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.undefined_refs and not self.unused_labels

    def summary(self) -> str:
        parts = []
        if self.undefined_refs:
            parts.append(f"{len(self.undefined_refs)} undefined ref(s)")
        if self.unused_labels:
            parts.append(f"{len(self.unused_labels)} unused label(s)")
        return ", ".join(parts) if parts else "all refs OK"

    def __str__(self) -> str:
        lines = []
        for r in self.undefined_refs:
            lines.append(f"  [undef ref]  \\ref{{{r}}}")
        for l in self.unused_labels:
            lines.append(f"  [unused lbl] \\label{{{l}}}")
        return "\n".join(lines)


def _extract_labels(text: str) -> Set[str]:
    return set(re.findall(r"\\label\{([^}]+)\}", text))


def _extract_refs(text: str) -> Set[str]:
    keys: Set[str] = set()
    for m in re.findall(r"\\(?:ref|eqref|pageref|autoref|cref|Cref)\{([^}]+)\}", text):
        for k in m.split(","):
            keys.add(k.strip())
    return keys


def check_refs(tex_path: Path, extra_files: list[Path] | None = None) -> RefCheckResult:
    """Scan *tex_path* (and optional extra files) for label/ref mismatches."""
    paths = [tex_path] + (extra_files or [])
    all_labels: Set[str] = set()
    all_refs: Set[str] = set()
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            continue
        # strip comments
        text = re.sub(r"%.*", "", text)
        all_labels |= _extract_labels(text)
        all_refs |= _extract_refs(text)

    undefined = sorted(all_refs - all_labels)
    unused = sorted(all_labels - all_refs)
    return RefCheckResult(undefined_refs=undefined, unused_labels=unused)
