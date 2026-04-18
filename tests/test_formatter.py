"""Tests for texflow.formatter."""
import pytest
from texflow.formatter import format_errors, format_diff, format_build_status
from texflow.parser import ParseResult, LatexError
from texflow.diff import DiffResult, DiffLine


def make_parse_result(errors=None, warnings=None):
    return ParseResult(errors=errors or [], warnings=warnings or [])


def make_diff(lines):
    dl = [DiffLine(kind=k, text=t) for k, t in lines]
    return DiffResult(lines=dl)


def test_format_build_status_success():
    out = format_build_status(True, "main.tex", use_color=False)
    assert "succeeded" in out
    assert "main.tex" in out


def test_format_build_status_failure():
    out = format_build_status(False, "main.tex", use_color=False)
    assert "failed" in out


def test_format_errors_empty():
    result = make_parse_result()
    assert format_errors(result, use_color=False) == ""


def test_format_errors_with_error():
    err = LatexError(message="Undefined control sequence", file="main.tex", line=10)
    result = make_parse_result(errors=[err])
    out = format_errors(result, use_color=False)
    assert "ERROR" in out
    assert "main.tex:10" in out
    assert "Undefined control sequence" in out


def test_format_errors_warning_no_line():
    warn = LatexError(message="Overfull hbox", file="main.tex", line=None)
    result = make_parse_result(warnings=[warn])
    out = format_errors(result, use_color=False)
    assert "WARN" in out
    assert "Overfull hbox" in out


def test_format_errors_multiple():
    """Multiple errors and warnings should all appear in output."""
    errors = [
        LatexError(message="Error one", file="a.tex", line=1),
        LatexError(message="Error two", file="b.tex", line=2),
    ]
    warnings = [
        LatexError(message="Warn one", file="a.tex", line=None),
    ]
    result = make_parse_result(errors=errors, warnings=warnings)
    out = format_errors(result, use_color=False)
    assert "Error one" in out
    assert "Error two" in out
    assert "Warn one" in out
    assert out.count("ERROR") == 2
    assert out.count("WARN") == 1


def test_format_diff_no_changes():
    diff = make_diff([])
    out = format_diff(diff, use_color=False)
    assert "no content changes" in out


def test_format_diff_with_changes():
    diff = make_diff([("added", "new line"), ("removed", "old line")])
    out = format_diff(diff, use_color=False)
    assert "+ new line" in out
    assert "- old line" in out
    assert "+1" in out
    assert "-1" in out
