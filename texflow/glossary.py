"""Glossary term extraction and checking for LaTeX files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set


@dataclass
class GlossaryIssue:
    term: str
    kind: str  # 'undefined' | 'unused'

    def __str__(self) -> str:
        if self.kind == 'undefined':
            return f"Undefined glossary term: '{self.term}'"
        return f"Unused glossary term: '{self.term}'"


@dataclass
class GlossaryResult:
    issues: List[GlossaryIssue] = field(default_factory=list)
    defined: Set[str] = field(default_factory=set)
    used: Set[str] = field(default_factory=set)

    def ok(self) -> bool:
        return not self.issues

    def summary(self) -> str:
        if self.ok():
            return f"Glossary OK — {len(self.defined)} terms defined, {len(self.used)} used."
        undefined = sum(1 for i in self.issues if i.kind == 'undefined')
        unused = sum(1 for i in self.issues if i.kind == 'unused')
        parts = []
        if undefined:
            parts.append(f"{undefined} undefined")
        if unused:
            parts.append(f"{unused} unused")
        return "Glossary issues: " + ", ".join(parts) + "."


_DEF_PATTERN = re.compile(
    r'\\newglossaryentry\{([^}]+)\}|\\newacronym\{([^}]+)\}'
)
_USE_PATTERN = re.compile(
    r'\\(?:gls|Gls|GLS|glspl|acrshort|acrlong|acrfull)\{([^}]+)\}'
)


def _extract_defined(text: str) -> Set[str]:
    terms: Set[str] = set()
    for m in _DEF_PATTERN.finditer(text):
        terms.add(m.group(1) or m.group(2))
    return terms


def _extract_used(text: str) -> Set[str]:
    return {m.group(1) for m in _USE_PATTERN.finditer(text)}


def check_glossary(tex_path: Path, gls_path: Path | None = None) -> GlossaryResult:
    """Check glossary definitions vs usages.

    If *gls_path* is provided it is treated as the definitions file;
    otherwise definitions are extracted from *tex_path* itself.
    """
    if not tex_path.exists():
        return GlossaryResult()

    tex_text = tex_path.read_text(encoding='utf-8', errors='replace')
    def_text = gls_path.read_text(encoding='utf-8', errors='replace') if gls_path and gls_path.exists() else tex_text

    defined = _extract_defined(def_text)
    used = _extract_used(tex_text)

    issues: List[GlossaryIssue] = []
    for term in sorted(used - defined):
        issues.append(GlossaryIssue(term=term, kind='undefined'))
    for term in sorted(defined - used):
        issues.append(GlossaryIssue(term=term, kind='unused'))

    return GlossaryResult(issues=issues, defined=defined, used=used)
