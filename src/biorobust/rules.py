"""Human-readable rule catalog used by ``biorobust rules`` and ``explain``."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


RULE_PACK_VERSION = "0.3.0"


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    rule_id: str
    title: str
    profile: str
    claim: str
    description: str
    limitations: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["limitations"] = list(self.limitations)
        return value


RULES: tuple[RuleDefinition, ...] = (
    RuleDefinition("DOC-001", "Project README", "generic", "The repository explains how to use the project.", "Looks for a conventional README file.", ("Presence does not establish that the documentation is complete or correct.",)),
    RuleDefinition("META-001", "Open-source license", "generic", "The repository declares a license artifact.", "Looks for standard license filenames.", ("The scanner does not interpret license compatibility or legal sufficiency.",)),
    RuleDefinition("META-002", "Citation metadata", "generic", "The repository provides a citation signal.", "Looks for CITATION.cff, codemeta, DOI, or explicit citation guidance.", ("A citation mention is not a validated bibliographic record.",)),
    RuleDefinition("TEST-001", "Automated tests", "generic", "The repository contains test artifacts.", "Detects test files or test directories.", ("Static presence does not show that tests pass or are substantive.",)),
    RuleDefinition("CI-001", "Continuous integration", "generic", "The repository declares an automation configuration.", "Detects common CI configuration paths.", ("The scanner does not execute CI jobs.",)),
    RuleDefinition("DEP-001", "Declared dependencies", "generic", "Runtime dependencies are declared.", "Detects common package and environment manifests.", ("A manifest may be incomplete or not used by the workflow.",)),
    RuleDefinition("REPRO-001", "Dependency pinning", "generic", "Some dependency versions are constrained reproducibly.", "Detects lockfiles or exact requirements pins.", ("Pinning alone does not make a workflow reproducible.",)),
    RuleDefinition("SEC-001", "Credential exposure", "generic", "No obvious hard-coded credential pattern was detected.", "Heuristically scans selected source/configuration files.", ("This is not a complete secret scanner and can miss or misclassify values.",)),
    RuleDefinition("DNA-WF-001", "Workflow definition", "genomics", "A supported workflow definition is present.", "Detects Nextflow and Snakemake as first-class targets, plus CWL/WDL.", ("Workflow presence does not establish scientific correctness.",)),
    RuleDefinition("DNA-WF-002", "Workflow paths", "genomics", "Referenced workflow input/output paths are locally resolvable.", "Extracts conservative path references and reports missing local artifacts.", ("Dynamic paths, parameters, and runtime-generated files require review.",)),
    RuleDefinition("DNA-WF-003", "Workflow parameters", "genomics", "Workflow parameters are documented or explicitly reviewable.", "Compares detectable parameter references with README/configuration text.", ("Static text matching cannot determine whether a parameter is scientifically appropriate.",)),
    RuleDefinition("DNA-REF-001", "Reference genome provenance", "genomics", "The referenced genome assembly and integrity evidence are traceable.", "Requires a local/external reference identity, assembly/version, syntactically valid associated checksum, and a matching local digest when possible.", ("This does not validate the biological suitability of the assembly.",)),
    RuleDefinition("DNA-VAL-001", "Known-answer validation", "genomics", "Representative inputs are connected to an expected output by a substantive comparison.", "Requires artifacts plus a test or documented command that compares actual and expected results.", ("Static analysis does not run the test or establish scientific validity.",)),
    RuleDefinition("DNA-PORT-001", "Execution portability", "genomics", "The repository declares an immutable container or pinned environment.", "Distinguishes digest-pinned images and exact environment pins from mutable tags or prose.", ("A pinned environment can still contain incorrect or unavailable software.",)),
    RuleDefinition("SBOL-001", "SBOL artifact detection", "sbol", "The repository contains an identifiable SBOL design artifact.", "Looks for SBOL-specific file extensions or namespace markers.", ("A detected artifact is not proof of SBOL semantic validity.",)),
    RuleDefinition("SBOL-002", "SBOL serialization syntax", "sbol", "Detected SBOL serializations are syntactically parseable by a generic parser.", "Parses detected XML/JSON artifacts and explicitly reports unsupported Turtle/RDF parsing.", ("Generic parsing is not SBOL schema or semantic validation.",)),
    RuleDefinition("SBOL-003", "SBOL version declaration", "sbol", "The repository identifies the SBOL version used by its artifacts or tooling.", "Detects explicit SBOL 2 or SBOL 3 signals.", ("The scanner does not infer the intended version from ambiguous artifacts.",)),
    RuleDefinition("SBOL-004", "SBOL validation evidence", "sbol", "The repository provides an explicit SBOL validation or validator-integration signal.", "Detects validation-related tests, dependencies, commands, or documentation without executing them.", ("The validator is not run by the static MVP.",)),
    RuleDefinition("SBOL-005", "SBOL interoperability evidence", "sbol", "The repository provides an explicit SBOL interoperability or round-trip signal.", "Detects import/export, conversion, serialization, and round-trip signals.", ("Static signals do not establish cross-tool semantic equivalence.",)),
)


RULE_BY_ID = {rule.rule_id: rule for rule in RULES}


