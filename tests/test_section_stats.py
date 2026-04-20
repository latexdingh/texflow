"""Tests for texflow.section_stats."""
from pathlib import Path
import pytest
from texflow.section_stats import gather_section_stats


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


def test_missing_file_returns_error(tmp_path):
    result = gather_section_stats(tmp_path / "nope.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_no_sections_returns_empty(tmp_path):
    p = _write(tmp_path, "Hello world\n")
    result = gather_section_stats(p)
    assert result.ok()
    assert result.sections == []
    assert "no sections" in result.summary()


def test_single_section(tmp_path):
    p = _write(tmp_path, "\\section{Intro}\nSome words here\n")
    result = gather_section_stats(p)
    assert result.ok()
    assert len(result.sections) == 1
    s = result.sections[0]
    assert s.title == "Intro"
    assert s.level == "section"
    assert s.word_count >= 2


def test_multiple_sections(tmp_path):
    content = (
        "\\section{First}\nOne two three\n"
        "\\section{Second}\nFour five\n"
    )
    p = _write(tmp_path, content)
    result = gather_section_stats(p)
    assert len(result.sections) == 2
    assert result.sections[0].title == "First"
    assert result.sections[1].title == "Second"


def test_equation_counted(tmp_path):
    content = (
        "\\section{Math}\n"
        "\\begin{equation}\nx = 1\n\\end{equation}\n"
    )
    p = _write(tmp_path, content)
    result = gather_section_stats(p)
    assert result.sections[0].equation_count == 1


def test_subsection_level(tmp_path):
    p = _write(tmp_path, "\\subsection{Details}\nText\n")
    result = gather_section_stats(p)
    assert result.sections[0].level == "subsection"


def test_summary_includes_totals(tmp_path):
    content = "\\section{A}\nalpha beta\n\\section{B}\ngamma\n"
    p = _write(tmp_path, content)
    result = gather_section_stats(p)
    summary = result.summary()
    assert "2 section" in summary
    assert "words" in summary


def test_str_representation(tmp_path):
    p = _write(tmp_path, "\\section{Intro}\nhello world\n")
    result = gather_section_stats(p)
    s = str(result.sections[0])
    assert "Intro" in s
    assert "section" in s


def test_word_count_excludes_commands(tmp_path):
    """Words inside LaTeX commands should not inflate the word count."""
    content = (
        "\\section{Results}\n"
        "See \\cite{smith2020} and \\ref{fig:plot} for details.\n"
    )
    p = _write(tmp_path, content)
    result = gather_section_stats(p)
    # Plain words: 'See', 'and', 'for', 'details' => 4
    assert result.sections[0].word_count == 4
