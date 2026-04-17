"""Optional post-build hook: auto-export PDF after a successful compile."""
from __future__ import annotations

from pathlib import Path

from texflow.export import export_pdf, ExportResult


class ExportHook:
    """Calls export_pdf after each successful build when enabled."""

    def __init__(
        self,
        dest_dir: Path,
        name: str | None = None,
        stamp: bool = False,
        enabled: bool = True,
    ) -> None:
        self.dest_dir = dest_dir
        self.name = name
        self.stamp = stamp
        self.enabled = enabled

    def run(self, pdf_path: Path) -> ExportResult | None:
        """Export *pdf_path* if the hook is enabled. Returns None when disabled."""
        if not self.enabled:
            return None
        return export_pdf(pdf_path, self.dest_dir, name=self.name, stamp=self.stamp)

    @classmethod
    def from_profile(cls, profile: dict) -> "ExportHook":
        """Build an ExportHook from a profile dict (keys: auto_export, export_dir,
        export_name, export_stamp)."""
        return cls(
            dest_dir=Path(profile.get("export_dir", "exports")),
            name=profile.get("export_name") or None,
            stamp=bool(profile.get("export_stamp", False)),
            enabled=bool(profile.get("auto_export", False)),
        )
