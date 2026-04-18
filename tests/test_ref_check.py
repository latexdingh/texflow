"""Tests for texflow.ref_check."""
import pytest
from pathlib import Path
from texflow.ref_check import check_refs, RefCheckResult, _extract_labels, _extract_refs


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_extract_labels_basic():
    text = r"\label{fig:one} some text \label{eq:two}"
    assert _extract_labels(text) == {"fig:one", "eq:two"}


def test_extract_refs_variants():
    text = r"\ref{fig:one} \eqref{eq:two} \cref{sec:three,sec:four}"
    assert _extract_refs(text) == {"fig:one", "eq:two", "sec:three", "sec:four"}


def test_all_ok(tmp_path):
    tex = _write(tmp_path, "main.tex",
        r"\label{fig:a} See \ref{fig:a}.")
    result = check_refs(tex)
    assert result.ok
    assert result.summary() == "all refs OK"


def test_undefined_ref(tmp_path):
    tex = _write(tmp_path, "main.tex",
        r"See \ref{fig:missing}.")
    result = check_refs(tex)
    assert not result.ok
    assert "fig:missing" in result.undefined_refs
    assert "undefined" in result.summary()


def test_unused_label(tmp_path):
    tex = _write(tmp_path, "main.tex",
        r"\label{fig:orphan} No refs here.")
    result = check_refs(tex)
    assert not result.ok
    assert "fig:orphan" in result.unused_labels
    assert "unused" in result.summary()


def test_comments_ignored(tmp_path):
    tex = _write(tmp_path, "main.tex",
        "% \\label{fig:commented}\n\\label{fig:real} \\ref{fig:real}")
    result = check_refs(tex)
    assert result.ok
    assert "fig:commented" not in result.unused_labels


def test_extra_files_combined(tmp_path):
    main = _write(tmp_path, "main.tex", r"\ref{fig:b}")
    extra = _write(tmp_path, "chap.tex", r"\label{fig:b}")
    result = check_refs(main, extra_files=[extra])
    assert result.ok


def test_missing_file_skipped(tmp_path):
    tex = _write(tmp_path, "main.tex", r"\label{fig:x} \ref{fig:x}")
    result = check_refs(tex, extra_files=[tmp_path / "ghost.tex"])
    assert result.ok


def test_str_output(tmp_path):
    tex = _write(tmp_path, "main.tex", r"\ref{missing} \label{orphan}")
    result = check_refs(tex)
    out = str(result)
    assert "missing" in out
    assert "orphan" in out
