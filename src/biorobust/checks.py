"""Evidence-producing checks for the MVP profiles."""

from __future__ import annotations

import re
from collections.abc import Callable

from .models import Finding
from .repository import Repository

Check = Callable[[Repository], Finding]


def _finding(
    rule_id: str,
    title: str,
    status: str,
    message: str,
    *,
    severity: str = "medium",
    evidence: list[str] | None = None,
    recommendation: str = "",
) -> Finding:
    return Finding(rule_id, title, status, severity, message, evidence or [], recommendation)


def check_readme(repo: Repository) -> Finding:
    files = repo.find("README", "README.md", "README.rst", "README.txt")
    return _finding(
        "DOC-001", "Project README", "pass" if files else "fail",
        "A project README is present." if files else "No README file was found.",
        severity="low", evidence=[repo.relative(files[0])] if files else [],
        recommendation="Document purpose, installation, inputs, outputs, and a minimal example." if not files else "",
    )


def check_license(repo: Repository) -> Finding:
    files = repo.find("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
    return _finding(
        "META-001", "Open-source license", "pass" if files else "fail",
        "A license file is present." if files else "No standard license file was found.",
        severity="high", evidence=[repo.relative(files[0])] if files else [],
        recommendation="Add a machine-readable license before publishing or reusing the software." if not files else "",
    )


def check_citation(repo: Repository) -> Finding:
    files = repo.find("CITATION.cff", "citation.cff", "codemeta.json")
    text = repo.all_text().lower()
    readme_citation = "citation" in text or "doi.org" in text
    evidence = [repo.relative(files[0])] if files else []
    if readme_citation and not evidence:
        evidence = ["repository text mentions citation/DOI"]
    return _finding(
        "META-002", "Citation metadata", "pass" if files or readme_citation else "unknown",
        "Citation metadata or a DOI reference was found." if files or readme_citation else "Citation guidance was not detected.",
        severity="low", evidence=evidence,
        recommendation="Add CITATION.cff with authors, version, repository, and DOI if available." if not files and not readme_citation else "",
    )


def check_tests(repo: Repository) -> Finding:
    files = repo.files()
    test_files = [p for p in files if p.name.startswith("test_") or p.name.endswith("_test.py") or "tests" in p.parts]
    return _finding(
        "TEST-001", "Automated tests", "pass" if test_files else "unknown",
        f"Found {len(test_files)} test-related file(s)." if test_files else "No automated test files were detected.",
        severity="medium", evidence=[repo.relative(p) for p in test_files[:5]],
        recommendation="Add a small deterministic smoke test with representative genomic inputs." if not test_files else "",
    )


def check_ci(repo: Repository) -> Finding:
    files = repo.files()
    ci = [p for p in files if ".github/workflows" in p.as_posix() or p.name.lower() in {".gitlab-ci.yml", "azure-pipelines.yml", "appveyor.yml"}]
    return _finding(
        "CI-001", "Continuous integration", "pass" if ci else "unknown",
        "Continuous-integration configuration was found." if ci else "No continuous-integration configuration was detected.",
        severity="low", evidence=[repo.relative(p) for p in ci[:5]],
        recommendation="Run tests and at least one static scan on every pull request." if not ci else "",
    )


def check_dependencies(repo: Repository) -> Finding:
    names = repo.names()
    candidates = {
        "pyproject.toml", "requirements.txt", "environment.yml", "environment.yaml", "renv.lock",
        "package.json", "package-lock.json", "pnpm-lock.yaml", "poetry.lock", "uv.lock", "pixi.toml",
        "cargo.toml", "go.mod", "mix.exs", "gemfile",
    }
    found = sorted(names & candidates)
    return _finding(
        "DEP-001", "Declared dependencies", "pass" if found else "unknown",
        "Dependency metadata was found." if found else "No common dependency declaration was detected.",
        severity="medium", evidence=found,
        recommendation="Declare runtime dependencies and their supported versions." if not found else "",
    )


def check_pinning(repo: Repository) -> Finding:
    files = repo.files()
    lock_names = {"uv.lock", "poetry.lock", "package-lock.json", "pnpm-lock.yaml", "renv.lock", "conda-lock.yml", "pixi.lock"}
    lockfiles = [p for p in files if p.name.lower() in lock_names]
    pinned_lines: list[str] = []
    for path in files:
        if path.name.lower() in {"requirements.txt", "environment.yml", "environment.yaml"}:
            for line in repo.text(path).splitlines():
                if re.search(r"(^|\s)[A-Za-z0-9_.-]+\s*(==|@|sha256:)", line):
                    pinned_lines.append(repo.relative(path))
                    break
    if lockfiles or pinned_lines:
        evidence = [repo.relative(p) for p in lockfiles] + sorted(set(pinned_lines))
        return _finding("REPRO-001", "Dependency pinning", "pass", "Pinned or lockfile-based dependencies were found.", severity="medium", evidence=evidence)
    return _finding(
        "REPRO-001", "Dependency pinning", "unknown", "Dependency versions do not appear to be pinned.", severity="medium",
        recommendation="Add a lockfile or pin the versions of runtime dependencies.",
    )


def check_secrets(repo: Repository) -> Finding:
    findings: list[str] = []
    private_key = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
    access_key = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
    assignment = re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\b\s*[:=]\s*[\"'][^\"']{8,}[\"']")
    for path in repo.files():
        if path.suffix.lower() not in {".py", ".r", ".js", ".ts", ".yaml", ".yml", ".json", ".toml", ".sh", ".env"}:
            continue
        for line_number, line in enumerate(repo.text(path).splitlines(), 1):
            if private_key.search(line) or access_key.search(line) or assignment.search(line):
                findings.append(f"{repo.relative(path)}:{line_number}")
    if findings:
        return _finding("SEC-001", "Credential exposure", "fail", "A possible hard-coded credential pattern was detected.", severity="high", evidence=findings[:10], recommendation="Remove secrets, rotate exposed credentials, and use environment or secret-manager injection.")
    return _finding("SEC-001", "Credential exposure", "pass", "No common hard-coded credential patterns were detected.", severity="high")


def check_workflow(repo: Repository) -> Finding:
    files = repo.files()
    workflows = [p for p in files if p.name.lower() in {"snakefile", "workflow.smk"} or p.suffix.lower() in {".nf", ".cwl", ".wdl"}]
    if workflows:
        kinds = sorted({"Nextflow" if p.suffix.lower() == ".nf" else "Snakemake" if p.name.lower() in {"snakefile", "workflow.smk"} else p.suffix.upper()[1:] for p in workflows})
        return _finding("DNA-WF-001", "Workflow language", "pass", f"Detected workflow definition(s): {', '.join(kinds)}.", severity="low", evidence=[repo.relative(p) for p in workflows[:10]])
    return _finding("DNA-WF-001", "Workflow language", "unknown", "No Nextflow, Snakemake, CWL, or WDL workflow definition was detected.", severity="medium", recommendation="Use a declarative workflow or document the execution order and parameters explicitly.")


def check_reference_provenance(repo: Repository) -> Finding:
    text = repo.all_text().lower()
    signals = [term for term in ("reference", "genome", "assembly", ".fasta", ".fa", "ref_fasta", "ref_fa") if term in text]
    checksums = [term for term in ("sha256", "md5", "checksum", "digest") if term in text]
    evidence = [f"genomic reference signals: {', '.join(sorted(set(signals)))}"] if signals else []
    if signals and checksums:
        evidence.append(f"integrity signals: {', '.join(checksums)}")
        return _finding("DNA-REF-001", "Reference genome provenance", "pass", "Reference genome and an integrity/provenance signal were documented.", severity="high", evidence=evidence)
    if signals:
        return _finding("DNA-REF-001", "Reference genome provenance", "unknown", "A reference genome is mentioned, but an integrity or exact-version signal was not detected.", severity="high", evidence=evidence, recommendation="Record assembly/version, source URL or accession, and a checksum for reference files.")
    return _finding("DNA-REF-001", "Reference genome provenance", "manual_review", "No reference genome declaration was detected; manual review is needed to determine whether one is required.", severity="high", recommendation="Document the reference assembly and provenance, or explicitly state that the workflow is reference-free.")


def check_genomic_validation(repo: Repository) -> Finding:
    text = repo.all_text().lower()
    data_files = [p for p in repo.files() if p.suffix.lower() in {".fastq", ".fq", ".bam", ".cram", ".vcf", ".gz"} or "test" in p.parts or "example" in p.parts]
    truth_signals = [term for term in ("truth set", "truth-set", "known answer", "expected.vcf", "expected output", "benchmark", "golden") if term in text]
    evidence = [repo.relative(p) for p in data_files[:5]] + truth_signals[:3]
    if data_files and truth_signals:
        return _finding("DNA-VAL-001", "Known-answer validation", "pass", "Representative data and a known-answer or benchmark signal were found.", severity="high", evidence=evidence)
    if data_files:
        return _finding("DNA-VAL-001", "Known-answer validation", "unknown", "Representative genomic data were found, but no expected result or truth-set signal was detected.", severity="high", evidence=evidence, recommendation="Add a small fixture and compare outputs against an expected VCF/BAM or benchmark summary.")
    return _finding("DNA-VAL-001", "Known-answer validation", "unknown", "No representative genomic fixture or known-answer test was detected.", severity="high", recommendation="Add a tiny, redistributable fixture and an expected output for a deterministic smoke test.")


def check_portability(repo: Repository) -> Finding:
    text = repo.all_text().lower()
    portability = [term for term in ("docker", "singularity", "apptainer", "conda", "micromamba", "container") if term in text]
    if portability:
        return _finding("DNA-PORT-001", "Execution portability", "pass", "A container or environment-management signal was found.", severity="medium", evidence=sorted(set(portability)))
    return _finding("DNA-PORT-001", "Execution portability", "unknown", "No container or environment-management signal was detected.", severity="medium", recommendation="Provide a container, lockfile, or reproducible environment specification.")


GENERIC_CHECKS: tuple[Check, ...] = (check_readme, check_license, check_citation, check_tests, check_ci, check_dependencies, check_pinning, check_secrets)
GENOMICS_CHECKS: tuple[Check, ...] = (check_workflow, check_reference_provenance, check_genomic_validation, check_portability)

