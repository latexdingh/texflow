from pathlib import Path
import pytest
from texflow.indent_check import check_indent, IndentCheckResult


def _write(tmp_path, content):
    p = tmp_path / "main.tex"
    p.write_text(content)
    return p


def test_missing_file_returns_error(tmp_path):
    result = check_indent(tmp_path / "nope.tex")
    assert not result.ok()
    assert "not found" in result.error


def test_clean_file_returns_ok(tmp_path):
    tex = _write(tmp_path, "\\begin{document}\n  hello\n\\end{document}\n")
    result = check_indent(tex)
    assert result.ok()
    assert result.summary() == "No indentation issues found."


def test_mismatched_indent_detected(tmp_path):
    content = (
        "\\begin{itemize}\n"
        "  \\item foo\n"
        "   \\end{itemize}\n"  # three spaces vs zero
    )
    tex = _write(tmp_path, content)
    result = check_indent(tex)
    assert not result.ok()
    assert len(result.issues) == 1
    assert result.issues[0].line == 3
    assert "itemize" in result.issues[0].message


def test_matching_indent_no_issue(tmp_path):
    content = (
        "  \\begin{figure}\n"
        "    content\n"
        "  \\end{figure}\n"
    )
    tex = _write(tmp_path, content)
    result = check_indent(tex)
    assert result.ok()


def test_multiple_issues(tmp_path):
    content = (
        "\\begin{document}\n"
        "  \\begin{itemize}\n"
        "    \\item x\n"
        " \\end{itemize}\n"   # mismatch
        " \\end{document}\n"  # mismatch
    )
    tex = _write(tmp_path, content)
    result = check_indent(tex)
    assert len(result.issues) == 2
    assert "2 indentation issue(s)" in result.summary()


def test_issue_str():
    content = "\\begin{table}\n  x\n  \\end{table}\n"
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".tex", delete=False, mode="w") as f:
        f.write(content)
        name = f.name
    result = check_indent(Path(name))
    os.unlink(name)
    if result.issues:
        s = str(result.issues[0])
        assert "Line" in s
