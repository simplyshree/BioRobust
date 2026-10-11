"""Versioned profile registry for domain-specific BioRobust checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .checks import Check, GENERIC_CHECKS, GENOMICS_CHECKS, SBOL_CHECKS
from .repository import Repository


@dataclass(frozen=True, slots=True)
class ProfileDefinition:
    """A named collection of checks with a conservative repository detector."""

    name: str
    description: str
    checks: tuple[Check, ...]
    detector: Callable[[Repository], bool]


def _always(_: Repository) -> bool:
    return True


def _has_genomics_signal(repo: Repository) -> bool:
    suffixes = {".fastq", ".fq", ".bam", ".cram", ".vcf", ".fa", ".fasta", ".gff", ".gtf", ".nf", ".cwl", ".wdl"}
    names = {path.name.lower() for path in repo.files()}
    if any(path.suffix.lower() in suffixes for path in repo.files()):
        return True
    return bool(names & {"snakefile", "workflow.smk", "nextflow.config"})


def _has_sbol_signal(repo: Repository) -> bool:
    suffixes = {".sbol", ".sbol2", ".sbol3"}
    for path in repo.files():
        if path.suffix.lower() in suffixes:
            return True
        if path.suffix.lower() in {".xml", ".json", ".ttl", ".rdf"}:
            text = repo.text(path, limit=80_000).lower()
            if "sbols.org" in text or "sbol3" in text or "sbol 3" in text or "sbol2" in text or "sbol 2" in text:
                return True
    return False


PROFILES: dict[str, ProfileDefinition] = {
    "generic": ProfileDefinition(
        "generic",
        "Repository documentation, metadata, tests, CI, dependencies, and obvious credential patterns.",
        GENERIC_CHECKS,
        _always,
    ),
    "genomics": ProfileDefinition(
        "genomics",
        "Generic repository checks plus evidence for genomic workflows, references, validation, and portability.",
        GENERIC_CHECKS + GENOMICS_CHECKS,
        _has_genomics_signal,
    ),
    "genomics-workflow": ProfileDefinition(
        "genomics-workflow",
        "Genomics profile intended for repositories centered on a declarative workflow.",
        GENERIC_CHECKS + GENOMICS_CHECKS,
        _has_genomics_signal,
    ),
    "sbol": ProfileDefinition(
        "sbol",
        "Generic repository checks plus conservative SBOL artifact, serialization, validation, and interoperability signals.",
        GENERIC_CHECKS + SBOL_CHECKS,
        _has_sbol_signal,
    ),
}


def resolve_profile(repo: Repository, requested: str) -> tuple[str, ProfileDefinition]:
    """Resolve an explicit profile or choose one using narrow, explainable signals."""
    if requested == "auto":
        if _has_sbol_signal(repo):
            requested = "sbol"
        elif _has_genomics_signal(repo):
            requested = "genomics"
        else:
            requested = "generic"
    try:
        return requested, PROFILES[requested]
    except KeyError as exc:
        raise ValueError(f"Unknown profile {requested!r}; choose from {', '.join(sorted(PROFILES))} or auto") from exc
