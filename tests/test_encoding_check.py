"""Tests for texflow.encoding_check."""
from pathlib import Path
import pytest
from texflow.encoding_check import check_encoding, EncodingCheckResult


def _write(tmp_path: Path, name: str, content: str, encoding: str = "utf-8") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding=encoding)
    return p


def test_missing_file_returns_error(tmp_path):
    result = check_encoding(tmp_path / "ghost.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_clean_file_returns_ok(tmp_path):
    p = _write(tmp_path, "clean.tex", "\\documentclass{article}\n\\begin{document}\nHello.\n\\end{document}\n")
    result = check_encoding(p)
    assert result.ok()
    assert result.summary() == "No encoding issues found."


def test_detects_smart_quote(tmp_path):
    p = _write(tmp_path, "sq.tex", "He said \u201cHello\u201d to her.\n")
    result = check_encoding(p)
    assert not result.ok()
    assert any("Smart quote" in str(i) for i in result.issues)


def test_detects_bom(tmp_path):
    p = tmp_path / "bom.tex"
    p.write_bytes(b"\xef\xbb\xbf" + b"\\documentclass{article}\n")
    result = check_encoding(p)
    assert not result.ok()
    assert any("BOM" in str(i) for i in result.issues)


def test_invalid_utf8_returns_error(tmp_path):
    p = tmp_path / "bad.tex"
    p.write_bytes(b"Hello \xff\xfe world")
    result = check_encoding(p)
    assert not result.ok()
    assert "UTF-8" in result.error


def test_detects_inputenc(tmp_path):
    p = _write(tmp_path, "enc.tex", "\\usepackage{inputenc}\n")
    result = check_encoding(p)
    assert not result.ok()
    assert any("inputenc" in str(i) for i in result.issues)


def test_summary_counts_issues(tmp_path):
    p = _write(tmp_path, "multi.tex", "\u2018one\u2019 and \u201ctwo\u201d\n")
    result = check_encoding(p)
    assert "issue" in result.summary()


def test_issue_str_format(tmp_path):
    p = _write(tmp_path, "sq2.tex", "\u2018quote\u2019\n")
    result = check_encoding(p)
    issue = result.issues[0]
    assert str(issue).startswith(str(p))
    assert ":1:" in str(issue)
