"""Static, evidence-producing checks for the BioRobust profiles."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Iterable
from pathlib import Path

from .models import Evidence, Finding
from .repository import Repository

Check = Callable[[Repository], Finding]

LIMITATION_STATIC = "Static inspection does not execute target code or establish scientific correctness."
GENERIC_LIMITATIONS = (LIMITATION_STATIC,)
GENOMICS_LIMITATIONS = (LIMITATION_STATIC, "Domain judgment is required to determine whether the chosen data and reference are scientifically appropriate.")


def _line_number(text: str, needle: str) -> int | None:
    index = text.find(needle)
    return None if index < 0 else text.count("\n", 0, index) + 1


def _evidence(
    repo: Repository,
    path: Path | str | None,
    observation: str,
    evidence_type: str,
    confidence: float = 0.9,
    start_line: int | None = None,
    end_line: int | None = None,
) -> Evidence:
    return Evidence(
        path=repo.relative(path) if isinstance(path, Path) else path,
        observation=observation,
        evidence_type=evidence_type,
        detector_confidence=confidence,
        start_line=start_line,
        end_line=end_line,
    )


def _absence(observation: str, confidence: float = 0.9) -> Evidence:
    return Evidence(path=None, observation=observation, evidence_type="absence", detector_confidence=confidence)


def _finding(
    rule_id: str,
    title: str,
    claim: str,
    status: str,
    severity: str,
    confidence: float,
    message: str,
    *,
    evidence: list[Evidence] | None = None,
    limitations: Iterable[str] = GENERIC_LIMITATIONS,
    recommendation: str = "",
) -> Finding:
    return Finding(
        rule_id=rule_id,
        title=title,
        claim=claim,
        status=status,
        severity=severity,
        confidence=confidence,
        message=message,
        evidence=evidence or [_absence("No repository evidence was found for this criterion.")],
        limitations=list(limitations),
        recommendation=recommendation,
    )


def check_readme(repo: Repository) -> Finding:
    files = repo.find("README", "README.md", "README.rst", "README.txt")
    return _finding(
        "DOC-001", "Project README", "The repository explains how to use the project.",
        "pass" if files else "fail", "low", 0.99 if files else 0.98,
        "A project README is present." if files else "No README file was found.",
        evidence=[_evidence(repo, files[0], "A conventional README file exists.", "artifact")] if files else [_absence("No conventional README file was found.")],
        recommendation="Document purpose, installation, inputs, outputs, and a minimal example." if not files else "",
    )


def check_license(repo: Repository) -> Finding:
    files = repo.find("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
    return _finding(
        "META-001", "Open-source license", "The repository declares a license artifact.",
        "pass" if files else "fail", "high", 0.99 if files else 0.98,
        "A license file is present." if files else "No standard license file was found.",
        evidence=[_evidence(repo, files[0], "A standard license filename exists.", "artifact")] if files else [_absence("No standard license file was found.")],
        recommendation="Add a machine-readable license before publishing or reusing the software." if not files else "",
    )


def check_citation(repo: Repository) -> Finding:
    files = repo.find("CITATION.cff", "citation.cff", "codemeta.json")
    text_files = [path for path in repo.files() if path.name.lower().startswith("readme") or path.name.lower() in {"codemeta.json"}]
    citation_path = files[0] if files else None
    citation_text = repo.text(citation_path).lower() if citation_path else ""
    readme_hit = next((path for path in text_files if "citation" in repo.text(path).lower() or "doi.org" in repo.text(path).lower()), None)
    if citation_path:
        evidence = [_evidence(repo, citation_path, "Citation metadata artifact detected.", "artifact")]
        message = "Citation metadata was found."
        status = "pass"
    elif readme_hit:
        line = _line_number(repo.text(readme_hit).lower(), "citation") or _line_number(repo.text(readme_hit).lower(), "doi.org")
        evidence = [_evidence(repo, readme_hit, "Documentation mentions citation or DOI guidance.", "documentation", start_line=line)]
        message = "Documentation mentions citation or a DOI."
        status = "pass"
    else:
        evidence = [_absence("No citation artifact or DOI guidance was detected.")]
        message = "Citation guidance was not detected."
        status = "unknown"
    return _finding(
        "META-002", "Citation metadata", "The repository provides a citation signal.", status, "low", 0.9 if status == "pass" else 0.75,
        message, evidence=evidence,
        recommendation="Add CITATION.cff with authors, version, repository, and DOI if available." if status != "pass" else "",
    )


def check_tests(repo: Repository) -> Finding:
    files = repo.files()
    test_files = [p for p in files if p.name.startswith("test_") or p.name.endswith("_test.py") or any(part.lower() in {"test", "tests"} for part in repo.relative(p).split("/"))]
    evidence = [_evidence(repo, path, "Test-related artifact detected.", "test") for path in test_files[:8]]
    if not evidence:
        evidence = [_absence("No automated test files or test directory was detected.")]
    return _finding(
        "TEST-001", "Automated tests", "The repository contains test artifacts.", "pass" if test_files else "unknown", "medium", 0.92 if test_files else 0.75,
        f"Found {len(test_files)} test-related file(s)." if test_files else "No automated test files were detected.",
        evidence=evidence, recommendation="Add a small deterministic smoke test with representative genomic inputs." if not test_files else "",
    )


def check_ci(repo: Repository) -> Finding:
    ci = [p for p in repo.files() if ".github/workflows" in p.as_posix() or p.name.lower() in {".gitlab-ci.yml", "azure-pipelines.yml", "appveyor.yml"}]
    evidence = [_evidence(repo, path, "Continuous-integration configuration detected.", "declaration") for path in ci[:5]] or [_absence("No common continuous-integration configuration was detected.")]
    return _finding(
        "CI-001", "Continuous integration", "The repository declares an automation configuration.", "pass" if ci else "unknown", "low", 0.96 if ci else 0.75,
        "Continuous-integration configuration was found." if ci else "No continuous-integration configuration was detected.",
        evidence=evidence, recommendation="Run tests and at least one static scan on every pull request." if not ci else "",
    )


DEPENDENCY_NAMES = {
    "pyproject.toml", "requirements.txt", "environment.yml", "environment.yaml", "renv.lock", "package.json",
    "package-lock.json", "pnpm-lock.yaml", "poetry.lock", "uv.lock", "pixi.toml", "pixi.lock", "cargo.toml", "go.mod", "mix.exs", "gemfile",
}
LOCK_NAMES = {"uv.lock", "poetry.lock", "package-lock.json", "pnpm-lock.yaml", "renv.lock", "conda-lock.yml", "pixi.lock"}


def check_dependencies(repo: Repository) -> Finding:
    found = sorted(repo.names() & DEPENDENCY_NAMES)
    evidence = [_evidence(repo, next(path for path in repo.files() if path.name.lower() == name), "Dependency manifest detected.", "declaration") for name in found]
    if not evidence:
        evidence = [_absence("No common dependency declaration was detected.")]
    return _finding(
        "DEP-001", "Declared dependencies", "Runtime dependencies are declared.", "pass" if found else "unknown", "medium", 0.95 if found else 0.75,
        "Dependency metadata was found." if found else "No common dependency declaration was detected.", evidence=evidence,
        recommendation="Declare runtime dependencies and their supported versions." if not found else "",
    )


def _pinned_dependency_evidence(repo: Repository) -> list[Evidence]:
    evidence: list[Evidence] = []
    for path in repo.files():
        if path.name.lower() in LOCK_NAMES:
            evidence.append(_evidence(repo, path, "Lockfile artifact detected.", "artifact"))
            continue
        if path.name.lower() not in {"requirements.txt", "environment.yml", "environment.yaml"}:
            continue
        for line_number, line in enumerate(repo.text(path).splitlines(), 1):
            if re.search(r"^\s*[A-Za-z0-9_.-]+\s*(==|===|@\s*[^\s]+|sha256:)", line):
                evidence.append(_evidence(repo, path, f"Exact dependency constraint: {line.strip()}", "declaration", start_line=line_number, end_line=line_number))
    return evidence


def check_pinning(repo: Repository) -> Finding:
    evidence = _pinned_dependency_evidence(repo)
    if evidence:
        return _finding("REPRO-001", "Dependency pinning", "Some dependency versions are constrained reproducibly.", "pass", "medium", 0.96, "Pinned or lockfile-based dependencies were found.", evidence=evidence)
    return _finding("REPRO-001", "Dependency pinning", "Some dependency versions are constrained reproducibly.", "unknown", "medium", 0.75, "Dependency versions do not appear to be pinned.", recommendation="Add a lockfile or pin the versions of runtime dependencies.")


PLACEHOLDER_VALUES = ("example", "changeme", "change-me", "replace-me", "your_", "your-", "dummy", "test-secret", "${", "os.getenv", "getenv(")


def check_secrets(repo: Repository) -> Finding:
    findings: list[Evidence] = []
    private_key = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
    access_key = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
    assignment = re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\b\s*[:=]\s*[\"']([^\"']{8,})[\"']")
    source_suffixes = {".py", ".r", ".js", ".ts", ".yaml", ".yml", ".json", ".toml", ".sh", ".env"}
    for path in repo.files():
        if path.suffix.lower() not in source_suffixes:
            continue
        for line_number, line in enumerate(repo.text(path).splitlines(), 1):
            match = assignment.search(line)
            value = match.group(2).lower() if match else ""
            if value and any(marker in value for marker in PLACEHOLDER_VALUES):
                continue
            if private_key.search(line) or access_key.search(line) or match:
                findings.append(_evidence(repo, path, "Possible hard-coded credential pattern detected.", "contradictory", 0.96, line_number, line_number))
    if findings:
        return _finding("SEC-001", "Credential exposure", "No obvious hard-coded credential pattern was detected.", "fail", "high", 0.96, "A possible hard-coded credential pattern was detected.", evidence=findings[:10], recommendation="Remove secrets, rotate exposed credentials, and use environment or secret-manager injection.")
    return _finding("SEC-001", "Credential exposure", "No obvious hard-coded credential pattern was detected.", "pass", "high", 0.88, "No common hard-coded credential patterns were detected.", evidence=[_absence("No supported credential pattern was detected; this is not a proof of absence.")])


WORKFLOW_NAMES = {"snakefile", "workflow.smk"}
WORKFLOW_SUFFIXES = {".nf", ".cwl", ".wdl"}
PATH_PATTERN = re.compile(r"(?P<quote>[\"'])(?P<value>(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:fastq(?:\.gz)?|fq(?:\.gz)?|bam|cram|vcf|fa(?:sta)?(?:\.gz)?|gff3?|gtf|tsv|csv|txt))(?P=quote)", re.IGNORECASE)
UNQUOTED_PATH_PATTERN = re.compile(r"(?:--(?:reference|ref|reads|input|output|out)|\bpath)\s+(?P<value>(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:fastq(?:\.gz)?|fq(?:\.gz)?|bam|cram|vcf|fa(?:sta)?(?:\.gz)?|gff3?|gtf|tsv|csv|txt))", re.IGNORECASE)
PARAM_PATTERN = re.compile(r"\bparams\.([A-Za-z_][A-Za-z0-9_]*)")


def _workflow_files(repo: Repository) -> list[Path]:
    return [path for path in repo.files() if path.name.lower() in WORKFLOW_NAMES or path.suffix.lower() in WORKFLOW_SUFFIXES or path.name.lower().endswith(".smk")]


def _workflow_path_matches(repo: Repository, path: Path) -> list[tuple[str, int, str, str]]:
    matches: list[tuple[str, int, str, str]] = []
    current_role = "dynamic"
    for line_number, line in enumerate(repo.text(path).splitlines(), 1):
        lowered = line.lower()
        if re.search(r"\boutput\s*:", lowered) or "emit:" in lowered:
            current_role = "output"
        elif re.search(r"\binput\s*:", lowered):
            current_role = "input"
        elif re.search(r"\bscript\s*:", lowered):
            current_role = "dynamic"
        role = "output" if current_role == "output" else "input" if current_role == "input" or any(term in lowered for term in ("reads", "reference", "frompath", "--ref")) else "dynamic"
        for match in PATH_PATTERN.finditer(line):
            matches.append((match.group("value"), line_number, line.strip(), role))
        quoted_values = {match.group("value") for match in PATH_PATTERN.finditer(line)}
        for match in UNQUOTED_PATH_PATTERN.finditer(line):
            if match.group("value") not in quoted_values:
                matches.append((match.group("value"), line_number, line.strip(), role))
    return matches


def check_workflow(repo: Repository) -> Finding:
    workflows = _workflow_files(repo)
    if not workflows:
        return _finding("DNA-WF-001", "Workflow definition", "A supported workflow definition is present.", "unknown", "medium", 0.8, "No Nextflow, Snakemake, CWL, or WDL workflow definition was detected.", evidence=[_absence("No supported workflow definition was found.")], limitations=GENOMICS_LIMITATIONS, recommendation="Use a declarative workflow or document the execution order and parameters explicitly.")
    evidence = [_evidence(repo, path, f"Supported workflow definition detected: {path.name}.", "artifact") for path in workflows[:10]]
    return _finding("DNA-WF-001", "Workflow definition", "A supported workflow definition is present.", "pass", "low", 0.99, f"Detected {len(workflows)} supported workflow definition(s).", evidence=evidence, limitations=GENOMICS_LIMITATIONS)


def check_workflow_paths(repo: Repository) -> Finding:
    workflows = _workflow_files(repo)
    if not workflows:
        return _finding("DNA-WF-002", "Workflow paths", "Referenced workflow input/output paths are locally resolvable.", "not_applicable", "medium", 0.95, "No supported workflow was detected.", evidence=[_absence("Path analysis is not applicable without a supported workflow.")], limitations=GENOMICS_LIMITATIONS)
    matches = [(path, value, line, source, role) for path in workflows for value, line, source, role in _workflow_path_matches(repo, path)]
    if not matches:
        return _finding("DNA-WF-002", "Workflow paths", "Referenced workflow input/output paths are locally resolvable.", "unknown", "medium", 0.7, "No static input/output path references were detected.", evidence=[_absence("Dynamic or parameterized paths may not be visible to the static detector.")], limitations=GENOMICS_LIMITATIONS)
    evidence: list[Evidence] = []
    missing = False
    dynamic = False
    for workflow, value, line, source, role in matches:
        target = repo.find_path(value)
        if target is None:
            dynamic = True
            evidence.append(_evidence(repo, workflow, f"Dynamic or external path reference: {value}", "declaration", 0.78, line, line))
        elif target.is_file():
            evidence.append(_evidence(repo, workflow, f"Path reference resolves locally: {value}", "declaration", 0.95, line, line))
        elif role == "output":
            evidence.append(_evidence(repo, workflow, f"Runtime-generated output path declaration: {value}", "declaration", 0.9, line, line))
        else:
            missing = True
            evidence.append(_evidence(repo, workflow, f"Referenced local path is missing: {value}", "contradictory", 0.98, line, line))
    if missing:
        status, message, confidence = "fail", "One or more workflow-referenced local paths are missing.", 0.98
    elif dynamic:
        status, message, confidence = "manual_review", "Some workflow paths are dynamic or external and require review.", 0.8
    else:
        status, message, confidence = "pass", "Detected workflow input/output paths resolve locally.", 0.93
    return _finding("DNA-WF-002", "Workflow paths", "Referenced workflow input/output paths are locally resolvable.", status, "high" if missing else "medium", confidence, message, evidence=evidence, limitations=GENOMICS_LIMITATIONS, recommendation="Add the missing artifact or document the runtime-generated/external path." if missing or dynamic else "")


def check_workflow_parameters(repo: Repository) -> Finding:
    workflows = _workflow_files(repo)
    if not workflows:
        return _finding("DNA-WF-003", "Workflow parameters", "Workflow parameters are documented or explicitly reviewable.", "not_applicable", "low", 0.95, "No supported workflow was detected.", evidence=[_absence("Parameter analysis is not applicable without a supported workflow.")], limitations=GENOMICS_LIMITATIONS)
    parameters: list[tuple[Path, str, int]] = []
    for path in workflows:
        for line_number, line in enumerate(repo.text(path).splitlines(), 1):
            parameters.extend((path, name, line_number) for name in PARAM_PATTERN.findall(line))
    if not parameters:
        return _finding("DNA-WF-003", "Workflow parameters", "Workflow parameters are documented or explicitly reviewable.", "not_applicable", "low", 0.9, "No Nextflow-style parameter references were detected.", evidence=[_absence("No static parameter references were detected.")], limitations=GENOMICS_LIMITATIONS)
    documentation = "\n".join(repo.text(path).lower() for path in repo.files() if path.name.lower().startswith("readme") or path.name.lower() in {"nextflow.config", "config.yaml", "config.yml"})
    missing = [(path, name, line) for path, name, line in parameters if name.lower() not in documentation]
    evidence = [_evidence(repo, path, f"Parameter reference: params.{name}", "declaration", 0.9, line, line) for path, name, line in parameters]
    if missing:
        evidence.extend(_evidence(repo, path, f"Parameter is not documented in detectable README/config text: params.{name}", "absence", 0.8, line, line) for path, name, line in missing)
        return _finding("DNA-WF-003", "Workflow parameters", "Workflow parameters are documented or explicitly reviewable.", "manual_review", "medium", 0.78, "Some workflow parameters were detected without corresponding documentation.", evidence=evidence, limitations=GENOMICS_LIMITATIONS, recommendation="Document parameter meaning, defaults, units, and an example invocation.")
    return _finding("DNA-WF-003", "Workflow parameters", "Workflow parameters are documented or explicitly reviewable.", "pass", "medium", 0.88, "Detected workflow parameters appear in README/configuration text.", evidence=evidence, limitations=GENOMICS_LIMITATIONS)


REFERENCE_PATTERN = re.compile(r"(?P<value>(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:fa|fasta)(?:\.gz)?)(?=$|[^A-Za-z0-9])", re.IGNORECASE)
ASSEMBLY_PATTERN = re.compile(r"\b(?:GRCh\d+|GRCm\d+|hg\d+|mm\d+|T2T-[A-Za-z0-9_.-]+|GCA_\d+\.\d+|GCF_\d+\.\d+)\b", re.IGNORECASE)
EXTERNAL_REFERENCE_PATTERN = re.compile(r"(?:https?://[^\s)>'\"]+|(?:GCA|GCF)_\d+\.\d+)", re.IGNORECASE)
CHECKSUM_PATTERN = re.compile(r"(?i)^\s*(?:sha256\s*[:=]?\s*)?([0-9a-f]{64}|[0-9a-f]{32})\s+[*]?([^\s]+)\s*$")
INLINE_CHECKSUM_PATTERN = re.compile(r"(?i)(sha256|md5)\s*[:=]\s*([0-9a-f]{64}|[0-9a-f]{32})")


def _checksum_records(repo: Repository) -> list[tuple[Path, int, str, str, str]]:
    records: list[tuple[Path, int, str, str, str]] = []
    for path in repo.files():
        for line_number, line in enumerate(repo.text(path).splitlines(), 1):
            match = CHECKSUM_PATTERN.match(line)
            if match:
                digest, filename = match.groups()
                records.append((path, line_number, "sha256" if len(digest) == 64 else "md5", digest.lower(), filename.replace("\\", "/")))
            for inline in INLINE_CHECKSUM_PATTERN.finditer(line):
                records.append((path, line_number, inline.group(1).lower(), inline.group(2).lower(), ""))
    return records


def _checksum_matches(repo: Repository, reference: Path, records: list[tuple[Path, int, str, str, str]]) -> tuple[list[Evidence], list[Evidence]]:
    valid: list[Evidence] = []
    contradictory: list[Evidence] = []
    relative = repo.relative(reference)
    for checksum_path, line, algorithm, digest, filename in records:
        associated = not filename or filename == relative or Path(filename).name == reference.name
        if not associated:
            continue
        if filename and filename == relative and reference.exists():
            actual = hashlib.sha256(reference.read_bytes()).hexdigest() if algorithm == "sha256" else hashlib.md5(reference.read_bytes()).hexdigest()
            if actual != digest:
                contradictory.append(_evidence(repo, checksum_path, f"Checksum does not match {relative}: {digest}", "contradictory", 0.99, line, line))
                continue
        valid.append(_evidence(repo, checksum_path, f"Valid {algorithm} checksum associated with {filename or relative}.", "artifact", 0.97, line, line))
    return valid, contradictory


def check_reference_provenance(repo: Repository) -> Finding:
    all_files = repo.files()
    text_files = [path for path in all_files if path.suffix.lower() in {".nf", ".smk", ".py", ".r", ".sh", ".yaml", ".yml", ".md", ".txt", ".toml", ".cff"} or path.name.lower() in {"snakefile", "workflow.smk"}]
    reference_mentions: list[tuple[Path, str, int]] = []
    external_mentions: list[tuple[Path, str, int]] = []
    assembly_mentions: list[tuple[Path, str, int]] = []
    for path in text_files:
        for line_number, line in enumerate(repo.text(path).splitlines(), 1):
            if any(term in line.lower() for term in ("reference", "genome", "assembly", ".fa", ".fasta")):
                reference_mentions.extend((path, match.group("value"), line_number) for match in REFERENCE_PATTERN.finditer(line))
            external_mentions.extend((path, match.group(0), line_number) for match in EXTERNAL_REFERENCE_PATTERN.finditer(line))
            assembly_mentions.extend((path, match.group(0), line_number) for match in ASSEMBLY_PATTERN.finditer(line))
    local_reference_paths = [path for path in all_files if path.name.lower().endswith((".fa", ".fasta", ".fa.gz", ".fasta.gz"))]
    referenced_paths: list[tuple[Path, Path | None, int]] = []
    for path, value, line in reference_mentions:
        referenced_paths.append((path, repo.find_path(value), line))
    if not referenced_paths and local_reference_paths:
        referenced_paths = [(local_reference_paths[0], local_reference_paths[0], 1)]
    evidence: list[Evidence] = []
    missing: list[Evidence] = []
    for source, reference, line in referenced_paths:
        value = REFERENCE_PATTERN.search(repo.text(source).splitlines()[line - 1] if line <= len(repo.text(source).splitlines()) else "")
        ref_value = value.group("value") if value else repo.relative(reference) if reference else "reference"
        if reference is None or not reference.is_file():
            missing.append(_evidence(repo, source, f"Referenced reference file is missing: {ref_value}", "contradictory", 0.99, line, line))
        else:
            evidence.append(_evidence(repo, reference, f"Referenced reference file exists locally: {repo.relative(reference)}", "artifact", 0.98, line, line))
    external = bool(external_mentions)
    if external:
        evidence.extend(_evidence(repo, path, f"Explicit external reference identity: {value}", "declaration", 0.9, line, line) for path, value, line in external_mentions[:5])
    if missing:
        return _finding("DNA-REF-001", "Reference genome provenance", "The referenced genome assembly and integrity evidence are traceable.", "fail", "high", 0.99, "A workflow or document references a missing local reference file.", evidence=missing + evidence, limitations=GENOMICS_LIMITATIONS, recommendation="Add the referenced file or explicitly identify the external accession/URL used at runtime.")
    if not referenced_paths and not external:
        return _finding("DNA-REF-001", "Reference genome provenance", "The referenced genome assembly and integrity evidence are traceable.", "manual_review", "high", 0.75, "No local or explicit external reference identity was detected.", evidence=[_absence("No reference FASTA path, accession, or URL was detected.")], limitations=GENOMICS_LIMITATIONS, recommendation="Document the reference assembly and provenance, or explicitly state that the workflow is reference-free.")
    if assembly_mentions:
        evidence.extend(_evidence(repo, path, f"Assembly/version signal: {value}", "declaration", 0.9, line, line) for path, value, line in assembly_mentions[:5])
    else:
        evidence.append(_absence("No recognizable assembly/version identifier was detected.", 0.85))
    if not assembly_mentions:
        return _finding("DNA-REF-001", "Reference genome provenance", "The referenced genome assembly and integrity evidence are traceable.", "unknown", "high", 0.78, "A reference was identified, but its assembly/version was not detected.", evidence=evidence, limitations=GENOMICS_LIMITATIONS, recommendation="Record the assembly/version, source accession or URL, and checksum.")
    records = _checksum_records(repo)
    valid_checksums: list[Evidence] = []
    contradictory_checksums: list[Evidence] = []
    for _, reference, _ in referenced_paths:
        if reference and reference.is_file():
            valid, bad = _checksum_matches(repo, reference, records)
            valid_checksums.extend(valid)
            contradictory_checksums.extend(bad)
    if external and not valid_checksums:
        for path, line, algorithm, digest, filename in records:
            if filename and (Path(filename).name in {Path(value).name for _, value, _ in external_mentions}):
                valid_checksums.append(_evidence(repo, path, f"Valid {algorithm} checksum associated with external reference {filename}.", "artifact", 0.9, line, line))
    if contradictory_checksums:
        return _finding("DNA-REF-001", "Reference genome provenance", "The referenced genome assembly and integrity evidence are traceable.", "fail", "high", 0.99, "A checksum artifact contradicts the referenced local reference file.", evidence=evidence + contradictory_checksums, limitations=GENOMICS_LIMITATIONS, recommendation="Recompute and publish the checksum for the exact reference file used.")
    if not valid_checksums:
        evidence.append(_absence("No syntactically valid checksum associated with the referenced reference file was found.", 0.98))
        return _finding("DNA-REF-001", "Reference genome provenance", "The referenced genome assembly and integrity evidence are traceable.", "unknown", "high", 0.95, "Reference and assembly signals exist, but no valid associated checksum was found.", evidence=evidence, limitations=GENOMICS_LIMITATIONS, recommendation="Publish a real SHA-256 or MD5 checksum associated with the exact reference file or external accession.")
    return _finding("DNA-REF-001", "Reference genome provenance", "The referenced genome assembly and integrity evidence are traceable.", "pass", "high", 0.97, "The reference identity, assembly/version, and associated checksum were detected.", evidence=evidence + valid_checksums, limitations=GENOMICS_LIMITATIONS)


def _genomic_input(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith((".fastq", ".fastq.gz", ".fq", ".fq.gz", ".bam", ".cram")) and "expected" not in name


def _expected_output(path: Path) -> bool:
    name = path.name.lower()
    return any(token in name for token in ("expected", "golden", "truth")) and name.endswith((".vcf", ".vcf.gz", ".bam", ".cram", ".tsv", ".csv", ".txt"))


def _substantive_comparison(text: str) -> bool:
    if re.search(r"(?i)assert\s+true\b", text):
        return False
    return bool(re.search(r"(?m)(==|filecmp|read_text|read_bytes|hashlib|\bdiff\b|\bcmp\b|subprocess)", text)) and bool(re.search(r"(?i)assert|compare|diff|cmp|filecmp|read_text|read_bytes", text))


def check_genomic_validation(repo: Repository) -> Finding:
    files = repo.files()
    inputs = [path for path in files if _genomic_input(path)]
    expected = [path for path in files if _expected_output(path)]
    test_like = [path for path in files if path.suffix.lower() in {".py", ".r", ".sh", ".nf", ".smk", ".md", ".txt"} and (any(part.lower() in {"test", "tests"} for part in repo.relative(path).split("/")) or path.name.lower().startswith(("readme", "snakefile")))]
    connected: list[Evidence] = []
    for path in test_like:
        text = repo.text(path)
        if not _substantive_comparison(text):
            continue
        names = [candidate.name for candidate in inputs + expected]
        if len(names) >= 2 and sum(1 for name in names if name.lower() in text.lower()) >= 2:
            connected.append(_evidence(repo, path, "Substantive comparison connects representative input and expected output names.", "test", 0.94, 1, max(1, len(text.splitlines()))))
    evidence = [_evidence(repo, path, "Representative genomic input artifact exists.", "artifact") for path in inputs[:5]]
    evidence.extend(_evidence(repo, path, "Expected output artifact exists.", "artifact") for path in expected[:5])
    evidence.extend(connected)
    if not inputs:
        evidence.append(_absence("No representative FASTQ/BAM/CRAM input artifact was found."))
    if not expected:
        evidence.append(_absence("No expected/golden/truth output artifact was found."))
    if inputs and expected and connected:
        return _finding("DNA-VAL-001", "Known-answer validation", "Representative inputs are connected to an expected output by a substantive comparison.", "pass", "high", 0.96, "Representative input, expected output, and a substantive comparison were detected.", evidence=evidence, limitations=GENOMICS_LIMITATIONS)
    if inputs and expected:
        return _finding("DNA-VAL-001", "Known-answer validation", "Representative inputs are connected to an expected output by a substantive comparison.", "manual_review", "high", 0.9, "Input and expected-output artifacts exist, but a substantive comparison connecting them was not detected.", evidence=evidence, limitations=GENOMICS_LIMITATIONS, recommendation="Add a test or documented command that compares actual output to the expected output; an assertion such as assert True is insufficient.")
    return _finding("DNA-VAL-001", "Known-answer validation", "Representative inputs are connected to an expected output by a substantive comparison.", "unknown", "high", 0.9, "Known-answer validation could not be established from local artifacts.", evidence=evidence, limitations=GENOMICS_LIMITATIONS, recommendation="Add a small input fixture, expected output, and substantive comparison test.")


CONTAINER_DECLARATION = re.compile(r"(?i)(?:\bcontainer\b|\bimage\b)\s*[:=]\s*[\"']?([^\s\"']+)|^\s*FROM\s+([^\s]+)|^\s*container\s*:\s*([^\s]+)")
IMAGE_DIGEST = re.compile(r"@sha256:[0-9a-f]{64}$", re.IGNORECASE)


def check_portability(repo: Repository) -> Finding:
    declarations: list[tuple[Path, int, str]] = []
    for path in repo.files():
        if path.name.lower() in {"dockerfile", "nextflow.config", "snakefile", "workflow.smk"} or path.suffix.lower() in {".nf", ".smk", ".yaml", ".yml", ".cwl", ".wdl"}:
            for line_number, line in enumerate(repo.text(path).splitlines(), 1):
                match = CONTAINER_DECLARATION.search(line)
                if match:
                    image = next(group for group in match.groups() if group)
                    declarations.append((path, line_number, image.rstrip(",")))
    pinned_env = _pinned_dependency_evidence(repo)
    evidence = [_evidence(repo, path, f"Container declaration: {image}", "declaration", 0.95, line, line) for path, line, image in declarations]
    if any(IMAGE_DIGEST.search(image) for _, _, image in declarations):
        return _finding("DNA-PORT-001", "Execution portability", "The repository declares an immutable container or pinned environment.", "pass", "medium", 0.98, "An immutable container digest was detected.", evidence=evidence, limitations=GENOMICS_LIMITATIONS)
    if pinned_env:
        return _finding("DNA-PORT-001", "Execution portability", "The repository declares an immutable container or pinned environment.", "pass", "medium", 0.94, "A lockfile or exact environment dependency pin was detected.", evidence=evidence + pinned_env, limitations=GENOMICS_LIMITATIONS)
    if declarations:
        evidence.append(_absence("Container declarations are mutable tags or otherwise lack an immutable digest.", 0.94))
        return _finding("DNA-PORT-001", "Execution portability", "The repository declares an immutable container or pinned environment.", "unknown", "medium", 0.94, "A container was declared, but no immutable digest or pinned environment was detected.", evidence=evidence, limitations=GENOMICS_LIMITATIONS, recommendation="Pin the container by digest or provide a lockfile/exact environment specification.")
    return _finding("DNA-PORT-001", "Execution portability", "The repository declares an immutable container or pinned environment.", "unknown", "medium", 0.82, "No actionable container declaration or pinned environment was detected.", evidence=[_absence("Words such as Docker or conda in prose are not treated as portability evidence.")], limitations=GENOMICS_LIMITATIONS, recommendation="Provide an immutable container digest or pinned environment specification.")


GENERIC_CHECKS: tuple[Check, ...] = (check_readme, check_license, check_citation, check_tests, check_ci, check_dependencies, check_pinning, check_secrets)
GENOMICS_CHECKS: tuple[Check, ...] = (check_workflow, check_workflow_paths, check_workflow_parameters, check_reference_provenance, check_genomic_validation, check_portability)


