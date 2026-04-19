"""Utilities to export figure inventory as JSON or plain text."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List
from texflow.figure import FigureResult, check_figures


def export_figures_json(result: FigureResult) -> str:
    data = {
        "figures": result.figures,
        "issues": [
            {"path": i.path, "line": i.line, "message": i.message}
            for i in result.issues
        ],
        "ok": result.ok(),
    }
    return json.dumps(data, indent=2)


def export_figures_text(result: FigureResult) -> str:
    lines: List[str] = [result.summary()]
    for fig in result.figures:
        status = "✓" if not any(i.path == fig for i in result.issues) else "✗"
        lines.append(f"  {status} {fig}")
    return "\n".join(lines)


def figure_summary(tex_path: Path, base_dir: Path | None = None) -> str:
    result = check_figures(tex_path, base_dir)
    return result.summary()
