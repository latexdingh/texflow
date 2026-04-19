"""Check and list hyperlinks/URLs in LaTeX source files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

_URL_PATTERN = re.compile(
    r'\\(?:href|url)\{([^}]+)\}|'
    r'\\hyperref\[([^\]]+)\]'
)
_BARE_URL = re.compile(r'https?://[^\s}%]+')


@dataclass
class HyperlinkItem:
    line: int
    url: str
    kind: str  # 'href', 'url', 'hyperref', 'bare'

    def __str__(self) -> str:
        return f"Line {self.line}: [{self.kind}] {self.url}"


@dataclass
class HyperlinkResult:
    links: List[HyperlinkItem] = field(default_factory=list)
    error: str = ""

    def ok(self) -> bool:
        return not self.error

    def summary(self) -> str:
        if self.error:
            return f"Error: {self.error}"
        if not self.links:
            return "No hyperlinks found."
        return f"{len(self.links)} hyperlink(s) found."


def extract_hyperlinks(path: Path) -> HyperlinkResult:
    if not path.exists():
        return HyperlinkResult(error=f"File not found: {path}")

    links: List[HyperlinkItem] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return HyperlinkResult(error=str(exc))

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        for m in _URL_PATTERN.finditer(line):
            if m.group(1) is not None:
            # href or url
                cmd = "href" if "href" in m.group(0) else "url"
                links.append(HyperlinkItem(lineno, m.group(1), cmd))
            elif m.group(2) is not None:
                links.append(HyperlinkItem(lineno, m.group(2), "hyperref"))
        # Bare URLs not inside a command
        for bm in _BARE_URL.finditer(line):
            if not any(bm.start() > 0 and line[bm.start()-1] == '{' for _ in [1]):
                links.append(HyperlinkItem(lineno, bm.group(0), "bare"))

    return HyperlinkResult(links=links)
