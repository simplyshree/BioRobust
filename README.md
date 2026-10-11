# BioRobust

BioRobust is an evidence-based robustness profiler for open-source genomic software and workflows. It scans a local repository, looks for reproducibility and genomics-specific evidence, and produces a versioned JSON or HTML report.

It does not certify scientific correctness, security, clinical fitness, or biological truth. A result is a structured starting point for review.

## Current capabilities

- Scans without executing repository code.
- Checks project documentation, licensing, citation metadata, tests, CI, dependencies, pinning, and common credential exposure patterns.
- Detects Nextflow, Snakemake, CWL, and WDL workflow definitions.
- Looks for reference-genome provenance, known-answer validation, and portable execution environments.
- Represents `pass`, `fail`, `unknown`, `not_applicable`, and `manual_review` explicitly.
- Records structured evidence with repository-relative paths, line locations, observations, evidence type, and detector confidence.
- Records a deterministic repository manifest hash and rule-pack version.
- Emits a stable JSON report for automation and a compact HTML report for humans.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .

biorobust scan . --profile genomics --format html --output report.html
biorobust scan . --profile genomics --format json --output report.json
biorobust rules
biorobust explain DNA-REF-001
```

The scanner is also runnable without installation:

```powershell
python -m biorobust scan path\to\repository --profile genomics
```

## Scope of v0.1

The first product wedge is open-source computational genomics repositories, especially sequencing and variant-calling workflows using FASTQ, BAM/CRAM, VCF, and reference FASTA files. Nextflow and Snakemake are the primary workflow targets. Generic repository checks remain useful for stand-alone command-line tools.

Neuroscience, clinical certification, wet-lab protocols, human-genomic privacy certification, and AI-code detection are deliberately out of scope for this release.

## Development

```powershell
python -m unittest discover -s tests
```

The test fixtures under `tests/fixtures` are intentionally small and synthetic. They exercise evidence behavior, including missing references, placeholder checksums, mutable containers, missing expected outputs, and non-substantive `assert True` tests; they do not validate a real variant caller.

## Scientific interpretation

BioRobust can establish that observable repository artifacts support or fail a narrowly defined claim. It cannot establish that a method is biologically correct, that a reference is appropriate, that a workflow will run in every environment, or that a repository is clinically or scientifically certified. See [docs/validation-plan.md](docs/validation-plan.md) before interpreting future calibration results.

## Repository guide

- [PRODUCT.md](PRODUCT.md) defines the user problem and v0.1 boundary.
- [ARCHITECTURE.md](ARCHITECTURE.md) explains the scanner design.
- [AGENT.md](AGENT.md) contains collaboration and change rules.
- [ADR-001.md](ADR-001.md) records the local-first, evidence-first decision.
- [schemas/report.schema.json](schemas/report.schema.json) defines the JSON contract.


