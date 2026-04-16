"""Inline diff preview for LaTeX source changes."""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import List


@dataclass
class DiffLine:
    kind: str  # 'added', 'removed', 'context'
    lineno_old: int | None
    lineno_new: int | None
    content: str


@dataclass
class DiffResult:
    lines: List[DiffLine] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(l.kind != 'context' for l in self.lines)

    def added_count(self) -> int:
        return sum(1 for l in self.lines if l.kind == 'added')

    def removed_count(self) -> int:
        return sum(1 for l in self.lines if l.kind == 'removed')


def compute_diff(old_text: str, new_text: str, context: int = 3) -> DiffResult:
    """Compute a unified diff between two text strings."""
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    result = DiffResult()

    for group in matcher.get_grouped_opcodes(context):
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for k, line in enumerate(old_lines[i1:i2]):
                    result.lines.append(DiffLine('context', i1 + k + 1, j1 + k + 1, line.rstrip('\n')))
            elif tag in ('replace', 'delete'):
                for k, line in enumerate(old_lines[i1:i2]):
                    result.lines.append(DiffLine('removed', i1 + k + 1, None, line.rstrip('\n')))
            if tag in ('replace', 'insert'):
                for k, line in enumerate(new_lines[j1:j2]):
                    result.lines.append(DiffLine('added', None, j1 + k + 1, line.rstrip('\n')))

    return result


def format_diff(diff: DiffResult, use_color: bool = True) -> str:
    """Format a DiffResult as a human-readable string."""
    if not diff.has_changes:
        return "(no changes)"

    lines = []
    for dl in diff.lines:
        old_no = str(dl.lineno_old).rjust(4) if dl.lineno_old else '    '
        new_no = str(dl.lineno_new).rjust(4) if dl.lineno_new else '    '
        prefix = {'added': '+', 'removed': '-', 'context': ' '}[dl.kind]
        line = f"{old_no} {new_no} {prefix} {dl.content}"
        if use_color:
            if dl.kind == 'added':
                line = f"\033[32m{line}\033[0m"
            elif dl.kind == 'removed':
                line = f"\033[31m{line}\033[0m"
        lines.append(line)

    summary = f"+{diff.added_count()} / -{diff.removed_count()} lines"
    return summary + '\n' + '\n'.join(lines)
