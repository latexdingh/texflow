"""Terminal output formatting for texflow build results."""
from dataclasses import dataclass
from typing import List
from texflow.parser import ParseResult, LatexError
from texflow.diff import DiffResult, DiffLine

RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def _c(color: str, text: str, use_color: bool = True) -> str:
    return f"{color}{text}{RESET}" if use_color else text


def format_errors(result: ParseResult, use_color: bool = True) -> str:
    lines = []
    for err in result.errors:
        loc = f"{err.file}:{err.line}" if err.line else err.file
        prefix = _c(RED, "ERROR", use_color)
        lines.append(f"{prefix} [{loc}] {err.message}")
    for warn in result.warnings:
        loc = f":{warn.line}" if warn.line else ""
        prefix = _c(YELLOW, "WARN", use_color)
        lines.append(f"{prefix}{loc} {warn.message}")
    return "\n".join(lines)


def format_diff(diff: DiffResult, use_color: bool = True) -> str:
    if not diff.has_changes:
        return _c(DIM, "(no content changes)", use_color)
    lines = []
    for dl in diff.lines:
        if dl.kind == "added":
            lines.append(_c(GREEN, f"+ {dl.text}", use_color))
        elif dl.kind == "removed":
            lines.append(_c(RED, f"- {dl.text}", use_color))
        else:
            lines.append(_c(DIM, f"  {dl.text}", use_color))
    summary = _c(CYAN, f"[+{diff.added_count} -{diff.removed_count}]", use_color)
    lines.append(summary)
    return "\n".join(lines)


def format_build_status(success: bool, source: str, use_color: bool = True) -> str:
    if success:
        icon = _c(GREEN, "✔", use_color)
        return f"{icon} {_c(BOLD, 'Build succeeded', use_color)}: {source}"
    icon = _c(RED, "✘", use_color)
    return f"{icon} {_c(BOLD, 'Build failed', use_color)}: {source}"
