"""Summarise the full project environment: engine, packages, and tool availability."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from texflow.env_check import check_env, EnvCheckResult
from texflow.metadata import extract_metadata, DocumentMetadata
from texflow.profile import load_profile, BuildProfile


@dataclass
class EnvironmentSummary:
    profile: BuildProfile
    metadata: DocumentMetadata
    env: EnvCheckResult
    warnings: List[str] = field(default_factory=list)

    def ok(self) -> bool:
        return self.env.ok()

    def summary(self) -> str:
        lines = [
            f"Engine  : {self.profile.engine}",
            f"Title   : {self.metadata.title or '(none)'}",
            f"Author  : {self.metadata.author or '(none)'}",
            f"Env OK  : {self.ok()}",
        ]
        missing = self.env.missing_required()
        if missing:
            lines.append("Missing : " + ", ".join(t.name for t in missing))
        if self.warnings:
            for w in self.warnings:
                lines.append(f"Warning : {w}")
        return "\n".join(lines)


def gather_environment(tex_file: str, profile_path: str | None = None) -> EnvironmentSummary:
    profile = load_profile(profile_path) if profile_path else BuildProfile()
    metadata = extract_metadata(tex_file)
    env = check_env()
    warnings: list[str] = []
    if not metadata.ok():
        warnings.append("Could not extract document metadata.")
    return EnvironmentSummary(profile=profile, metadata=metadata, env=env, warnings=warnings)
