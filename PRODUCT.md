# Product brief: BioRobust

## Problem

Researchers and maintainers often cannot tell whether a genomic repository is merely available or is reproducible, inspectable, portable, and safe to reuse. Existing checks are fragmented across package registries, workflow systems, security scanners, and repository conventions.

## Target users

- Bioinformatics researchers selecting a workflow or tool.
- Maintainers preparing a genomic repository for reuse.
- Infrastructure teams reviewing research software before running it.
- Curators building evidence-based catalogs of biological software.

## Goal for v0.3

Give a user a fast, reproducible report about the observable robustness signals in a local biological repository, with structured evidence, explicit uncertainty, a deterministic snapshot identity, a human-readable review document, and narrowly scoped terminal answers grounded in that report.

## Non-goals

- Certifying that an algorithm is scientifically correct.
- Certifying clinical or regulatory compliance.
- Proving that a workflow is secure or free of vulnerabilities.
- Judging biological conclusions from source code.
- Detecting whether code was written by AI.
- Executing arbitrary repository code by default.

## Main workflow

1. User points BioRobust at a repository.
2. BioRobust selects an explicit profile or conservatively chooses one with `auto`.
3. Static checks inspect files, metadata, workflows, and documentation.
4. Each finding reports a claim, status, severity, confidence, structured evidence, limitations, and recommendation.
5. User opens JSON in automation, Markdown/HTML for review, or asks a focused question in the terminal.

## v0.3 acceptance criteria

- A fresh environment can install the package and run `biorobust scan .`.
- A scan is deterministic apart from the report timestamp.
- No repository code is executed during a scan.
- Every finding has a stable rule ID and evidence or a clear statement that evidence was absent.
- Missing evidence is represented as `unknown` or `manual_review`, not silently treated as a pass.
- Placeholder checksum text, generic portability prose, mutable image tags, and `assert True` do not produce scientific `pass` findings.
- A genomics fixture demonstrates detection of workflow, reference provenance, validation data, and portability signals with real local artifacts.
- The scanner supports explicit `generic`, `bioinformatics`, `genomics`, and `genomics-workflow` profiles plus conservative `auto` selection.
- A scan can emit JSON, Markdown, or HTML without changing the evidence model.
- `biorobust ask PATH QUESTION` answers from local findings and states that it did not execute repository code.
- A cloned external repository can be scanned using only its local path.

## Next extensions

- Adapter interfaces for WorkflowHub, Bioconda, OSV, OpenSSF Scorecard, RO-Crate, and GA4GH metadata.
- Optional sandboxed dry runs for selected workflow engines.
- Versioned rule packs for RNA-seq, metagenomics, neuroscience, machine-learning biology, and other domains.
- Domain adapters and opt-in sandboxed execution only after the static evidence model is calibrated.
- Maintainer-facing badges only after the underlying evidence model has been validated with real repositories.
- Pilot calibration over 15–30 pinned external repositories, as described in [docs/validation-plan.md](docs/validation-plan.md).


