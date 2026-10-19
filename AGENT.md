# Agent guide

## Project contract

BioRobust is a local, evidence-first repository analysis tool for open-source biological and scientific software. Preserve that contract in every change.

- Keep the repository runnable after every change.
- Make small, reviewable changes and add tests for non-trivial logic.
- Preserve explicit evidence, uncertainty, limitations, and recommendations.
- Do not turn `unknown` into `pass` for convenience.
- Do not add a global score, scientific certification, clinical claim, hosted service, arbitrary execution, or AI-authorship detector without revisiting `PRODUCT.md` and creating an ADR.
- Keep genomic checks behind genomic profiles; do not add DNA-specific assumptions to `generic` or `biology`.
- Update README.md, ARCHITECTURE.md, PRODUCT.md, or CHANGELOG.md when behavior or scope changes.
- Keep generated reports and external repository clones out of Git.
- Surface assumptions, false-positive risks, and blockers explicitly.

## Division of labor

Use ChatGPT for ambiguity reduction, research, scope decisions, rule design, architecture tradeoffs, sequencing, and review of whether implementation matches the product promise.

Use Codex for concrete file edits, implementation, refactoring within the approved boundary, tests, documentation wiring, and verification commands.

Before a large refactor, new profile, new external integration, or execution capability, revisit `PRODUCT.md` and `ARCHITECTURE.md`. Create an ADR when multiple reasonable designs exist or the decision is likely to be revisited.

## Evidence rules

- Every finding must have a stable rule ID and evidence or an explicit absence observation.
- Evidence must identify a repository path when possible and must not be fabricated from prose alone.
- Confidence describes detector confidence, not scientific truth.
- Profile detection must be conservative and explainable.
- New biological-domain checks need representative positive, negative, and ambiguous fixtures.
- Do not use a keyword as proof when an artifact or structured declaration is required.

## Handoff format

Every implementation task should state:

1. The user behavior or rule being changed.
2. The files or subsystems expected to change.
3. Acceptance criteria.
4. Tests and verification commands.
5. Assumptions, limitations, and external dependencies.

Report progress with concrete evidence: commands run, tests passed, files changed, commits, and unresolved risks. Do not silently expand scope.

## Release discipline

Before a public release:

- Run the complete test suite.
- Run at least one local scan with `auto` and one explicit profile.
- Check all report formats that changed.
- Inspect README commands from a clean environment when practical.
- Review the launch copy for overclaims about science, security, clinical use, or AI.
- Record meaningful scope or architecture changes in the changelog and an ADR.
