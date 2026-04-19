"""Tests for texflow.label_check."""
import pytest
from pathlib import Path
from texflow.label_check import check_labels, LabelIssue


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_no_labels_returns_ok(tmp_path):
    f = _write(tmp_path, "main.tex", "Hello world\n")
    result = check_labels([f])
    assert result.ok()
    assert result.summary() == "No label issues found."


def test_used_label_no_issue(tmp_path):
    f = _write(tmp_path, "main.tex",
               "\\label{sec:intro}\n\\ref{sec:intro}\n")
    result = check_labels([f])
    assert result.ok()


def test_unused_label_detected(tmp_path):
    f = _write(tmp_path, "main.tex", "\\label{sec:intro}\n")
    result = check_labels([f])
    assert not result.ok()
    assert any(i.kind == "unused" and i.label == "sec:intro" for i in result.issues)


def test_duplicate_label_detected(tmp_path):
    f = _write(tmp_path, "main.tex",
               "\\label{fig:1}\n\\ref{fig:1}\n\\label{fig:1}\n")
    result = check_labels([f])
    assert not result.ok()
    assert any(i.kind == "duplicate" and i.label == "fig:1" for i in result.issues)


def test_duplicate_across_files(tmp_path):
    a = _write(tmp_path, "a.tex", "\\label{eq:main}\n\\ref{eq:main}\n")
    b = _write(tmp_path, "b.tex", "\\label{eq:main}\n")
    result = check_labels([a, b])
    kinds = [i.kind for i in result.issues]
    assert "duplicate" in kinds


def test_comment_lines_ignored(tmp_path):
    f = _write(tmp_path, "main.tex", "% \\label{ghost}\n\\label{real}\n\\ref{real}\n")
    result = check_labels([f])
    assert result.ok()
    labels = [i.label for i in result.issues]
    assert "ghost" not in labels


def test_summary_shows_counts(tmp_path):
    f = _write(tmp_path, "main.tex",
               "\\label{a}\n\\label{b}\n\\label{b}\n\\ref{b}\n")
    result = check_labels([f])
    s = result.summary()
    assert "unused" in s
    assert "duplicate" in s


def test_label_issue_str():
    issue = LabelIssue("unused", "sec:x", "main.tex", 5)
    assert "unused" in str(issue)
    assert "sec:x" in str(issue)
    assert "main.tex:5" in str(issue)


def test_missing_file_handled_gracefully(tmp_path):
    missing = tmp_path / "ghost.tex"
    result = check_labels([missing])
    assert result.ok()
