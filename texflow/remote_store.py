"""Persist remote targets to a JSON config file."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional

from texflow.remote import RemoteTarget

DEFAULT_PATH = Path(".texflow_remotes.json")


class RemoteStore:
    def __init__(self, path: Path = DEFAULT_PATH):
        self._path = path
        self._targets: List[RemoteTarget] = []
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            data = json.loads(self._path.read_text())
            self._targets = [RemoteTarget.from_dict(d) for d in data]

    def _save(self) -> None:
        self._path.write_text(
            json.dumps([t.to_dict() for t in self._targets], indent=2)
        )

    def all(self) -> List[RemoteTarget]:
        return list(self._targets)

    def get(self, name: str) -> Optional[RemoteTarget]:
        return next((t for t in self._targets if t.name == name), None)

    def add(self, target: RemoteTarget) -> bool:
        if self.get(target.name):
            return False
        self._targets.append(target)
        self._save()
        return True

    def remove(self, name: str) -> bool:
        before = len(self._targets)
        self._targets = [t for t in self._targets if t.name != name]
        if len(self._targets) < before:
            self._save()
            return True
        return False

    def update(self, target: RemoteTarget) -> bool:
        for i, t in enumerate(self._targets):
            if t.name == target.name:
                self._targets[i] = target
                self._save()
                return True
        return False
