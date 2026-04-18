"""Tests for texflow.cite_check."""
from pathlib import Path
import pytest
from texflow.cite_check import (
    _extract_cite_keys,
    _extract_bib_keys,
    check_citations,
    CiteCheckResult,
)


TEX = r"""
\documentclass{article}
\begin{document}
See \cite{knuth1984} and \citep{lamport1994, knuth1984}.
Also \citet{einstein1905}.
\end{document}
"""

BIB = """
@book{knuth1984,
  title={The TeXbook},
}
@article{lamport1994,
  title={LaTeX},
}
@misc{unused_entry,
  title={Not cited},
}
"""


def test_extract_cite_keys():
    keys = _extract_cite_keys(TEX)
    assert keys == {"knuth1984", "lamport1994", "einstein1905"}


def test_extract_bib_keys():
    keys = _extract_bib_keys(BIB)
    assert keys == {"knuth1984", "lamport1994", "unused_entry"}


def test_check_citations_undefined_and_unused(tmp_path: Path):
    tex = tmp_path / "main.tex"
    bib = tmp_path / "refs.bib"
    tex.write_text(TEX)
    bib.write_text(BIB)

    result = check_citations(tex, bib)
    assert "einstein1905" in result.undefined
    assert "unused_entry" in result.unused
    assert not result.ok


def test_check_citations_all_ok(tmp_path: Path):
    tex = tmp_path / "main.tex"
    bib = tmp_path / "refs.bib"
    tex.write_text(r"\cite{alpha}")
    bib.write_text("@article{alpha, title={A},}")

    result = check_citations(tex, bib)
    assert result.ok
    assert result.summary() == "All citations OK"


def test_check_citations_auto_discovers_bib(tmp_path: Path):
    tex = tmp_path / "main.tex"
    bib = tmp_path / "auto.bib"
    tex.write_text(r"\cite{beta}")
    bib.write_text("@article{beta, title={B},}")

    result = check_citations(tex)  # no explicit bib_path
    assert result.ok


def test_check_citations_missing_tex(tmp_path: Path):
    result = check_citations(tmp_path / "ghost.tex")
    assert result.ok


def test_summary_string():
    r = CiteCheckResult(undefined=["a", "b"], unused=["c"])
    s = r.summary()
    assert "undefined" in s
    assert "unused" in s
