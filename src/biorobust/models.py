"""Data structures used by the scanner and report writers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


STATUSES = ("pass", "fail", "unknown", "not_applicable", "manual_review")
SEVERITIES = ("info", "low", "medium", "high")


@dataclass(slots=True)
class Finding:
    rule_id: str
    title: str
    status: str
    severity: str
    message: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"Unsupported status: {self.status}")
        if self.severity not in SEVERITIES:
            raise ValueError(f"Unsupported severity: {self.severity}")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ScanReport:
    target: str
    profile: str
    tool_version: str
    generated_at: str
    findings: list[Finding]
    notes: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls, target: str, profile: str, tool_version: str, findings: list[Finding], notes: list[str] | None = None
    ) -> "ScanReport":
        return cls(
            target=target,
            profile=profile,
            tool_version=tool_version,
            generated_at=datetime.now(timezone.utc).isoformat(),
            findings=findings,
            notes=notes or [],
        )

    @property
    def counts(self) -> dict[str, int]:
        counts = {status: 0 for status in STATUSES}
        for finding in self.findings:
            counts[finding.status] += 1
        return counts

    @property
    def decision(self) -> str:
        """A routing decision, deliberately not a quality score."""
        if self.counts["fail"]:
            return "needs_attention"
        if self.counts["unknown"] or self.counts["manual_review"]:
            return "review_required"
        if self.counts["pass"]:
            return "evidence_found"
        return "not_assessed"

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "0.1",
            "tool": {"name": "biorobust", "version": self.tool_version},
            "target": self.target,
            "profile": self.profile,
            "generated_at": self.generated_at,
            "decision": self.decision,
            "summary": self.counts,
            "findings": [finding.as_dict() for finding in self.findings],
            "notes": self.notes,
        }

