"""Multi-file project support: discover root and included .tex files."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set

_INPUT_RE = re.compile(r'\\(?:input|include)\{([^}]+)\}')


def _resolve(base: Path, ref: str) -> Path:
    p = base / ref
    if p.suffix == '':
        p = p.with_suffix('.tex')
    return p


def collect_includes(root: Path, _seen: Set[Path] | None = None) -> List[Path]:
    """Return all .tex files reachable from *root* via \\input / \\include."""
    if _seen is None:
        _seen = set()
    root = root.resolve()
    if root in _seen or not root.exists():
        return []
    _seen.add(root)
    files: List[Path] = [root]
    try:
        text = root.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return files
    base = root.parent
    for match in _INPUT_RE.finditer(text):
        child = _resolve(base, match.group(1))
        files.extend(collect_includes(child, _seen))
    return files


def find_root(start: Path) -> Path:
    """Walk up from *start* looking for a .tex file that contains \\documentclass."""
    candidate = start if start.is_file() else start / 'main.tex'
    for path in [candidate, *candidate.parents]:
        if path.is_file() and path.suffix == '.tex':
            try:
                if '\\documentclass' in path.read_text(encoding='utf-8', errors='replace'):
                    return path
            except OSError:
                pass
        if path.is_dir():
            for tex in sorted(path.glob('*.tex')):
                try:
                    if '\\documentclass' in tex.read_text(encoding='utf-8', errors='replace'):
                        return tex
                except OSError:
                    pass
    return candidate


def project_files(start: Path) -> List[Path]:
    """Return all .tex files belonging to the project rooted at *start*."""
    root = find_root(start)
    return collect_includes(root)
