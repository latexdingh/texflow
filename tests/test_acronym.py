"""Tests for texflow.acronym."""
from pathlib import Path
import pytest
from texflow.acronym import check_acronyms, AcronymResult


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


def test_missing_file_returns_empty(tmp_path: Path) -> None:
    result = check_acronyms(tmp_path / "missing.tex")
    assert result.ok()
    assert result.defined == {}
    assert result.used == {}


def test_no_acronyms_returns_ok(tmp_path: Path) -> None:
    p = _write(tmp_path, "Hello world\n")
    result = check_acronyms(p)
    assert result.ok()


def test_defined_and_used_no_issues(tmp_path: Path) -> None:
    content = (
        "\\newacronym{nasa}{NASA}{National Aeronautics and Space Administration}\n"
        "We reference \\ac{nasa} here.\n"
    )
    p = _write(tmp_path, content)
    result = check_acronyms(p)
    assert result.ok()
    assert "nasa" in result.defined
    assert "nasa" in result.used


def test_unused_acronym_detected(tmp_path: Path) -> None:
    content = "\\newacronym{api}{API}{Application Programming Interface}\n"
    p = _write(tmp_path, content)
    result = check_acronyms(p)
    assert not result.ok()
    kinds = [i.kind for i in result.issues]
    assert "unused" in kinds


def test_undefined_acronym_detected(tmp_path: Path) -> None:
    content = "See \\ac{rpc} for details.\n"
    p = _write(tmp_path, content)
    result = check_acronyms(p)
    assert not result.ok()
    kinds = [i.kind for i in result.issues]
    assert "undefined" in kinds


def test_comment_lines_skipped(tmp_path: Path) -> None:
    content = (
        "% \\newacronym{api}{API}{Application Programming Interface}\n"
        "% \\ac{api}\n"
    )
    p = _write(tmp_path, content)
    result = check_acronyms(p)
    assert result.ok()
    assert result.defined == {}


def test_summary_ok(tmp_path: Path) -> None:
    content = (
        "\\newacronym{pdf}{PDF}{Portable Document Format}\n"
        "\\ac{pdf} is widely used.\n"
    )
    p = _write(tmp_path, content)
    result = check_acronyms(p)
    assert "OK" in result.summary()


def test_summary_with_issues(tmp_path: Path) -> None:
    content = "\\newacronym{xml}{XML}{Extensible Markup Language}\n"
    p = _write(tmp_path, content)
    result = check_acronyms(p)
    s = result.summary()
    assert "unused" in s
