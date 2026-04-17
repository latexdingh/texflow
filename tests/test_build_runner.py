"""Tests for texflow.build_runner.BuildRunner."""
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

from texflow.build_runner import BuildRunner
from texflow.diff import DiffResult, DiffLine


def _make_runner(returncode=0, stdout="", pdf_exists=False):
    source = Path("main.tex")
    diff_reporter = MagicMock()
    diff_reporter.report.return_value = None
    output = []

    compile_result = types.SimpleNamespace(returncode=returncode, stdout=stdout)

    pdf_path = MagicMock(spec=Path)
    pdf_path.exists.return_value = pdf_exists

    runner = BuildRunner(
        source=source,
        diff_reporter=diff_reporter,
        use_color=False,
        print_fn=output.append,
    )
    return runner, diff_reporter, output, compile_result, pdf_path


def test_run_success_prints_succeeded():
    runner, dr, output, cr, pdf = _make_runner(returncode=0)
    with patch("texflow.build_runner.compile_latex", return_value=cr), \
         patch("texflow.build_runner.find_output_pdf", return_value=pdf), \
         patch("texflow.build_runner.parse_log") as pl:
        pl.return_value = MagicMock(errors=[], warnings=[])
        result = runner.run()
    assert result is True
    assert any("succeeded" in line for line in output)


def test_run_failure_prints_failed():
    runner, dr, output, cr, pdf = _make_runner(returncode=1)
    with patch("texflow.build_runner.compile_latex", return_value=cr), \
         patch("texflow.build_runner.find_output_pdf", return_value=pdf), \
         patch("texflow.build_runner.parse_log") as pl:
        pl.return_value = MagicMock(errors=[], warnings=[])
        result = runner.run()
    assert result is False
    assert any("failed" in line for line in output)


def test_run_prints_diff_when_available():
    runner, dr, output, cr, pdf = _make_runner(returncode=0, pdf_exists=True)
    diff = DiffResult(lines=[DiffLine(kind="added", text="hello")])
    dr.report.return_value = diff
    with patch("texflow.build_runner.compile_latex", return_value=cr), \
         patch("texflow.build_runner.find_output_pdf", return_value=pdf), \
         patch("texflow.build_runner.parse_log") as pl:
        pl.return_value = MagicMock(errors=[], warnings=[])
        runner.run()
    assert any("+" in line for line in output)


def test_run_no_diff_when_pdf_missing():
    """Diff reporter should not be called when the PDF does not exist."""
    runner, dr, output, cr, pdf = _make_runner(returncode=0, pdf_exists=False)
    with patch("texflow.build_runner.compile_latex", return_value=cr), \
         patch("texflow.build_runner.find_output_pdf", return_value=pdf), \
         patch("texflow.build_runner.parse_log") as pl:
        pl.return_value = MagicMock(errors=[], warnings=[])
        runner.run()
    dr.report.assert_not_called()


def test_preload_calls_diff_reporter():
    runner, dr, output, cr, pdf = _make_runner(pdf_exists=True)
    with patch("texflow.build_runner.find_output_pdf", return_value=pdf):
        runner.preload()
    dr.preload.assert_called_once_with(pdf)
