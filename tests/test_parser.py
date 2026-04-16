"""Tests for texflow.parser."""
import pytest
from texflow.parser import parse_log, LatexError

SIMPLE_ERROR_LOG = """
(/tmp/doc.tex
! Undefined control sequence.
l.42 \\badcommand
)
"""

WARNING_LOG = """
(/tmp/doc.tex
LaTeX Warning: Citation `foo' on input line 10 undefined on input line 10.
LaTeX Warning: There were undefined references.
)
"""

MIXED_LOG = SIMPLE_ERROR_LOG + WARNING_LOG


def test_parse_error_message():
    result = parse_log(SIMPLE_ERROR_LOG)
    assert not result.ok
    assert len(result.errors) == 1
    assert "Undefined control sequence" in result.errors[0].message


def test_parse_error_line():
    result = parse_log(SIMPLE_ERROR_LOG)
    assert result.errors[0].line == 42


def test_parse_error_file():
    result = parse_log(SIMPLE_ERROR_LOG)
    assert result.errors[0].file == "/tmp/doc.tex"


def test_parse_warnings():
    result = parse_log(WARNING_LOG)
    assert result.ok
    assert len(result.warnings) == 2


def test_warning_line_number():
    result = parse_log(WARNING_LOG)
    assert result.warnings[0].line == 10


def test_mixed_log_summary():
    result = parse_log(MIXED_LOG)
    assert "1 error" in result.summary()
    assert "warning" in result.summary()


def test_clean_log():
    result = parse_log("This is pdfTeX, Version 3.14")
    assert result.ok
    assert result.summary() == "no issues"


def test_latex_error_str():
    err = LatexError(message="Bad command", line=5, file="main.tex", kind="error")
    s = str(err)
    assert "ERROR" in s
    assert "main.tex:5" in s
    assert "Bad command" in s
