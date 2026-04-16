"""Run pdflatex and return structured parse results."""
from __future__ import annotations
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from .parser import ParseResult, parse_log


DEFAULT_CMD = "pdflatex"
DEFAULT_FLAGS = ["-interaction=nonstopmode", "-halt-on-error"]


def compile_latex(
    source: Path,
    output_dir: Optional[Path] = None,
    cmd: str = DEFAULT_CMD,
    extra_flags: Optional[list] = None,
) -> tuple[ParseResult, int]:
    """Compile *source* and return (ParseResult, returncode)."""
    source = Path(source).resolve()
    if output_dir is None:
        output_dir = source.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    flags = DEFAULT_FLAGS + (extra_flags or [])
    command = [cmd, *flags, f"-output-directory={output_dir}", str(source)]

    try:
        proc = subprocess.run(
            command,
            cwd=source.parent,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        result = ParseResult()
        from .parser import LatexError
        result.errors.append(LatexError(message=f"Compiler not found: {cmd}"))
        return result, 127
    except subprocess.TimeoutExpired:
        result = ParseResult()
        from .parser import LatexError
        result.errors.append(LatexError(message="Compilation timed out after 60s"))
        return result, 1

    log_text = proc.stdout + proc.stderr
    return parse_log(log_text), proc.returncode


def find_output_pdf(source: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
    """Return the expected PDF path for a given source file."""
    source = Path(source)
    base = output_dir or source.parent
    pdf = Path(base) / source.with_suffix(".pdf").name
    return pdf if pdf.exists() else None
