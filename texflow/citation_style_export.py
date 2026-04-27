"""Export citation style results to JSON or plain text."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from texflow.citation_style import CitationStyleResult, check_citation_style


def export_citation_style_json(result: CitationStyleResult) -> str:
    """Serialise a CitationStyleResult to a JSON string."""
    data = {
        "ok": result.ok(),
        "cite_count": result.cite_count,
        "styles_found": result.styles_found,
        "issue_count": len(result.issues),
        "issues": [
            {"line": i.line, "message": i.message, "snippet": i.snippet}
            for i in result.issues
        ],
    }
    return json.dumps(data, indent=2)


def export_citation_style_text(result: CitationStyleResult) -> str:
    """Serialise a CitationStyleResult to a plain-text report."""
    lines = [result.summary()]
    if result.styles_found:
        lines.append("Styles: " + ", ".join(f"\\{s}" for s in result.styles_found))
    for issue in result.issues:
        lines.append(str(issue))
    return "\n".join(lines)


def citation_style_summary(path: Union[str, Path]) -> str:
    """Return a one-line summary for *path* without extra options."""
    result = check_citation_style(Path(path))
    return result.summary()
