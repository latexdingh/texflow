"""Tests for environment_summary and environment_cli."""
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from texflow.environment_summary import gather_environment, EnvironmentSummary
from texflow.environment_cli import env_group
from texflow.profile import BuildProfile
from texflow.metadata import DocumentMetadata
from texflow.env_check import EnvCheckResult, ToolStatus


def _make_summary(missing: bool = False) -> EnvironmentSummary:
    tools = [ToolStatus("pdflatex", found=not missing, required=True)]
    return EnvironmentSummary(
        profile=BuildProfile(),
        metadata=DocumentMetadata(title="My Doc", author="Alice", date="2024", packages=[]),
        env=EnvCheckResult(tools=tools),
    )


def test_summary_ok_when_tools_present():
    s = _make_summary(missing=False)
    assert s.ok()


def test_summary_not_ok_when_tools_missing():
    s = _make_summary(missing=True)
    assert not s.ok()


def test_summary_string_contains_engine():
    s = _make_summary()
    text = s.summary()
    assert "pdflatex" in text


def test_summary_string_contains_title():
    s = _make_summary()
    assert "My Doc" in s.summary()


def test_gather_environment_returns_summary(tmp_path: Path):
    tex = tmp_path / "main.tex"
    tex.write_text(r"\title{Hello}\author{Bob}\begin{document}\end{document}")
    with patch("texflow.environment_summary.check_env") as mock_check:
        mock_check.return_value = EnvCheckResult(tools=[ToolStatus("pdflatex", found=True, required=True)])
        result = gather_environment(str(tex))
    assert isinstance(result, EnvironmentSummary)
    assert result.ok()


def test_cli_show_exits_zero(tmp_path: Path):
    tex = tmp_path / "main.tex"
    tex.write_text(r"\title{T}\author{A}")
    runner = CliRunner()
    with patch("texflow.environment_summary.check_env") as mock_check:
        mock_check.return_value = EnvCheckResult(tools=[ToolStatus("pdflatex", found=True, required=True)])
        result = runner.invoke(env_group, ["show", str(tex)])
    assert result.exit_code == 0


def test_cli_check_exits_nonzero_on_missing(tmp_path: Path):
    tex = tmp_path / "main.tex"
    tex.write_text("")
    runner = CliRunner()
    with patch("texflow.environment_summary.check_env") as mock_check:
        mock_check.return_value = EnvCheckResult(tools=[ToolStatus("pdflatex", found=False, required=True)])
        result = runner.invoke(env_group, ["check", str(tex)])
    assert result.exit_code != 0
    assert "pdflatex" in result.output
