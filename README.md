# BioRobust

BioRobust is a local, evidence-first starter skill for open-source genomic and bioinformatics software. Use it at the beginning of a project to understand what a repository does, decipher how it is organized, and identify what is needed to reproduce or safely extend it.

It produces a reviewable report about documentation, tests, dependencies, workflows, reference data, validation evidence, security signals, and portability. It does not certify scientific correctness or execute repository code.

## What it helps you do

- Understand the repository’s purpose, entry points, workflows, inputs, outputs, tests, and environment declarations.
- Decipher whether important claims are supported by observable files and configuration.
- Replicate a documented workflow by checking references, expected outputs, dependency pins, and portability signals.
- Compare repositories using stable rule IDs, structured evidence, and deterministic manifest hashes.
- Ask focused questions in the terminal after cloning, without sending code to an online AI service.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"

git clone https://github.com/OWNER/PROJECT.git project
biorobust start project --output project-BioRobust.md
```

The `start` command is the recommended first pass. It creates a Markdown onboarding report. For automation or browser viewing:

```powershell
biorobust scan project --profile auto --format json --output project-BioRobust.json
biorobust scan project --profile auto --format html --output project-BioRobust.html
```

The scanner can also run without installation:

```powershell
python -m biorobust scan path\to\repository --profile bioinformatics
```

## Profiles

| Profile | Use it for |
|---|---|
| `auto` | Choose a useful profile from narrow repository signals |
| `generic` | Any open-source scientific or computational software repository |
| `bioinformatics` | Genomic repositories and bioinformatics libraries, packages, and command-line tools |
| `genomics` | The genomics-focused rule pack, retained for compatibility |
| `genomics-workflow` | Repositories centered on Nextflow, Snakemake, CWL, or WDL |

Use `auto` when unsure. It selects the workflow profile when a supported workflow is present, the bioinformatics profile when genomic or bioinformatics signals are visible, and the generic profile otherwise.

```powershell
biorobust profiles
```

## Ask questions in the terminal

Questions are answered from a fresh local scan. They do not call an online AI service:

```powershell
biorobust ask project "What does this repository appear to do?"
biorobust ask project "Is this repository reproducible?"
biorobust ask project "What inputs, references, and validation evidence should I inspect?"
biorobust ask project "Are there obvious credential risks?"
```

Answers include the relevant rule, status, and evidence. Treat `unknown` and `manual_review` as requests for investigation, not as failures.

## Output and interpretation

```powershell
# Human-readable onboarding document
biorobust start project --format markdown --output report.md

# Machine-readable report for CI or scripts
biorobust scan project --profile auto --format json --output report.json

# Browser-friendly report
biorobust scan project --profile auto --format html --output report.html
```

| Status | Meaning |
|---|---|
| `pass` | Evidence supports the narrow claim |
| `fail` | Evidence contradicts the narrow claim |
| `unknown` | The scanner could not establish the claim |
| `manual_review` | Human or domain-specific validation is required |
| `not_applicable` | The criterion does not apply |

`pass` does not mean scientifically correct. A valid checksum supports file identity, for example, but does not prove that a reference assembly is biologically appropriate.

Inspect the rule catalog:

```powershell
biorobust rules
biorobust explain DNA-REF-001
biorobust explain TEST-001
```

## Scope

The primary target is open-source genomic and bioinformatics software: sequence-analysis tools, variant callers, annotation tools, reference-data packages, Python/R/JavaScript libraries, command-line programs, and workflow repositories. The same generic checks can be used for adjacent scientific software.

The scanner is deliberately static and local. It does not import or execute target code, fetch external reference data, run workflow engines, prove scientific validity, or provide clinical certification. Replication support means identifying the evidence and missing prerequisites needed for a human-controlled reproduction attempt.

## Development

```powershell
python -m unittest discover -s tests
```

The fixtures under `tests/fixtures` are small and synthetic. They exercise evidence behavior, including missing references, placeholder checksums, mutable containers, missing expected outputs, non-substantive tests, and a bioinformatics tool that has no sequence files but is discoverable from its metadata.

## Repository guide

- [PRODUCT.md](PRODUCT.md) defines the user problem and v0.3 boundary.
- [ARCHITECTURE.md](ARCHITECTURE.md) explains the scanner design.
- [AGENT.md](AGENT.md) contains collaboration and change rules.
- [ADR-001.md](ADR-001.md) records the local-first, evidence-first decision.
- [ADR-002.md](ADR-002.md) records the profile, onboarding-document, and terminal-question decision.
- [schemas/report.schema.json](schemas/report.schema.json) defines the JSON contract.
