"""Scanner orchestration and profile selection."""

from __future__ import annotations

from pathlib import Path

from . import __version__
from .checks import GENERIC_CHECKS, GENOMICS_CHECKS
from .models import ScanReport
from .repository import Repository


PROFILES = {"generic", "genomics", "genomics-workflow"}


def scan(path: str | Path, profile: str = "genomics") -> ScanReport:
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile {profile!r}; choose from {', '.join(sorted(PROFILES))}")
    repo = Repository(Path(path))
    checks = list(GENERIC_CHECKS)
    if profile != "generic":
        checks.extend(GENOMICS_CHECKS)
    findings = [check(repo) for check in checks]
    notes = [
        "This report presents evidence and uncertainty; it is not a certification of scientific correctness.",
        "Unknown and manual_review findings require human or domain-specific review.",
        "The default scanner is static and does not execute repository code.",
    ]
    return ScanReport.create(str(repo.root), profile, __version__, findings, notes)

