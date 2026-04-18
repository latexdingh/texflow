"""Simple in-memory search index for fast repeated queries."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple


class SearchIndex:
    """Caches file lines so repeated searches avoid re-reading disk."""

    def __init__(self) -> None:
        self._cache: Dict[Path, Tuple[float, List[str]]] = {}

    def _load(self, path: Path) -> List[str]:
        try:
            mtime = path.stat().st_mtime
        except OSError:
            return []
        if path in self._cache:
            cached_mtime, lines = self._cache[path]
            if cached_mtime == mtime:
                return lines
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return []
        self._cache[path] = (mtime, lines)
        return lines

    def lines(self, path: Path) -> List[str]:
        return self._load(path)

    def invalidate(self, path: Path) -> None:
        self._cache.pop(path, None)

    def invalidate_all(self) -> None:
        self._cache.clear()

    @property
    def cached_paths(self) -> List[Path]:
        return list(self._cache.keys())
