"""custom_command.py – define and run user-defined build commands."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_DEFAULT_STORE = Path(".texflow_commands.json")


@dataclass
class CustomCommand:
    label: str
    command: str
    description: str = ""

    def to_dict(self) -> dict:
        return {"label": self.label, "command": self.command, "description": self.description}

    @staticmethod
    def from_dict(d: dict) -> "CustomCommand":
        return CustomCommand(
            label=d["label"],
            command=d["command"],
            description=d.get("description", ""),
        )

    def __str__(self) -> str:
        desc = f" — {self.description}" if self.description else ""
        return f"[{self.label}] {self.command}{desc}"


@dataclass
class RunResult:
    label: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def __str__(self) -> str:
        status = "ok" if self.ok else f"exit {self.returncode}"
        return f"{self.label}: {status}"


class CommandStore:
    def __init__(self, path: Path = _DEFAULT_STORE) -> None:
        self._path = path
        self._commands: List[CustomCommand] = self._load()

    def _load(self) -> List[CustomCommand]:
        if not self._path.exists():
            return []
        data = json.loads(self._path.read_text())
        return [CustomCommand.from_dict(d) for d in data]

    def _save(self) -> None:
        self._path.write_text(json.dumps([c.to_dict() for c in self._commands], indent=2))

    def all(self) -> List[CustomCommand]:
        return list(self._commands)

    def get(self, label: str) -> Optional[CustomCommand]:
        return next((c for c in self._commands if c.label == label), None)

    def add(self, cmd: CustomCommand) -> None:
        self._commands = [c for c in self._commands if c.label != cmd.label]
        self._commands.append(cmd)
        self._save()

    def remove(self, label: str) -> bool:
        before = len(self._commands)
        self._commands = [c for c in self._commands if c.label != label]
        if len(self._commands) < before:
            self._save()
            return True
        return False


def run_command(cmd: CustomCommand, cwd: Optional[Path] = None) -> RunResult:
    result = subprocess.run(
        cmd.command, shell=True, capture_output=True, text=True, cwd=cwd
    )
    return RunResult(
        label=cmd.label,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )
