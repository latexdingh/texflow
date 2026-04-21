"""Command palette: fuzzy-search available texflow commands with descriptions."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PaletteEntry:
    name: str
    group: str
    description: str
    usage: str = ""

    def __str__(self) -> str:
        parts = [f"{self.group} {self.name}"]
        if self.usage:
            parts.append(self.usage)
        return f"{' '.join(parts):40s}  {self.description}"


@dataclass
class PaletteResult:
    entries: List[PaletteEntry] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.entries) > 0

    def summary(self) -> str:
        if not self.entries:
            return "No matching commands found."
        return f"{len(self.entries)} command(s) matched."


_REGISTRY: List[PaletteEntry] = [
    PaletteEntry("watch", "texflow", "Watch a .tex file and hot-reload PDF on save", "<file.tex>"),
    PaletteEntry("show", "profile", "Display current build profile"),
    PaletteEntry("init", "profile", "Initialise a profile file"),
    PaletteEntry("set", "profile", "Set a profile key", "<key> <value>"),
    PaletteEntry("show", "history", "Show recent build history"),
    PaletteEntry("stats", "history", "Show build success rate stats"),
    PaletteEntry("run", "clean", "Remove LaTeX auxiliary files"),
    PaletteEntry("list", "clean", "List auxiliary files without deleting"),
    PaletteEntry("new", "template", "Scaffold a new LaTeX project from a template", "<template> <dest>"),
    PaletteEntry("list", "template", "List available templates"),
    PaletteEntry("add", "pin", "Pin the current PDF build", "<label>"),
    PaletteEntry("list", "pin", "List pinned builds"),
    PaletteEntry("remove", "pin", "Remove a pinned build", "<label>"),
    PaletteEntry("run", "export", "Export the compiled PDF", "<source.pdf>"),
    PaletteEntry("add", "remote", "Add a remote push target", "<name> <dest>"),
    PaletteEntry("push", "remote", "Push PDF to a remote target", "<name> <pdf>"),
    PaletteEntry("count", "wordcount", "Count words in a .tex file", "<file.tex>"),
    PaletteEntry("find", "search", "Search for a pattern across .tex files", "<pattern>"),
    PaletteEntry("show", "focus", "Show a focused section of a .tex file", "<file.tex> <section>"),
    PaletteEntry("check", "spell", "Spell-check a .tex file", "<file.tex>"),
    PaletteEntry("check", "cite", "Check citation keys", "<file.tex>"),
    PaletteEntry("check", "ref", "Check cross-references", "<file.tex>"),
    PaletteEntry("check", "lint", "Lint a .tex file for common issues", "<file.tex>"),
    PaletteEntry("check", "macro", "Check for unused macros", "<file.tex>"),
    PaletteEntry("check", "label", "Check labels for duplicates and unused entries", "<file.tex>"),
    PaletteEntry("check", "figure", "Check figures for missing files", "<file.tex>"),
    PaletteEntry("check", "table", "Check table column consistency", "<file.tex>"),
    PaletteEntry("check", "math", "Check math environments for balance", "<file.tex>"),
    PaletteEntry("check", "package", "Check declared packages", "<file.tex>"),
    PaletteEntry("check", "indent", "Check indentation consistency", "<file.tex>"),
    PaletteEntry("check", "encoding", "Check for encoding issues", "<file.tex>"),
    PaletteEntry("check", "duplicate", "Check for duplicate lines", "<file.tex>"),
    PaletteEntry("check", "acronym", "Check acronym definitions and usage", "<file.tex>"),
    PaletteEntry("check", "wrap", "Check line wrapping", "<file.tex>"),
    PaletteEntry("show", "stats", "Show aggregated project statistics", "<file.tex>"),
    PaletteEntry("show", "env", "Show environment and tool availability"),
    PaletteEntry("tree", "dependency", "Show file dependency tree", "<file.tex>"),
    PaletteEntry("rename", "rename", "Rename a .tex file and update references", "<old> <new>"),
    PaletteEntry("show", "abstract", "Extract and display the document abstract", "<file.tex>"),
    PaletteEntry("show", "metadata", "Show document metadata", "<file.tex>"),
    PaletteEntry("list", "hyperlink", "List hyperlinks in a .tex file", "<file.tex>"),
    PaletteEntry("list", "cross-ref", "List cross-reference labels", "<file.tex>"),
    PaletteEntry("show", "section-stats", "Show per-section word counts", "<file.tex>"),
]


def search_palette(
    query: str,
    registry: Optional[List[PaletteEntry]] = None,
    *,
    group_filter: Optional[str] = None,
) -> PaletteResult:
    """Fuzzy-search the command palette by query string.

    Matches if every whitespace-separated token in *query* appears (case-
    insensitively) in either the entry's group, name, or description.
    """
    entries = registry if registry is not None else _REGISTRY
    tokens = query.lower().split() if query.strip() else []

    matched: List[PaletteEntry] = []
    for entry in entries:
        if group_filter and entry.group.lower() != group_filter.lower():
            continue
        haystack = f"{entry.group} {entry.name} {entry.description}".lower()
        if all(tok in haystack for tok in tokens):
            matched.append(entry)

    return PaletteResult(entries=matched)
