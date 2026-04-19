"""Tests for texflow.package_check."""
import pytest
from pathlib import Path
from texflow.package_check import check_packages, PackageCheckResult


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


def test_missing_file_returns_error(tmp_path):
    result = check_packages(tmp_path / "missing.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_no_packages_returns_ok(tmp_path):
    p = _write(tmp_path, r"\documentclass{article}\begin{document}Hello\end{document}")
    result = check_packages(p)
    assert result.ok()
    assert result.packages == []


def test_detects_declared_packages(tmp_path):
    p = _write(tmp_path, "\\usepackage{amsmath}\n\\usepackage{graphicx}\n")
    result = check_packages(p)
    assert "amsmath" in result.packages
    assert "graphicx" in result.packages


def test_duplicate_package_detected(tmp_path):
    content = "\\usepackage{amsmath}\n\\usepackage{amsmath}\n"
    p = _write(tmp_path, content)
    result = check_packages(p)
    kinds = [i.kind for i in result.issues]
    assert "duplicate" in kinds


def test_unused_package_detected(tmp_path):
    # graphicx declared but \includegraphics never used
    p = _write(tmp_path, "\\usepackage{graphicx}\nHello world\n")
    result = check_packages(p)
    kinds = [i.kind for i in result.issues]
    assert "unused" in kinds
    assert result.issues[0].package == "graphicx"


def test_used_package_no_issue(tmp_path):
    content = "\\usepackage{graphicx}\n\\includegraphics{fig.png}\n"
    p = _write(tmp_path, content)
    result = check_packages(p)
    unused = [i for i in result.issues if i.kind == "unused"]
    assert unused == []


def test_summary_ok(tmp_path):
    content = "\\usepackage{graphicx}\n\\includegraphics{fig.png}\n"
    p = _write(tmp_path, content)
    result = check_packages(p)
    assert "no issues" in result.summary()


def test_summary_with_issues(tmp_path):
    p = _write(tmp_path, "\\usepackage{graphicx}\nHello\n")
    result = check_packages(p)
    assert "issue" in result.summary()


def test_package_issue_str():
    from texflow.package_check import PackageIssue
    issue = PackageIssue(kind="unused", package="tikz", line=3)
    assert "unused" in str(issue)
    assert "tikz" in str(issue)
    assert "3" in str(issue)
