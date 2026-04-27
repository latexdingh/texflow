"""Citation style checker: validates \\cite usage patterns and style consistency."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class StyleIssue:
    line: int
    message: str
    snippet: str

    def __str__(self) -> str:
        return f"  Line {self.line}: {self.message} — {self.snippet!r}"


@dataclass
class CitationStyleResult:
    issues: List[StyleIssue] = field(default_factory=list)
    cite_count: int = 0
    styles_found: List[str] = field(default_factory=list)
    missing: bool = False

    def ok(self) -> bool:
        return not self.missing and len(self.issues) == 0

    def summary(self) -> str:
        if self.missing:
            return "File not found."
        if self.ok():
            return f"Citation style OK ({self.cite_count} citation(s))."
        return f"{len(self.issues)} style issue(s) across {self.cite_count} citation(s)."


_CITE_RE = re.compile(r"\\(cite|citep|citet|citealt|citealp|citeauthor|citeyear)\s*(?:\[[^\]]*\])?\{([^}]*)\}")
_MULTI_KEY_RE = re.compile(r"\{[^}]*,[^}]*\}")
_SPACE_AFTER_CITE_RE = re.compile(r"\\cite[a-z]*\s*\{")
_TILDE_BEFORE_CITE_RE = re.compile(r"~\\cite")


def check_citation_style(
    path: Path,
    require_tilde: bool = True,
    disallow_multi_key: bool = False,
) -> CitationStyleResult:
    if not path.exists():
        return CitationStyleResult(missing=True)

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    issues: List[StyleIssue] = []
    styles_found: set = set()
    cite_count = 0

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("%"):
            continue

        for m in _CITE_RE.finditer(line):
            cite_count += 1
            styles_found.add(m.group(1))

            if disallow_multi_key and "," in m.group(2):
                issues.append(StyleIssue(lineno, "Multiple keys in single \\cite", line.strip()))

        if require_tilde:
            for m in _SPACE_AFTER_CITE_RE.finditer(line):
                start = m.start()
                preceding = line[:start]
                if _CITE_RE.search(line) and not preceding.endswith("~") and not preceding.endswith("("):
                    if preceding and not preceding[-1] in ("~", "(", "{", "["):
                        issues.append(StyleIssue(lineno, "Missing non-breaking space (~) before \\cite", line.strip()))
                        break

    return CitationStyleResult(
        issues=issues,
        cite_count=cite_count,
        styles_found=sorted(styles_found),
    )
