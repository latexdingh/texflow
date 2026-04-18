"""Tests for texflow.outline."""
from pathlib import Path
import pytest
from texflow.outline import extract_outline, OutlineEntry, Outline, SECTION_CMDS


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_empty(tmp_path):
    outline = extract_outline(tmp_path / "nope.tex")
    assert outline.is_empty()


def test_no_sections_returns_empty(tmp_path):
    p = _write(tmp_path, "Hello world\n")
    assert extract_outline(p).is_empty()


def test_single_section(tmp_path):
    p = _write(tmp_path, "\\section{Introduction}\n")
    outline = extract_outline(p)
    assert len(outline.entries) == 1
    e = outline.entries[0]
    assert e.level == "section"
    assert e.title == "Introduction"
    assert e.line == 1


def test_multiple_levels(tmp_path):
    tex = "\\section{Intro}\n\\subsection{Background}\n\\subsubsection{Detail}\n"
    outline = extract_outline(_write(tmp_path, tex))
    assert len(outline.entries) == 3
    assert [e.level for e in outline.entries] == ["section", "subsection", "subsubsection"]


def test_starred_variant(tmp_path):
    p = _write(tmp_path, "\\section*{Unnumbered}\n")
    outline = extract_outline(p)
    assert len(outline.entries) == 1
    assert outline.entries[0].title == "Unnumbered"


def test_comment_lines_skipped(tmp_path):
    tex = "% \\section{Hidden}\n\\section{Visible}\n"
    outline = extract_outline(_write(tmp_path, tex))
    assert len(outline.entries) == 1
    assert outline.entries[0].title == "Visible"


def test_depth_ordering():
    assert OutlineEntry("part", "P", 1).depth() < OutlineEntry("chapter", "C", 2).depth()
    assert OutlineEntry("section", "S", 1).depth() < OutlineEntry("subsection", "SS", 2).depth()


def test_summary_empty():
    assert Outline().summary() == "(no sections found)"


def test_summary_indentation(tmp_path):
    tex = "\\section{A}\n\\subsection{B}\n"
    summary = extract_outline(_write(tmp_path, tex)).summary()
    lines = summary.splitlines()
    assert not lines[0].startswith(" ")
    assert lines[1].startswith("  ")


def test_filter_level(tmp_path):
    tex = "\\section{S}\n\\subsection{SS}\n\\section{S2}\n"
    outline = extract_outline(_write(tmp_path, tex))
    sections = outline.filter_level("section")
    assert len(sections.entries) == 2
    assert all(e.level == "section" for e in sections.entries)
