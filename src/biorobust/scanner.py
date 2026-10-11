"""Scanner orchestration and profile selection."""

from __future__ import annotations

from pathlib import Path

from . import __version__
from .models import ScanReport
from .profiles import PROFILES, resolve_profile
from .repository import Repository
from .rules import RULE_PACK_VERSION


SCANNER_LIMITATIONS = [
    "The default scanner is static and does not import or execute target code.",
    "The scanner does not make network requests or retrieve external reference data.",
    "Heuristics can miss dynamic paths, generated files, hidden credentials, and domain-specific conventions.",
    "Evidence of repository practice is not certification of scientific correctness, clinical fitness, or security.",
]


def scan(path: str | Path, profile: str = "genomics") -> ScanReport:
    repo = Repository(Path(path))
    resolved_profile, definition = resolve_profile(repo, profile)
    findings = [check(repo) for check in definition.checks]
    notes = [
        "This report presents evidence and uncertainty; it is not a certification of scientific correctness.",
        "Unknown and manual_review findings require human or domain-specific review.",
    ]
    if profile == "auto":
        notes.append(f"Automatic profile selection chose: {resolved_profile}.")
    return ScanReport.create(
        target=str(repo.root),
        profile=resolved_profile,
        tool_version=__version__,
        rule_pack_version=RULE_PACK_VERSION,
        manifest_hash=repo.manifest_hash(),
        findings=findings,
        scanner_limitations=SCANNER_LIMITATIONS,
        notes=notes,
    )


