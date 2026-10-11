# Product brief: BioRobust

## Problem

Researchers and maintainers often cannot tell whether a genomic repository is merely available or is reproducible, inspectable, portable, and safe to reuse. Existing checks are fragmented across package registries, workflow systems, security scanners, and repository conventions.

## Target users

- Bioinformatics researchers selecting a workflow or tool.
- Maintainers preparing a genomic repository for reuse.
- Infrastructure teams reviewing research software before running it.
- Curators building evidence-based catalogs of biological software.

## Goal for v0.1

Give a user a fast, reproducible report about the observable robustness signals in a local genomic repository, with evidence paths and explicit uncertainty.

## Non-goals

- Certifying that an algorithm is scientifically correct.
- Certifying clinical or regulatory compliance.
- Proving that a workflow is secure or free of vulnerabilities.
- Judging biological conclusions from source code.
- Detecting whether code was written by AI.
- Executing arbitrary repository code by default.

## Main workflow

1. User points BioRobust at a repository.
2. BioRobust selects the `genomics` profile.
3. Static checks inspect files, metadata, workflows, and documentation.
4. Each finding reports status, severity, message, evidence, and recommendation.
5. User opens JSON in automation or HTML for review.

## v0.1 acceptance criteria

- A fresh environment can install the package and run `biorobust scan .`.
- A scan is deterministic apart from the report timestamp.
- No repository code is executed during a scan.
- Every finding has a stable rule ID and evidence or a clear statement that evidence was absent.
- Missing evidence is represented as `unknown` or `manual_review`, not silently treated as a pass.
- A genomics fixture demonstrates detection of workflow, reference provenance, validation data, and portability signals.

## Next extensions

- Adapter interfaces for WorkflowHub, Bioconda, OSV, OpenSSF Scorecard, RO-Crate, and GA4GH metadata.
- Optional sandboxed dry runs for selected workflow engines.
- Versioned rule packs for RNA-seq, metagenomics, and other genomics domains.
- Maintainer-facing badges only after the underlying evidence model has been validated with real repositories.

