"""Tests for BuildProfile loading and saving."""
import json
import os
import pytest
from texflow.profile import BuildProfile, load_profile, save_profile


def test_default_profile():
    p = BuildProfile()
    assert p.engine == "pdflatex"
    assert p.max_runs == 2
    assert ".tex" in p.watch_extensions


def test_from_dict_partial():
    p = BuildProfile.from_dict({"engine": "xelatex"})
    assert p.engine == "xelatex"
    assert p.max_runs == 2


def test_to_dict_roundtrip():
    p = BuildProfile(engine="lualatex", max_runs=3, extra_args=["-shell-escape"])
    d = p.to_dict()
    p2 = BuildProfile.from_dict(d)
    assert p2.engine == "lualatex"
    assert p2.max_runs == 3
    assert p2.extra_args == ["-shell-escape"]


def test_load_profile_missing_file(tmp_path):
    path = str(tmp_path / "nonexistent.json")
    p = load_profile(path)
    assert p.engine == "pdflatex"


def test_save_and_load_profile(tmp_path):
    path = str(tmp_path / "profile.json")
    p = BuildProfile(engine="xelatex", output_dir="build", max_runs=1)
    save_profile(p, path)
    assert os.path.exists(path)
    loaded = load_profile(path)
    assert loaded.engine == "xelatex"
    assert loaded.output_dir == "build"
    assert loaded.max_runs == 1


def test_save_profile_json_structure(tmp_path):
    path = str(tmp_path / "profile.json")
    p = BuildProfile(extra_args=["-interaction=nonstopmode"])
    save_profile(p, path)
    with open(path) as f:
        data = json.load(f)
    assert data["extra_args"] == ["-interaction=nonstopmode"]
