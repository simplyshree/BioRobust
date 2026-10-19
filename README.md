# BioRobust

BioRobust is a free, open-source, local-first tool for understanding unfamiliar biological and scientific software repositories before you run, reuse, or extend them.

It creates evidence-backed reports about documentation, tests, dependencies, workflows, reference data, validation signals, security patterns, and portability. It makes uncertainty visible instead of hiding everything behind a single score.

BioRobust is useful for genomics, bioinformatics, transcriptomics, proteomics, metabolomics, synthetic biology, neuroscience, biological imaging, systems biology, ecology, and adjacent open-source scientific software.

It does not certify scientific correctness, clinical suitability, security, or AI-generated code quality. The default scanner is static: it does not import or execute repository code and does not send repository contents to an online AI service.

## What it does

- Helps researchers understand the purpose, entry points, inputs, outputs, and setup of an unfamiliar repository.
- Helps maintainers identify missing documentation, tests, dependency constraints, licenses, citation metadata, and portability evidence.
- Helps reviewers prepare a controlled reproduction or reuse attempt by showing what evidence exists and what is missing.
- Produces Markdown, PDF, HTML, and JSON reports from the same evidence model.
- Answers focused questions in the terminal from a fresh local scan.
- Keeps stable rule IDs, evidence locations, confidence, limitations, and a deterministic manifest hash in every report.
- Supports AI-assisted repository exploration without replacing the underlying local evidence trail.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"

# Run inside an already-cloned repository
cd path\to\repository
biorobust start .
```

The normal workflow is one command from the repository folder. `start` uses the `auto` profile, creates a Markdown onboarding report by default, and does not execute the target project.

To start directly from a GitHub or other HTTP(S) Git URL:

```powershell
biorobust start https://github.com/OWNER/PROJECT.git
```

BioRobust clones the repository into `.biorobust/repos/` and reuses that local copy on later runs.

## Reports and terminal questions

```powershell
# Markdown onboarding report
biorobust start . --format markdown --output report.md

# Shareable PDF report
New-Item -ItemType Directory -Force output\pdf | Out-Null
biorobust start . --format pdf --theme scientific --detail standard --output output\pdf\report.pdf

# A compact report for a quick review
biorobust start . --format pdf --theme minimal --detail minimal --output output\pdf\quick-review.pdf

# A high-contrast report with every evidence observation
biorobust start . --format pdf --theme high-contrast --detail verbose --output output\pdf\full-review.pdf

# Machine-readable report for CI or scripts
biorobust scan . --format json --output report.json

# Browser-friendly report
biorobust scan . --format html --output report.html

# Evidence-grounded terminal questions
biorobust ask . "What does this repository appear to do?"
biorobust ask . "What would I need to reproduce its main workflow?"
biorobust ask . "What evidence is missing before I reuse this tool?"
```

Generated PDFs and other local report artifacts are ignored by Git. The available formats are `markdown` for onboarding, `pdf` for sharing or archiving, `html` for browser viewing, and `json` for automation.

### Presentation options

The scanner always builds the same evidence-bearing report. These options only control human-readable presentation:

| Option | Values | Use |
|---|---|---|
| `--theme` | `scientific`, `minimal`, `high-contrast` | Choose the visual palette for PDF and HTML; Markdown records the choice. |
| `--detail` | `minimal`, `standard`, `verbose` | Show 2, 5, or all evidence observations per finding in human-readable reports. |

JSON always contains the complete evidence list, regardless of theme or detail. Both `scan` and `start` accept these options. For example:

```powershell
biorobust scan . --format html --theme high-contrast --detail verbose --output report.html
```

## How the workflow works

```text
local folder or Git URL
        |
        v
automatic profile selection
        |
        v
static evidence scan
        |
        v
Markdown, PDF, HTML, or JSON report
        |
        v
grounded terminal questions
```

## Profiles

| Profile | Use it for |
|---|---|
| `auto` | Choose the least-specialized useful profile from explainable repository signals |
| `generic` | Any open-source scientific or computational software repository |
| `biology` | Biological and life-science software without assuming genomic inputs |
| `bioinformatics` | Bioinformatics, genomic, sequence-analysis, and related tool repositories |
| `genomics` | The genomics-focused rule pack, retained for compatibility |
| `genomics-workflow` | Repositories centered on Nextflow, Snakemake, CWL, or WDL workflows |

Automatic selection checks workflow and repository-language signals in this order:

1. `genomics-workflow` for supported workflow repositories.
2. `bioinformatics` for genomic and sequence-analysis repositories.
3. `biology` for broader biological software such as neuroscience, proteomics, imaging, or synthetic biology.
4. `generic` for other scientific and computational repositories.

Use an explicit profile when the repository needs a particular rule pack:

```powershell
biorobust profiles
biorobust scan . --profile biology
biorobust scan . --profile genomics
```

## Interpreting results

| Status | Meaning |
|---|---|
| `pass` | Evidence supports the narrow claim |
| `fail` | Evidence contradicts the narrow claim |
| `unknown` | The scanner could not establish the claim |
| `manual_review` | Human or domain-specific validation is required |
| `not_applicable` | The criterion does not apply |

`pass` does not mean scientifically correct. For example, a valid checksum supports file identity but does not prove that a reference is biologically appropriate. The report has a routing decision, not a universal quality score.

## AI-compatible by design

BioRobust is useful in an AI-assisted workflow because its reports preserve the source paths, observations, rule IDs, confidence, limitations, and manifest hash behind each conclusion. An AI assistant can summarize or explain that evidence, while the repository owner can inspect the same local files and rerun the scan. BioRobust itself does not make AI authorship claims and does not present generated text as scientific evidence.

## Scope and limitations

The current project provides broad repository checks and a focused genomic rule pack. It is not a complete domain validator for every biological field. Domain-specific checks should be added only when their evidence model and limitations are clear.

The scanner is deliberately static and local. It does not import or execute target code, make network requests during a local scan, retrieve external reference data, run workflow engines, prove biological validity, or provide clinical certification. Replication support means identifying the evidence and missing prerequisites needed for a human-controlled reproduction attempt.

## Install as software

For the current development version:

```powershell
python -m pip install "biorobust @ git+https://github.com/simplyshree/BioRobust.git@main"
biorobust --version
```

For local development and contributions:

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
```

After a numbered PyPI release is published, the normal user installation will be:

```powershell
python -m pip install biorobust
```

See [RELEASING.md](RELEASING.md) for the versioning and GitHub Release process.

## Repository layout

- `src/biorobust/` contains the installable CLI and evidence model.
- `tests/` contains deterministic unit tests and small synthetic fixtures.
- `docs/` contains validation and launch material.
- `schemas/` contains the machine-readable report contract.

For AI-assisted changes, read [PRODUCT.md](PRODUCT.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [AGENT.md](AGENT.md) before editing. Plans should preserve the evidence trail; generated conclusions must not be treated as evidence.

## Development

```powershell
python -m pytest -q
```

The CI workflow tests Python 3.11–3.14, validates report schemas, checks all report formats, scans the genomics fixture, and performs a PDF smoke test for the broader biology fixture. The fixtures under `tests/fixtures` are small and synthetic so they remain deterministic.

There is no container or hosted service required for v0.4. The supported runtime is a local Python CLI. A future sandboxed execution adapter must be opt-in, resource-limited, and separately documented.

## Release

BioRobust uses semantic-style versions such as `0.4.0`. The version must match in `pyproject.toml` and `src/biorobust/__init__.py`. A release is made from a Git tag such as `v0.4.0`; GitHub Actions builds the source archive and wheel and attaches them to a GitHub Release. PyPI publication is intentionally a separate maintainer decision.

## Repository guide

- [PRODUCT.md](PRODUCT.md) defines the v0.4 product boundary and user workflows.
- [ARCHITECTURE.md](ARCHITECTURE.md) explains the scanner design and extension seams.
- [AGENT.md](AGENT.md) contains collaboration and change rules.
- [CONTRIBUTING.md](CONTRIBUTING.md) explains how to add checks, profiles, tests, and documentation.
- [ADR-001.md](ADR-001.md) records the local-first, evidence-first decision.
- [ADR-002.md](ADR-002.md) records the profile, onboarding-document, and terminal-question decision.
- [ADR-003.md](ADR-003.md) records the v0.4 broadening to biological software.
- [docs/launch/linkedin-post.md](docs/launch/linkedin-post.md) contains the launch announcement draft.
- [docs/launch/pilot-invitation.md](docs/launch/pilot-invitation.md) contains the first user-testing message.
- [docs/validation-plan.md](docs/validation-plan.md) defines the cross-domain calibration pilot.
- [schemas/report.schema.json](schemas/report.schema.json) defines the JSON contract.
