import pytest
from click.testing import CliRunner
from pathlib import Path
from texflow.snippet_cli import snippet_group


@pytest.fixture
def runner():
    return CliRunner()


def _tex(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "doc.tex"
    p.write_text(content, encoding="utf-8")
    return p


def test_extract_no_snippets(runner, tmp_path):
    p = _tex(tmp_path, "\\section{Hi}\n")
    result = runner.invoke(snippet_group, ["extract", str(p)])
    assert result.exit_code == 0
    assert "No snippets" in result.output


def test_extract_shows_snippet(runner, tmp_path):
    p = _tex(tmp_path, "% snippet: intro\n\\textbf{Hello}\n% end-snippet\n")
    result = runner.invoke(snippet_group, ["extract", str(p)])
    assert result.exit_code == 0
    assert "intro" in result.output


def test_extract_save_persists(runner, tmp_path):
    p = _tex(tmp_path, "% snippet: s1\nfoo\n% end-snippet\n")
    with runner.isolated_filesystem():
        result = runner.invoke(snippet_group, ["extract", str(p), "--save"])
        assert result.exit_code == 0
        assert "Saved 1" in result.output
        list_result = runner.invoke(snippet_group, ["list"])
        assert "s1" in list_result.output


def test_list_no_snippets(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(snippet_group, ["list"])
        assert result.exit_code == 0
        assert "No snippets" in result.output


def test_show_missing(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(snippet_group, ["show", "ghost"])
        assert result.exit_code != 0


def test_remove_missing(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(snippet_group, ["remove", "ghost"])
        assert result.exit_code != 0
