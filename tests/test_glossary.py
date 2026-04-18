"""Tests for texflow.glossary."""
from pathlib import Path
import pytest
from texflow.glossary import check_glossary, GlossaryResult


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_missing_file_returns_empty(tmp_path):
    result = check_glossary(tmp_path / 'missing.tex')
    assert result.ok()
    assert result.defined == set()
    assert result.used == set()


def test_all_ok_same_file(tmp_path):
    tex = _write(tmp_path, 'main.tex', r"""
\newglossaryentry{latex}{name={LaTeX}, description={A typesetting system}}
\newacronym{pdf}{PDF}{Portable Document Format}
See \gls{latex} and \acrshort{pdf} for details.
""")
    result = check_glossary(tex)
    assert result.ok()
    assert 'latex' in result.defined
    assert 'pdf' in result.defined
    assert 'latex' in result.used
    assert 'pdf' in result.used


def test_undefined_term_detected(tmp_path):
    tex = _write(tmp_path, 'main.tex', r"""
\newglossaryentry{latex}{name={LaTeX}, description={A typesetting system}}
See \gls{latex} and \gls{ghost}.
""")
    result = check_glossary(tex)
    assert not result.ok()
    kinds = {i.term: i.kind for i in result.issues}
    assert kinds.get('ghost') == 'undefined'


def test_unused_term_detected(tmp_path):
    tex = _write(tmp_path, 'main.tex', r"""
\newglossaryentry{latex}{name={LaTeX}, description={A typesetting system}}
\newglossaryentry{unused}{name={Unused}, description={Never referenced}}
See \gls{latex}.
""")
    result = check_glossary(tex)
    assert not result.ok()
    kinds = {i.term: i.kind for i in result.issues}
    assert kinds.get('unused') == 'unused'


def test_separate_gls_file(tmp_path):
    gls = _write(tmp_path, 'glossary.tex', r"""
\newglossaryentry{algo}{name={Algorithm}, description={A procedure}}
""")
    tex = _write(tmp_path, 'main.tex', r"See \gls{algo}.")
    result = check_glossary(tex, gls_path=gls)
    assert result.ok()


def test_summary_ok(tmp_path):
    tex = _write(tmp_path, 'main.tex', r"""
\newglossaryentry{a}{name={A}, description={A}}
\gls{a}
""")
    result = check_glossary(tex)
    assert 'OK' in result.summary()


def test_summary_issues(tmp_path):
    tex = _write(tmp_path, 'main.tex', r"""
\newglossaryentry{defined}{name={D}, description={D}}
\gls{other}
""")
    result = check_glossary(tex)
    s = result.summary()
    assert 'undefined' in s
    assert 'unused' in s
