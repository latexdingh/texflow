"""Rename a .tex source file and update \\input/\\include references across the project."""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class RenameResult:
    old_path: Path
    new_path: Path
    updated_files: List[Path] = field(default_factory=list)
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error

    def __str__(self) -> str:
        if not self.ok:
            return f"Rename failed: {self.error}"
        lines = [f"Renamed: {self.old_path} -> {self.new_path}"]
        if self.updated_files:
            lines.append("Updated references in:")
            for f in self.updated_files:
                lines.append(f"  {f}")
        else:
            lines.append("No references updated.")
        return "\n".join(lines)


_REF_RE = re.compile(
    r'(\\(?:input|include)\{)([^}]+)(\})',
    re.MULTILINE,
)


def _stem(name: str) -> str:
    """Return name without .tex suffix for comparison."""
    return name[:-4] if name.endswith(".tex") else name


def _update_references(files: List[Path], old_stem: str, new_stem: str) -> List[Path]:
    changed: List[Path] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        new_text, n = _REF_RE.subn(
            lambda m: m.group(1) + new_stem + m.group(3)
            if _stem(m.group(2)) == old_stem else m.group(0),
            text,
        )
        if n and new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed.append(path)
    return changed


def rename_tex_file(
    old_path: Path,
    new_name: str,
    project_root: Path | None = None,
) -> RenameResult:
    if not old_path.exists():
        return RenameResult(old_path, old_path, error=f"File not found: {old_path}")
    if not old_path.suffix == ".tex":
        return RenameResult(old_path, old_path, error="Only .tex files can be renamed")

    new_path = old_path.with_name(new_name if new_name.endswith(".tex") else new_name + ".tex")
    if new_path.exists():
        return RenameResult(old_path, new_path, error=f"Destination already exists: {new_path}")

    root = project_root or old_path.parent
    tex_files = [p for p in root.rglob("*.tex") if p != old_path]

    old_stem = old_path.stem
    new_stem = new_path.stem

    shutil.move(str(old_path), str(new_path))
    updated = _update_references(tex_files, old_stem, new_stem)
    return RenameResult(old_path, new_path, updated_files=updated)
