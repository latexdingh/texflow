"""Persistent store for saved snippets."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
from texflow.snippet import Snippet

_DEFAULT = Path(".texflow_snippets.json")


class SnippetStore:
    def __init__(self, store_path: Path = _DEFAULT) -> None:
        self._path = store_path
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def save(self, snippet: Snippet) -> None:
        self._data[snippet.label] = {
            "content": snippet.content,
            "source_file": snippet.source_file,
            "start_line": snippet.start_line,
        }
        self._save()

    def get(self, label: str) -> Optional[Snippet]:
        d = self._data.get(label)
        if d is None:
            return None
        return Snippet(label=label, **d)

    def remove(self, label: str) -> bool:
        if label in self._data:
            del self._data[label]
            self._save()
            return True
        return False

    def all(self) -> list[Snippet]:
        return [Snippet(label=k, **v) for k, v in self._data.items()]
