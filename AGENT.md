# Agent guide

## Working rules

- Keep the repository runnable after every change.
- Make small, reviewable changes with tests for non-trivial logic.
- Preserve the evidence-first contract: do not turn `unknown` into `pass` for convenience.
- Do not add workflow execution, network calls, clinical claims, or a global score without updating PRODUCT.md and an ADR.
- Update README.md, ARCHITECTURE.md, or PRODUCT.md when behavior or scope changes.
- Avoid broad refactors until the project brief and architecture are revisited.

## Division of labor

Use ChatGPT for ambiguity reduction, research, scope decisions, rule design, and sequencing. Use Codex for concrete file edits, tests, refactors within the agreed boundary, and running verification commands.

Before a large refactor or a new profile, return to the product and architecture documents and record the decision. Create an ADR when there are multiple reasonable designs or the choice is likely to be revisited.

## Handoff format

Every implementation task should state:

1. the rule or user behavior being changed;
2. files expected to change;
3. acceptance criteria;
4. tests to run;
5. assumptions and known limitations.

Report progress with concrete evidence: commands run, tests passed, files changed, and unresolved risks. Surface blockers instead of silently expanding scope.

