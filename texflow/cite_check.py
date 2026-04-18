"""Check for undefined or unused citations in a LaTeX project."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set


@dataclass
class CiteCheckResult:
    undefined: list[str] = field(default_factory=list)
    unused: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.undefined and not self.unused

    def summary(self) -> str:
        parts = []
        if self.undefined:
            parts.append(f"{len(self.undefined)} undefined citation(s)")
        if self.unused:
            parts.append(f"{len(self.unused)} unused citation(s)")
        return ", ".join(parts) if parts else "All citations OK"


def _extract_cite_keys(tex_source: str) -> Set[str]:
    """Return all citation keys referenced in the source."""
    pattern = re.compile(r"\\(?:cite|citep|citet|citealt|nocite)\{([^}]+)\}")
    keys: Set[str] = set()
    for match in pattern.finditer(tex_source):
        for key in match.group(1).split(","):
            keys.add(key.strip())
    return keys


def _extract_bib_keys(bib_source: str) -> Set[str]:
    """Return all entry keys defined in a .bib file."""
    pattern = re.compile(r"@\w+\{([^,]+),")
    return {m.group(1).strip() for m in pattern.finditer(bib_source)}


def check_citations(tex_path: Path, bib_path: Path | None = None) -> CiteCheckResult:
    """Compare citation usage in *tex_path* against definitions in *bib_path*.

    If *bib_path* is None the function tries to locate a .bib file in the
    same directory as the tex file.
    """
    if not tex_path.exists():
        return CiteCheckResult()

    tex_source = tex_path.read_text(encoding="utf-8", errors="replace")
    cited_keys = _extract_cite_keys(tex_source)

    if bib_path is None:
        candidates = list(tex_path.parent.glob("*.bib"))
        bib_path = candidates[0] if candidates else None

    if bib_path is None or not bib_path.exists():
        return CiteCheckResult(undefined=sorted(cited_keys))

    bib_source = bib_path.read_text(encoding="utf-8", errors="replace")
    defined_keys = _extract_bib_keys(bib_source)

    undefined = sorted(cited_keys - defined_keys)
    unused = sorted(defined_keys - cited_keys)
    return CiteCheckResult(undefined=undefined, unused=unused)
