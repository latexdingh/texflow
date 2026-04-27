"""Export helpers for whitespace check results."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from texflow.whitespace import WhitespaceResult, check_whitespace


def export_whitespace_json(result: WhitespaceResult) -> str:
    """Serialise a WhitespaceResult to a JSON string."""
    data: Dict[str, Any] = {
        "ok": result.ok(),
        "missing": result.missing,
        "issue_count": len(result.issues),
        "issues": [
            {"line": i.line, "kind": i.kind, "text": i.text}
            for i in result.issues
        ],
    }
    return json.dumps(data, indent=2)


def export_whitespace_text(result: WhitespaceResult) -> str:
    """Serialise a WhitespaceResult to a plain-text report."""
    if result.missing:
        return "File not found.\n"
    lines: List[str] = [result.summary()]
    for issue in result.issues:
        lines.append(f"  {issue}")
    return "\n".join(lines) + "\n"


def whitespace_summary(path: Path, **kwargs: bool) -> str:
    """Return a one-line summary for *path*."""
    result = check_whitespace(path, **kwargs)  # type: ignore[arg-type]
    return result.summary()
