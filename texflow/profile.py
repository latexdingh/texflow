"""Build profile configuration for texflow."""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional

DEFAULT_PROFILE_FILE = ".texflow.json"


@dataclass
class BuildProfile:
    engine: str = "pdflatex"
    output_dir: str = "."
    extra_args: list[str] = field(default_factory=list)
    watch_extensions: list[str] = field(default_factory=lambda: [".tex", ".bib", ".sty"])
    max_runs: int = 2

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "BuildProfile":
        return BuildProfile(
            engine=data.get("engine", "pdflatex"),
            output_dir=data.get("output_dir", "."),
            extra_args=data.get("extra_args", []),
            watch_extensions=data.get("watch_extensions", [".tex", ".bib", ".sty"]),
            max_runs=data.get("max_runs", 2),
        )


def load_profile(path: str = DEFAULT_PROFILE_FILE) -> BuildProfile:
    if not os.path.exists(path):
        return BuildProfile()
    with open(path, "r") as f:
        data = json.load(f)
    return BuildProfile.from_dict(data)


def save_profile(profile: BuildProfile, path: str = DEFAULT_PROFILE_FILE) -> None:
    with open(path, "w") as f:
        json.dump(profile.to_dict(), f, indent=2)
    print(f"Profile saved to {path}")
