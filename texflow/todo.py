"""Extract and manage TODO/FIXME comments from LaTeX source files."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re

TODO_PATTERN = re.compile(
    r"%+\s*(TODO|FIXME|HACK|NOTE|XXX)(?:\s*[:\-])?\s*(.*)",
    re.IGNORECASE,
)


@dataclass
class TodoItem:
    file: Path
    line: int
    kind: str
    message: str

    def __str__(self) -> str:
        return f"[{self.kind}] {self.file}:{self.line}  {self.message}"


@dataclass
class TodoResult:
    items: list[TodoItem]

    @property
    def ok(self) -> bool:
        return len(self.items) == 0

    def summary(self) -> str:
        if self.ok:
            return "No TODO items found."
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.kind] = counts.get(item.kind, 0) + 1
        parts = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
        return f"{len(self.items)} item(s): {parts}"

    def by_kind(self, kind: str) -> list[TodoItem]:
        return [i for i in self.items if i.kind.upper() == kind.upper()]


def scan_todos(path: Path) -> TodoResult:
    """Scan a single .tex file for TODO-style comments."""
    if not path.exists():
        return TodoResult(items=[])
    items: list[TodoItem] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = TODO_PATTERN.search(line)
        if m:
            items.append(TodoItem(
                file=path,
                line=lineno,
                kind=m.group(1).upper(),
                message=m.group(2).strip(),
            ))
    return TodoResult(items=items)


def scan_todos_multi(files: list[Path]) -> TodoResult:
    """Scan multiple files and merge results."""
    all_items: list[TodoItem] = []
    for f in files:
        all_items.extend(scan_todos(f).items)
    return TodoResult(items=all_items)
