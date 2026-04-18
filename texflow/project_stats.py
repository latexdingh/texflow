"""Aggregate project statistics across all source files."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from texflow.multi_file import project_files
from texflow.word_count import count_words
from texflow.outline import parse_outline
from texflow.cite_check import check_citations
from texflow.ref_check import check_refs


@dataclass
class ProjectStats:
    root: Path
    files: List[Path] = field(default_factory=list)
    total_words: int = 0
    math_envs: int = 0
    sections: int = 0
    undefined_refs: int = 0
    undefined_cites: int = 0
    unused_cites: int = 0

    def summary(self) -> str:
        lines = [
            f"Project root : {self.root}",
            f"Source files : {len(self.files)}",
            f"Total words  : {self.total_words}",
            f"Math envs    : {self.math_envs}",
            f"Sections     : {self.sections}",
            f"Undef refs   : {self.undefined_refs}",
            f"Undef cites  : {self.undefined_cites}",
            f"Unused cites : {self.unused_cites}",
        ]
        return "\n".join(lines)


def gather_stats(root: Path, bib_file: Path | None = None) -> ProjectStats:
    files = project_files(root)
    stats = ProjectStats(root=root, files=files)

    for f in files:
        wc = count_words(f)
        stats.total_words += wc.total_words
        stats.math_envs += wc.math_envs

        outline = parse_outline(f)
        stats.sections += len(outline.entries)

    ref_result = check_refs(root)
    stats.undefined_refs = len(ref_result.undefined)

    cite_result = check_citations(root, bib_file=bib_file)
    stats.undefined_cites = len(cite_result.undefined)
    stats.unused_cites = len(cite_result.unused)

    return stats
