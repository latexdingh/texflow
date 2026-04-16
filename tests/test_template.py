"""Tests for template scaffolding."""
import pytest
from pathlib import Path
from click.testing import CliRunner
from texflow.template import list_templates, scaffold, BUILTIN_TEMPLATES
from texflow.template_cli import template_group


def test_list_templates_includes_builtins():
    templates = list_templates()
    for name in BUILTIN_TEMPLATES:
        assert name in templates


def test_scaffold_unknown_template(tmp_path):
    result = scaffold("nonexistent", tmp_path / "out", "Test")
    assert not result.success
    assert "not found" in result.error


def test_scaffold_article(tmp_path):
    dest = tmp_path / "myproject"
    result = scaffold("article", dest, "My Article")
    assert result.success
    main = dest / "main.tex"
    assert main.exists()
    content = main.read_text()
    assert "My Article" in content


def test_scaffold_beamer(tmp_path):
    dest = tmp_path / "slides"
    result = scaffold("beamer", dest, "My Talk")
    assert result.success
    assert (dest / "main.tex").exists()


def test_scaffold_non_empty_dest_fails(tmp_path):
    dest = tmp_path / "existing"
    dest.mkdir()
    (dest / "file.txt").write_text("x")
    result = scaffold("article", dest, "X")
    assert not result.success
    assert "not empty" in result.error


def test_cli_list():
    runner = CliRunner()
    result = runner.invoke(template_group, ["list"])
    assert result.exit_code == 0
    assert "article" in result.output


def test_cli_new(tmp_path):
    runner = CliRunner()
    dest = str(tmp_path / "proj")
    result = runner.invoke(template_group, ["new", "article", dest, "--name", "Hello"])
    assert result.exit_code == 0
    assert "created" in result.output


def test_cli_new_bad_template(tmp_path):
    runner = CliRunner()
    dest = str(tmp_path / "proj")
    result = runner.invoke(template_group, ["new", "ghost", dest])
    assert result.exit_code != 0
