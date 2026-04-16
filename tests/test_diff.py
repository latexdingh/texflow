"""Tests for texflow.diff module."""
import pytest
from texflow.diff import compute_diff, format_diff, DiffLine


OLD = """line one
line two
line three
"""

NEW = """line one
line TWO
line three
line four
"""


def test_no_changes_empty_diff():
    result = compute_diff("same\n", "same\n")
    assert not result.has_changes


def test_added_count():
    result = compute_diff(OLD, NEW)
    assert result.added_count() >= 1


def test_removed_count():
    result = compute_diff(OLD, NEW)
    assert result.removed_count() >= 1


def test_diff_line_kinds():
    result = compute_diff(OLD, NEW)
    kinds = {dl.kind for dl in result.lines}
    assert 'added' in kinds
    assert 'removed' in kinds


def test_format_diff_no_changes():
    result = compute_diff("abc\n", "abc\n")
    assert format_diff(result, use_color=False) == "(no changes)"


def test_format_diff_contains_summary():
    result = compute_diff(OLD, NEW)
    formatted = format_diff(result, use_color=False)
    assert '+' in formatted and '-' in formatted


def test_format_diff_color_codes():
    result = compute_diff("a\n", "b\n")
    colored = format_diff(result, use_color=True)
    assert '\033[32m' in colored or '\033[31m' in colored
