# Architecture

## Boundary

BioRobust is a local-first static analysis tool. The input boundary is a directory containing an open-source software repository. The output boundary is a versioned report with a deterministic manifest hash; the scanner does not modify or execute the target repository.

```text
repository path
      |
      v
Repository inspector -> profile resolver -> profile checks -> Finding objects -> ScanReport
                                                     |             |
                                                     v             v
                                                  JSON schema     HTML
```

## Components

- `repository.py` provides deterministic file discovery and bounded text reads.
- `checks.py` contains small checks that return evidence-bearing `Finding` objects.
- `profiles.py` is the profile registry and extension seam. Profiles combine generic checks with domain-specific checks and can be selected explicitly or through narrow `auto` detection.
- `scanner.py` resolves the profile and orchestrates checks.
- `models.py` defines the strict report contract, structured evidence, and status semantics.
- `rules.py` defines the versioned rule catalog used by the CLI and reports.
- `reporting.py` renders JSON and HTML.
- `cli.py` exposes the command-line interface.
- `schemas/report.schema.json` is the machine-readable output contract.

## Profiles

The current registry contains `generic`, `genomics`, `genomics-workflow`, and
`sbol`. A profile is a named tuple of checks, a description, and a conservative
detector. The SBOL profile is intentionally evidence-oriented: generic XML/JSON
parsing can report serialization evidence, but the report remains `manual_review`
or `unknown` where SBOL semantic or interoperability validation would be needed.

New domains should add a profile and fixtures rather than adding domain-specific
heuristics to generic checks. A future external plugin API can wrap the same
`ProfileDefinition` contract without changing the report schema.

## Review documents and terminal questions

JSON is the stable machine contract. Markdown is a portable review document and
HTML is the browser-friendly view. `biorobust ask PATH QUESTION` runs a scan and
selects relevant findings by question terms; it is deliberately deterministic,
local, and evidence-grounded rather than an unconstrained chat interface.

## Status semantics

- `pass`: evidence supporting the criterion was found.
- `fail`: evidence of a high-confidence problem was found.
- `unknown`: the static scanner could not establish the criterion.
- `manual_review`: domain judgment is needed, or the repository may not require the criterion.
- `not_applicable`: reserved for future profile adapters that can establish non-applicability.

Unknown is not a failure and pass is not certification. Every finding carries evidence or an explicit absence observation. The report has a routing decision, not a global quality score.

## Security and operations

The default mode is static and local. It reads bounded text, skips common generated/dependency directories, and never imports or runs target code. Future execution support must be opt-in, sandboxed, resource-limited, and clearly separated from static scanning.

The credential check is intentionally heuristic. It is useful for catching obvious mistakes but is not a secret scanner replacement. Reference, validation, workflow-path, and portability checks require concrete artifacts rather than keyword mentions. External integrations must be adapters with explicit network behavior and cached evidence; none are enabled in the static MVP.

## Testing strategy

Unit tests cover status/severity semantics, schema validation, deterministic manifests, CLI output, ignored directories, credential false positives, and representative positive/negative/ambiguous fixtures. Real-repository pilots should be recorded separately from the unit test suite so external repository drift does not make CI flaky.

## Risks

- Genomics repositories vary widely; a rule can be useful without being universal.
- Text signals can produce false positives; findings must retain evidence and recommendations.
- Workflow execution is powerful but unsafe without sandboxing.
- A single score would hide uncertainty and invite misuse, so the first version avoids one.


