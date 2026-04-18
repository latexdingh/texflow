"""Analyse inter-file dependencies in a LaTeX project."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

_INCLUDE_RE = re.compile(
    r'\\(?:input|include|subfile|subimport\{[^}]*\})\{([^}]+)\}'
)


@dataclass
class DependencyNode:
    path: Path
    depends_on: List[Path] = field(default_factory=list)

    def __str__(self) -> str:
        deps = ", ".join(p.name for p in self.depends_on)
        return f"{self.path.name} -> [{deps}]"


@dataclass
class DependencyGraph:
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return not self.nodes

    def dependents_of(self, path: Path) -> List[Path]:
        """Return all files that directly depend on *path*."""
        target = path.resolve()
        return [
            node.path
            for node in self.nodes.values()
            if target in [p.resolve() for p in node.depends_on]
        ]

    def summary(self) -> str:
        if self.is_empty():
            return "No dependency information available."
        lines = [str(node) for node in self.nodes.values()]
        return "\n".join(lines)


def _resolve_include(base: Path, raw: str) -> Path:
    p = Path(raw)
    if not p.suffix:
        p = p.with_suffix(".tex")
    return (base / p).resolve()


def build_graph(root: Path, visited: Set[Path] | None = None) -> DependencyGraph:
    """Recursively build a dependency graph starting from *root*."""
    graph = DependencyGraph()
    if visited is None:
        visited = set()

    def _visit(path: Path) -> None:
        resolved = path.resolve()
        if resolved in visited:
            return
        visited.add(resolved)
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8", errors="ignore")
        deps: List[Path] = []
        for m in _INCLUDE_RE.finditer(text):
            child = _resolve_include(path.parent, m.group(1))
            deps.append(child)
            _visit(child)
        graph.nodes[str(resolved)] = DependencyNode(path=path, depends_on=deps)

    _visit(root)
    return graph
