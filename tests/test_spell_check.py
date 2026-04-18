"""Tests for texflow.spell_check."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from texflow.spell_check import SpellIssue, SpellResult, _extract_words, check_file


# --- unit helpers ---

def test_extract_words_strips_latex_commands():
    words = _extract_words(r"\textbf{Hello} world")
    assert "Hello" in words or "hello" in words.copy()
    assert not any(w.startswith("\\") for w in words)


def test_extract_words_strips_math():
    words = _extract_words("The value $x^2 + y$ is nice")
    assert "nice" in words
    assert "x^2" not in words


def test_extract_words_strips_comments():
    words = _extract_words("Hello % this is a comment")
    assert "comment" not in words
    assert "Hello" in words


def test_extract_words_min_length():
    words = _extract_words("a an the big")
    assert "a" not in words
    assert "an" not in words
    assert "big" in words


# --- SpellResult ---

def test_spell_result_ok_when_no_issues():
    r = SpellResult(issues=[])
    assert r.ok
    assert "No spelling" in r.summary()


def test_spell_result_not_ok_with_issues():
    issue = SpellIssue(word="teh", line=3, suggestions=["the"])
    r = SpellResult(issues=[issue])
    assert not r.ok
    assert "1 spelling" in r.summary()


def test_spell_result_skipped():
    r = SpellResult(skipped=True)
    assert "skipped" in r.summary()


def test_spell_issue_str():
    issue = SpellIssue(word="teh", line=5, suggestions=["the"])
    s = str(issue)
    assert "Line 5" in s
    assert "teh" in s
    assert "the" in s


# --- check_file ---

def test_check_file_skipped_when_no_spellchecker(tmp_path):
    tex = tmp_path / "main.tex"
    tex.write_text("Hello world\n")
    with patch.dict("sys.modules", {"spellchecker": None}):
        result = check_file(tex)
    assert result.skipped


def test_check_file_missing_file(tmp_path):
    result = check_file(tmp_path / "missing.tex")
    assert result.skipped


def test_check_file_returns_issues(tmp_path):
    tex = tmp_path / "main.tex"
    tex.write_text("Ths iz a tst line\n")

    mock_spell = MagicMock()
    mock_spell.unknown.return_value = {"tst"}
    mock_spell.candidates.return_value = {"test"}

    mock_module = MagicMock()
    mock_module.SpellChecker.return_value = mock_spell

    with patch.dict("sys.modules", {"spellchecker": mock_module}):
        result = check_file(tex)

    assert not result.skipped
    assert any(i.word == "tst" for i in result.issues)
