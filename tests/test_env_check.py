"""Tests for texflow.env_check."""
from unittest.mock import patch

import pytest

from texflow.env_check import (
    EnvCheckResult,
    ToolStatus,
    check_environment,
)


def _fake_which(present):
    """Return a shutil.which stub that finds only tools in *present*."""
    def _which(name):
        return f"/usr/bin/{name}" if name in present else None
    return _which


def test_tool_status_found():
    ts = ToolStatus(name="pdflatex", found=True, path="/usr/bin/pdflatex")
    assert "ok" in str(ts)
    assert "pdflatex" in str(ts)


def test_tool_status_missing():
    ts = ToolStatus(name="biber", found=False)
    assert "missing" in str(ts)


def test_check_all_present():
    tools = ["pdflatex", "bibtex"]
    with patch("texflow.env_check.shutil.which", side_effect=_fake_which(tools)):
        result = check_environment(required=tools, optional=[])
    assert result.ok
    assert result.missing_required == []


def test_check_some_missing():
    with patch("texflow.env_check.shutil.which", side_effect=_fake_which(["pdflatex"])):
        result = check_environment(required=["pdflatex", "xelatex"], optional=[])
    assert not result.ok
    assert "xelatex" in result.missing_required


def test_optional_missing_does_not_fail():
    with patch("texflow.env_check.shutil.which", side_effect=_fake_which(["pdflatex"])):
        result = check_environment(required=["pdflatex"], optional=["latexmk"])
    assert result.ok
    assert not result.optional[0].found


def test_summary_ok():
    with patch("texflow.env_check.shutil.which", side_effect=_fake_which(["pdflatex"])):
        result = check_environment(required=["pdflatex"], optional=[])
    summary = result.summary()
    assert "All required tools" in summary


def test_summary_missing():
    with patch("texflow.env_check.shutil.which", return_value=None):
        result = check_environment(required=["pdflatex"], optional=[])
    summary = result.summary()
    assert "Missing required tools" in summary
    assert "pdflatex" in summary
