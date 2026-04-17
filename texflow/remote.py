"""Remote/cloud export targets for compiled PDFs."""
from __future__ import annotations
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class RemoteTarget:
    name: str
    kind: str          # 'directory' | 'ftp' (extensible)
    path: str          # local path or remote URL
    auto_push: bool = False

    def to_dict(self) -> dict:
        return {"name": self.name, "kind": self.kind,
                "path": self.path, "auto_push": self.auto_push}

    @classmethod
    def from_dict(cls, d: dict) -> "RemoteTarget":
        return cls(
            name=d["name"], kind=d["kind"],
            path=d["path"], auto_push=d.get("auto_push", False)
        )


@dataclass
class PushResult:
    success: bool
    target: str
    dest: str
    message: str = ""

    def __str__(self) -> str:
        status = "OK" if self.success else "FAIL"
        return f"[{status}] {self.target} -> {self.dest}" + (
            f": {self.message}" if self.message else ""
        )


def push_to_target(pdf: Path, target: RemoteTarget) -> PushResult:
    """Push a compiled PDF to the given remote target."""
    if not pdf.exists():
        return PushResult(False, target.name, target.path,
                          message=f"{pdf} not found")

    if target.kind == "directory":
        dest_dir = Path(target.path)
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / pdf.name
            shutil.copy2(pdf, dest)
            return PushResult(True, target.name, str(dest))
        except OSError as exc:
            return PushResult(False, target.name, target.path, message=str(exc))

    return PushResult(False, target.name, target.path,
                      message=f"unsupported kind: {target.kind}")
