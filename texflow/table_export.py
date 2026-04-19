"""Export table check results to JSON or plain text."""
from __future__ import annotations
import json
from pathlib import Path
from texflow.table_check import TableCheckResult


def export_table_check_json(result: TableCheckResult, dest: Path) -> None:
    """Write table check result as JSON to *dest*."""
    data = {
        "table_count": result.table_count,
        "ok": result.ok(),
        "issues": [
            {"line": issue.line, "message": issue.message}
            for issue in result.issues
        ],
    }
    dest.write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_table_check_text(result: TableCheckResult, dest: Path) -> None:
    """Write table check result as plain text to *dest*."""
    lines = [result.summary()]
    for issue in result.issues:
        lines.append(f"  - {issue}")
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_check_summary(result: TableCheckResult) -> str:
    """Return a compact one-line summary string."""
    if result.ok():
        return f"✓ {result.table_count} table(s), no issues"
    return f"✗ {len(result.issues)} issue(s) across {result.table_count} table(s)"
