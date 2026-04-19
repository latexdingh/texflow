"""Tests for texflow.footnote."""
from pathlib import Path
import pytest
from texflow.footnote import extract_footnotes, FootnoteResult


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_missing_file_returns_error(tmp_path):
    result = extract_footnotes(tmp_path / "nope.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_no_footnotes_returns_empty(tmp_path):
    p = _write(tmp_path, "Hello world\n")
    result = extract_footnotes(p)
    assert result.ok()
    assert result.items == []
    assert "No footnotes" in result.summary()


def test_single_footnote(tmp_path):
    p = _write(tmp_path, "Some text\\footnote{This is a note} here.\n")
    result = extract_footnotes(p)
    assert result.ok()
    assert len(result.items) == 1
    assert result.items[0].line == 1
    assert result.items[0].text == "This is a note"


def test_multiple_footnotes(tmp_path):
    content = "First\\footnote{A} and second\\footnote{B}.\n"
    p = _write(tmp_path, content)
    result = extract_footnotes(p)
    assert len(result.items) == 2
    assert result.items[0].text == "A"
    assert result.items[1].text == "B"


def test_footnote_line_number(tmp_path):
    content = "line one\nline two\\footnote{note here}\nline three\n"
    p = _write(tmp_path, content)
    result = extract_footnotes(p)
    assert result.items[0].line == 2


def test_skips_comment_lines(tmp_path):
    content = "% \\footnote{ignored}\nreal\\footnote{real note}\n"
    p = _write(tmp_path, content)
    result = extract_footnotes(p)
    assert len(result.items) == 1
    assert result.items[0].text == "real note"


def test_long_footnotes_filter(tmp_path):
    short = "short"
    long_text = "x" * 250
    content = f"\\footnote{{{short}}} and \\footnote{{{long_text}}}\n"
    p = _write(tmp_path, content)
    result = extract_footnotes(p)
    long_ones = result.long_footnotes(threshold=200)
    assert len(long_ones) == 1
    assert long_ones[0].text == long_text


def test_summary_plural(tmp_path):
    content = "\\footnote{A} \\footnote{B} \\footnote{C}\n"
    p = _write(tmp_path, content)
    result = extract_footnotes(p)
    assert "3 footnotes" in result.summary()


def test_str_repr_truncates(tmp_path):
    long_text = "w" * 100
    p = _write(tmp_path, f"\\footnote{{{long_text}}}\n")
    result = extract_footnotes(p)
    s = str(result.items[0])
    assert "..." in s
