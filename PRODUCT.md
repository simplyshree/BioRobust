# Product brief: BioRobust v0.4

## Product promise

BioRobust helps researchers and maintainers understand unfamiliar biological software repositories, identify reproducibility and reuse risks, and produce evidence-backed reports before running or extending the software.

## Problem

Open-source biological software is abundant but difficult to evaluate quickly. A repository may have a useful algorithm yet lack clear entry points, tests, dependency constraints, reference-data provenance, citation metadata, or portable execution instructions. These signals are scattered across README files, source trees, workflows, manifests, and CI configuration.

People need a safe first pass that explains what is observable, what is missing, and what should be reviewed by a human or domain expert.

## Target users

- Researchers choosing biological software for a new analysis.
- Maintainers preparing a biological repository for reuse.
- Bioinformatics and computational biology students learning an unfamiliar codebase.
- Infrastructure and platform teams screening research software before controlled use.
- Curators building evidence-based catalogs of open-source biological tools.
- AI-assisted developers who need a local evidence pack before asking an assistant to explain or extend a repository.

## Goals

- Make a repository understandable from a local folder or Git URL with one starter command.
- Cover biological software broadly while keeping genomic checks specialized and explicit.
- Produce reports that preserve evidence, uncertainty, limitations, recommendations, and snapshot identity.
- Help a human prepare a controlled reproduction or reuse attempt.
- Remain free, open source, local-first, deterministic, and useful without an online AI service.
- Provide an extension seam for future domain profiles without changing the core report contract.

## Non-goals

- Certifying scientific correctness, clinical suitability, regulatory compliance, or security.
- Producing a universal biological quality score.
- Detecting whether code or documentation was written by AI.
- Executing arbitrary repository code by default.
- Replacing vulnerability scanners, package registries, workflow engines, or domain experts.
- Pretending that broad marker detection is complete domain understanding.

## Main workflow

1. The user points BioRobust at a local repository or an HTTP(S) Git URL.
2. BioRobust clones a URL into a local cache when necessary and never executes the target during the default scan.
3. The profile resolver chooses the least-specialized useful profile: workflow, bioinformatics, biology, or generic.
4. Static checks inspect bounded repository files, metadata, workflows, documentation, and configuration.
5. Each check returns a stable rule ID, status, severity, confidence, evidence, limitation, and recommendation.
6. The user opens a Markdown, PDF, HTML, or JSON report and asks focused questions in the terminal.
7. The user decides what to inspect, reproduce, or validate next.

## v0.4 scope

The broad `biology` profile applies the generic repository checks to biological software without assuming genomic inputs. The specialized `bioinformatics`, `genomics`, and `genomics-workflow` profiles retain the existing genomic evidence rules. Automatic detection recognizes conservative signals for genomics, transcriptomics, proteomics, metabolomics, synthetic biology, neuroscience, imaging, systems biology, ecology, and related areas.

The v0.4 launch also includes a public README, contribution guide, Apache-2.0 license, changelog, architecture decision record, launch announcement draft, and CI coverage for broad biology profile selection and PDF output.

## Success criteria

- A new user can understand the purpose and limitations from the first README screen.
- `biorobust start .` works for local biological and scientific repositories without profile knowledge.
- `biorobust start URL` clones and scans an open Git repository locally.
- Automatic selection chooses `biology` for a non-genomic biology fixture and `generic` for an unrelated fixture.
- Existing genomic repositories continue selecting `bioinformatics` or `genomics-workflow` when appropriate.
- Reports are available in Markdown, PDF, HTML, and JSON without changing the evidence model.
- The scanner never imports or executes target code in the default path.
- CI passes on Python 3.11, 3.12, 3.13, and 3.14.
- The project has an explicit license and contributor workflow.
- External pilots on the SBOL specification repository, SeqTrainer, and a broader biological repository produce reviewable local reports.

## Constraints

- Python CLI and local filesystem are the v0.4 runtime boundary.
- Static checks must be bounded, deterministic apart from report timestamps, and safe on untrusted repositories.
- Missing evidence must remain `unknown` or `manual_review`, not silently become `pass`.
- Existing rule IDs and profile names remain compatible.
- Generated reports are local artifacts and are not committed as source fixtures.

## Future extensions

- Calibrated profiles for protein science, imaging, neuroscience, ecology, and other domains.
- Adapters for WorkflowHub, Bioconda, OSV, OpenSSF Scorecard, RO-Crate, and GA4GH metadata.
- Optional sandboxed dry runs for selected workflow engines.
- Maintainer-facing badges only after real-repository calibration.
- A tested third-party profile plugin contract.
