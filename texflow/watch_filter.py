"""Filter rules for deciding which file events should trigger a rebuild."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

DEFAULT_IGNORE_DIRS = {".git", "__pycache__", ".texflow_exports", "node_modules"}
DEFAULT_WATCH_EXTENSIONS = {".tex", ".bib", ".cls", ".sty", ".bst"}


@dataclass
class WatchFilter:
    watch_extensions: List[str] = field(default_factory=lambda: list(DEFAULT_WATCH_EXTENSIONS))
    ignore_dirs: List[str] = field(default_factory=lambda: list(DEFAULT_IGNORE_DIRS))
    ignore_patterns: List[str] = field(default_factory=list)

    def should_process(self, path: str) -> bool:
        """Return True if the given file path should trigger a rebuild."""
        p = Path(path)

        # Must be a file with a watched extension
        if p.suffix not in self.watch_extensions:
            return False

        # Check none of the path parts are ignored directories
        parts = set(p.parts)
        if parts & set(self.ignore_dirs):
            return False

        # Check against simple glob-style ignore patterns (basename only)
        name = p.name
        for pattern in self.ignore_patterns:
            if _match_pattern(name, pattern):
                return False

        return True

    def add_extension(self, ext: str) -> None:
        if not ext.startswith("."):
            ext = "." + ext
        if ext not in self.watch_extensions:
            self.watch_extensions.append(ext)

    def ignore_dir(self, dirname: str) -> None:
        if dirname not in self.ignore_dirs:
            self.ignore_dirs.append(dirname)

    def ignore_pattern(self, pattern: str) -> None:
        if pattern not in self.ignore_patterns:
            self.ignore_patterns.append(pattern)


def _match_pattern(name: str, pattern: str) -> bool:
    """Very small subset of glob: supports leading/trailing '*' only."""
    if pattern.startswith("*") and pattern.endswith("*"):
        return pattern[1:-1] in name
    if pattern.startswith("*"):
        return name.endswith(pattern[1:])
    if pattern.endswith("*"):
        return name.startswith(pattern[:-1])
    return name == pattern
