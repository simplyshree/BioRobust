"""Scanner orchestration and profile selection."""

from __future__ import annotations

from pathlib import Path

from . import __version__
from .checks import GENERIC_CHECKS, GENOMICS_CHECKS
from .models import ScanReport
from .repository import Repository
from .rules import RULE_PACK_VERSION


PROFILES = {"generic", "genomics", "genomics-workflow"}
SCANNER_LIMITATIONS = [
    "The default scanner is static and does not import or execute target code.",
    "The scanner does not make network requests or retrieve external reference data.",
    "Heuristics can miss dynamic paths, generated files, hidden credentials, and domain-specific conventions.",
    "Evidence of repository practice is not certification of scientific correctness, clinical fitness, or security.",
]


def scan(path: str | Path, profile: str = "genomics") -> ScanReport:
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile {profile!r}; choose from {', '.join(sorted(PROFILES))}")
    repo = Repository(Path(path))
    checks = list(GENERIC_CHECKS)
    if profile != "generic":
        checks.extend(GENOMICS_CHECKS)
    findings = [check(repo) for check in checks]
    return ScanReport.create(
        target=str(repo.root),
        profile=profile,
        tool_version=__version__,
        rule_pack_version=RULE_PACK_VERSION,
        manifest_hash=repo.manifest_hash(),
        findings=findings,
        scanner_limitations=SCANNER_LIMITATIONS,
        notes=[
            "This report presents evidence and uncertainty; it is not a certification of scientific correctness.",
            "Unknown and manual_review findings require human or domain-specific review.",
        ],
    )


