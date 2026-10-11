"""Strict, serializable data structures for evidence-bearing reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


STATUSES = ("pass", "fail", "unknown", "not_applicable", "manual_review")
SEVERITIES = ("info", "low", "medium", "high")
EVIDENCE_TYPES = ("artifact", "declaration", "documentation", "test", "absence", "contradictory")
DECISIONS = ("needs_attention", "review_required", "evidence_found", "not_assessed")


@dataclass(slots=True)
class Evidence:
    """A bounded observation that supports or limits a finding."""

    path: str | None
    observation: str
    evidence_type: str
    detector_confidence: float
    start_line: int | None = None
    end_line: int | None = None

    def __post_init__(self) -> None:
        if self.evidence_type not in EVIDENCE_TYPES:
            raise ValueError(f"Unsupported evidence type: {self.evidence_type}")
        if not 0.0 <= self.detector_confidence <= 1.0:
            raise ValueError("detector_confidence must be between 0 and 1")
        if self.start_line is not None and self.start_line < 1:
            raise ValueError("start_line must be positive")
        if self.end_line is not None and self.end_line < 1:
            raise ValueError("end_line must be positive")
        if self.start_line and self.end_line and self.end_line < self.start_line:
            raise ValueError("end_line must not precede start_line")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Finding:
    rule_id: str
    title: str
    claim: str
    status: str
    severity: str
    confidence: float
    message: str
    evidence: list[Evidence] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    recommendation: str = ""

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"Unsupported status: {self.status}")
        if self.severity not in SEVERITIES:
            raise ValueError(f"Unsupported severity: {self.severity}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.evidence:
            self.evidence.append(
                Evidence(
                    path=None,
                    observation="No repository evidence was found for this finding.",
                    evidence_type="absence",
                    detector_confidence=0.95,
                )
            )

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "claim": self.claim,
            "status": self.status,
            "severity": self.severity,
            "confidence": self.confidence,
            "message": self.message,
            "evidence": [item.as_dict() for item in self.evidence],
            "limitations": list(self.limitations),
            "recommendation": self.recommendation,
        }


@dataclass(slots=True)
class ScanReport:
    target: str
    profile: str
    tool_version: str
    rule_pack_version: str
    generated_at: str
    manifest_hash: str
    findings: list[Finding]
    scanner_limitations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        target: str,
        profile: str,
        tool_version: str,
        rule_pack_version: str,
        manifest_hash: str,
        findings: list[Finding],
        scanner_limitations: list[str] | None = None,
        notes: list[str] | None = None,
        generated_at: str | None = None,
    ) -> "ScanReport":
        return cls(
            target=target,
            profile=profile,
            tool_version=tool_version,
            rule_pack_version=rule_pack_version,
            generated_at=generated_at or datetime.now(timezone.utc).isoformat(),
            manifest_hash=manifest_hash,
            findings=findings,
            scanner_limitations=scanner_limitations or [],
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
            "schema_version": "0.2",
            "tool": {"name": "biorobust", "version": self.tool_version},
            "target": self.target,
            "profile": self.profile,
            "generated_at": self.generated_at,
            "rule_pack_version": self.rule_pack_version,
            "manifest_hash": self.manifest_hash,
            "decision": self.decision,
            "summary": self.counts,
            "findings": [finding.as_dict() for finding in self.findings],
            "scanner_limitations": list(self.scanner_limitations),
            "notes": list(self.notes),
        }


