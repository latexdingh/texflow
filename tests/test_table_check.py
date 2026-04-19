"""Tests for texflow.table_check."""
from pathlib import Path
import pytest
from texflow.table_check import check_tables, TableCheckResult


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "doc.tex"
    p.write_text(content)
    return p


def test_missing_file_returns_empty(tmp_path):
    result = check_tables(tmp_path / "nope.tex")
    assert result.ok()
    assert result.table_count == 0


def test_no_tables_returns_ok(tmp_path):
    p = _write(tmp_path, "Just some text, no tables.\n")
    result = check_tables(p)
    assert result.ok()
    assert result.table_count == 0


def test_valid_table_no_issues(tmp_path):
    content = (
        "\\begin{tabular}{lll}\n"
        "A & B & C \\\\\n"
        "1 & 2 & 3 \\\\\n"
        "\\end{tabular}\n"
    )
    result = check_tables(_write(tmp_path, content))
    assert result.ok()
    assert result.table_count == 1


def test_mismatched_columns_detected(tmp_path):
    content = (
        "\\begin{tabular}{ll}\n"
        "A & B & C \\\\\n"
        "\\end{tabular}\n"
    )
    result = check_tables(_write(tmp_path, content))
    assert not result.ok()
    assert len(result.issues) == 1
    assert "3" in result.issues[0].message
    assert "2" in result.issues[0].message


def test_multiple_tables_counted(tmp_path):
    content = (
        "\\begin{tabular}{l}\nA \\\\\n\\end{tabular}\n"
        "\\begin{tabular}{ll}\nA & B \\\\\n\\end{tabular}\n"
    )
    result = check_tables(_write(tmp_path, content))
    assert result.ok()
    assert result.table_count == 2


def test_summary_ok(tmp_path):
    p = _write(tmp_path, "\\begin{tabular}{l}\nA \\\\\n\\end{tabular}\n")
    result = check_tables(p)
    assert "OK" in result.summary()


def test_summary_issues(tmp_path):
    content = "\\begin{tabular}{l}\nA & B \\\\\n\\end{tabular}\n"
    result = check_tables(_write(tmp_path, content))
    assert "issue" in result.summary()
