# Architecture

## Boundary

BioRobust is a local-first static analysis tool. The input boundary is a directory containing an open-source software repository. The output boundary is a versioned report with a deterministic manifest hash; the scanner does not modify or execute the target repository.

```text
repository path
      |
      v
Repository inspector -> profile checks -> Finding objects -> ScanReport
                                                     |             |
                                                     v             v
                                                  JSON schema     HTML
```

## Components

- `repository.py` provides deterministic file discovery and bounded text reads.
- `checks.py` contains small checks that return evidence-bearing `Finding` objects.
- `scanner.py` selects the profile and orchestrates checks.
- `models.py` defines the strict report contract, structured evidence, and status semantics.
- `rules.py` defines the versioned rule catalog used by the CLI and reports.
- `reporting.py` renders JSON and HTML.
- `cli.py` exposes the command-line interface.
- `schemas/report.schema.json` is the machine-readable output contract.

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


