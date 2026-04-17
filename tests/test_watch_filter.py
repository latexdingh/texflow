"""Tests for WatchFilter."""
import pytest
from texflow.watch_filter import WatchFilter, _match_pattern


@pytest.fixture
def wf():
    return WatchFilter()


def test_tex_file_accepted(wf):
    assert wf.should_process("document.tex") is True


def test_bib_file_accepted(wf):
    assert wf.should_process("refs.bib") is True


def test_pdf_file_rejected(wf):
    assert wf.should_process("output.pdf") is False


def test_py_file_rejected(wf):
    assert wf.should_process("script.py") is False


def test_git_dir_ignored(wf):
    assert wf.should_process(".git/config") is False


def test_nested_ignored_dir(wf):
    assert wf.should_process("project/__pycache__/main.tex") is False


def test_custom_extension(wf):
    wf.add_extension(".ltx")
    assert wf.should_process("main.ltx") is True


def test_add_extension_without_dot(wf):
    wf.add_extension("tikz")
    assert ".tikz" in wf.watch_extensions


def test_ignore_custom_dir(wf):
    wf.ignore_dir("vendor")
    assert wf.should_process("vendor/pkg.tex") is False


def test_ignore_pattern_prefix(wf):
    wf.ignore_pattern("tmp*")
    assert wf.should_process("tmpfile.tex") is False
    assert wf.should_process("main.tex") is True


def test_ignore_pattern_suffix(wf):
    wf.ignore_pattern("*_draft.tex")
    assert wf.should_process("chapter_draft.tex") is False
    assert wf.should_process("chapter_final.tex") is True


def test_ignore_pattern_contains(wf):
    wf.ignore_pattern("*backup*")
    assert wf.should_process("main_backup_v2.tex") is False


def test_match_pattern_exact():
    assert _match_pattern("main.tex", "main.tex") is True
    assert _match_pattern("other.tex", "main.tex") is False
