"""Track file snapshots to enable diff computation on change."""
from __future__ import annotations

import os
from typing import Dict, Optional


class SnapshotStore:
    """Stores last-seen content of watched files."""

    def __init__(self) -> None:
        self._store: Dict[str, str] = {}

    def read_and_store(self, path: str) -> str:
        """Read file content, store it, and return it."""
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                content = fh.read()
        except OSError:
            content = ''
        self._store[path] = content
        return content

    def get(self, path: str) -> Optional[str]:
        return self._store.get(path)

    def update(self, path: str, content: str) -> None:
        self._store[path] = content

    def remove(self, path: str) -> None:
        self._store.pop(path, None)

    def preload(self, directory: str, extension: str = '.tex') -> None:
        """Preload all matching files under a directory."""
        for root, _, files in os.walk(directory):
            for fname in files:
                if fname.endswith(extension):
                    full = os.path.join(root, fname)
                    self.read_and_store(full)
