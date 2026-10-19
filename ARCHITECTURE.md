# Architecture

## System context

BioRobust is a local Python CLI for a first-pass review of open-source biological and scientific software repositories.

```text
local path or HTTP(S) Git URL
              |
              v
      start target resolver
              |
              v
       Repository inspector
              |
              v
        Profile resolver
      /         |          \
 workflow   bioinformatics  biology
      \         |          /
              v
        Evidence-producing checks
              |
              v
          ScanReport model
       /       |       |       \
    JSON   Markdown   HTML     PDF
              |
              v
        reviewable reports
```

The input boundary is a repository directory or a public HTTP(S) Git URL. The output boundary is a versioned report with a deterministic manifest hash. The scanner does not modify or execute the target repository.

## Components

- `repository.py` discovers files deterministically, skips common generated/dependency directories, bounds text reads, and computes the manifest hash.
- `checks.py` contains small static checks that return evidence-bearing `Finding` objects.
- `profiles.py` defines the profile registry, conservative detectors, and the extension seam for domain-specific check collections.
- `scanner.py` resolves the requested profile, runs checks, and creates a `ScanReport` with limitations and notes.
- `models.py` defines strict report objects, evidence types, statuses, decisions, and serialization.
- `rules.py` defines the versioned rule catalog used by the CLI and reports.
- `reporting.py` is the stable writer API for JSON, Markdown, HTML, and PDF reports.
- `report_options.py` defines immutable, presentation-only themes and evidence-detail levels.
- `pdf_styles.py` centralizes readable typography, status labels, and theme palettes.
- `pdf_layout.py` builds the portrait A4 PDF story without changing the underlying report.
- `cli.py` exposes `start`, `scan`, `rules`, `profiles`, and `explain` commands.
- `schemas/report.schema.json` defines the machine-readable JSON contract.

## Profile model

Profiles are named tuples of checks with a description and a conservative detector:

| Profile | Checks | Purpose |
|---|---|---|
| `generic` | Generic checks | Any open-source scientific or computational repository |
| `biology` | Generic checks | Biological software without genomic assumptions |
| `bioinformatics` | Generic plus genomic checks | Genomic, sequence-analysis, and bioinformatics tools |
| `genomics` | Generic plus genomic checks | Compatibility name for the genomic rule pack |
| `genomics-workflow` | Generic plus genomic checks | Workflow repositories using Nextflow, Snakemake, CWL, or WDL |

`auto` chooses the least-specialized useful profile in this order: workflow, bioinformatics, biology, generic. Genomic rule IDs remain stable and are not applied by the broad `biology` profile.

## Data flow

1. `start` treats a local path as already available or clones an HTTP(S) Git URL into `.biorobust/repos/<name>`.
2. `Repository` exposes bounded, deterministic observations to checks.
3. The selected checks return `Finding` objects with evidence or explicit absence observations.
4. `ScanReport` derives status counts and a routing decision without calculating a global quality score.
5. Writers serialize the report to JSON, Markdown, HTML, or PDF. Render options affect only human-readable output; JSON remains complete.
6. The user reviews the report and can use the stable rule IDs and evidence paths to investigate specific findings.

## Interfaces and compatibility

- The JSON report schema remains the stable automation contract.
- The `RenderOptions` interface is immutable and presentation-only: `scientific`, `minimal`, or `high-contrast` themes and `minimal`, `standard`, or `verbose` evidence detail.
- Existing profile names and `DNA-*` rule IDs remain valid.
- `scan` and the CLI now default to `auto`; callers can request `generic`, `biology`, `bioinformatics`, `genomics`, or `genomics-workflow` explicitly.
- New profiles should reuse the report model and add fixtures before adding broad heuristics.
- Generated PDFs are presentation artifacts, not a second source of truth.

## Deployment and operations

There is no backend, frontend, database, hosted service, or container requirement in v0.4. Installation is a local Python package. CI runs the test suite and JSON/PDF scan smoke tests on Python 3.11–3.14.

The default mode reads local files only. URL cloning is the one explicit network-capable workflow and is visible to the user. External metadata adapters, if added later, must make network behavior explicit and cache or record the evidence they use.

## Security and safety

- Target code is never imported or executed by the default scanner.
- File reads are bounded and common generated/dependency directories are skipped.
- The credential check is heuristic and is not a secret-scanner replacement.
- A `pass` means that a narrow repository signal was observed, not that the software is safe or scientifically correct.
- Future execution support must be opt-in, sandboxed, resource-limited, and separated from static scanning.

## Testing strategy

Unit tests cover evidence semantics, schema validation, deterministic manifests, CLI outputs, ignored directories, credential false positives, genomic positive/negative/ambiguous fixtures, broad biology profile detection, generic fallback, immutable rendering options, HTML table semantics, PDF text/status readability, PDF non-mutation, and all report formats. Real-repository pilots are run manually and are not part of CI because external repositories change over time.

## Risks and open questions

- Biological terminology is broad and can create profile false positives; markers remain conservative and the selected profile is recorded in the report.
- Generic checks cannot prove domain-specific validity; future profiles must be calibrated against pinned repositories.
- Static inspection misses dynamic paths, generated artifacts, and runtime behavior.
- A single score would invite misuse, so reports retain evidence and uncertainty instead.
- A third-party profile plugin API should wait until rule lifecycle and compatibility requirements are tested against real contributors.
