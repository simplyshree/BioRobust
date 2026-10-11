"""Versioned profile registry for domain-specific BioRobust checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .checks import Check, GENERIC_CHECKS, GENOMICS_CHECKS
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


GENOMIC_SUFFIXES = {
    ".fastq", ".fq", ".bam", ".cram", ".vcf", ".fa", ".fasta", ".gff", ".gtf",
}
WORKFLOW_NAMES = {"snakefile", "workflow.smk", "nextflow.config"}
WORKFLOW_SUFFIXES = {".nf", ".smk", ".cwl", ".wdl"}
BIOINFORMATICS_TEXT_NAMES = {
    "readme", "readme.md", "readme.rst", "pyproject.toml", "setup.py", "setup.cfg",
    "package.json", "environment.yml", "environment.yaml", "pixi.toml", "nextflow.config",
}
BIOINFORMATICS_MARKERS = (
    "bioinformatics", "computational genomics", "genomic analysis", "sequence analysis",
    "variant calling", "rna-seq", "rnaseq", "single-cell", "metagenomics", "sequencing",
    "fastq", "bam", "cram", "vcf", "fasta", "gff", "gtf", "genome assembly",
)


def _has_genomics_signal(repo: Repository) -> bool:
    files = repo.files()
    if any(path.suffix.lower() in GENOMIC_SUFFIXES for path in files):
        return True
    if _has_workflow_signal(repo):
        return True
    for path in files:
        if path.name.lower() not in BIOINFORMATICS_TEXT_NAMES:
            continue
        text = repo.text(path, limit=40_000).lower()
        if any(marker in text for marker in BIOINFORMATICS_MARKERS):
            return True
    return False


def _has_workflow_signal(repo: Repository) -> bool:
    return any(path.name.lower() in WORKFLOW_NAMES or path.suffix.lower() in WORKFLOW_SUFFIXES for path in repo.files())


PROFILES: dict[str, ProfileDefinition] = {
    "generic": ProfileDefinition(
        "generic",
        "Repository documentation, metadata, tests, CI, dependencies, and obvious credential patterns.",
        GENERIC_CHECKS,
        _always,
    ),
    "genomics": ProfileDefinition(
        "genomics",
        "Genomics-focused evidence for genomic repositories, sequence data, references, validation, and portability.",
        GENERIC_CHECKS + GENOMICS_CHECKS,
        _has_genomics_signal,
    ),
    "bioinformatics": ProfileDefinition(
        "bioinformatics",
        "Evidence profile for open-source bioinformatics tools and genomic repositories, including workflows, tests, references, and portability.",
        GENERIC_CHECKS + GENOMICS_CHECKS,
        _has_genomics_signal,
    ),
    "genomics-workflow": ProfileDefinition(
        "genomics-workflow",
        "Genomics profile for repositories centered on Nextflow, Snakemake, CWL, or WDL workflows.",
        GENERIC_CHECKS + GENOMICS_CHECKS,
        _has_workflow_signal,
    ),
}


def resolve_profile(repo: Repository, requested: str) -> tuple[str, ProfileDefinition]:
    """Resolve an explicit profile or choose one using narrow, explainable signals."""
    if requested == "auto":
        if _has_workflow_signal(repo):
            requested = "genomics-workflow"
        elif _has_genomics_signal(repo):
            requested = "bioinformatics"
        else:
            requested = "generic"
    try:
        return requested, PROFILES[requested]
    except KeyError as exc:
        raise ValueError(f"Unknown profile {requested!r}; choose from {', '.join(sorted(PROFILES))} or auto") from exc
