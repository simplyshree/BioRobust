# Contributing to BioRobust

Thank you for helping make open-source biological software easier to understand and reuse.

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python -m unittest discover -s tests -v
```

BioRobust is a local Python CLI. No hosted service or container is required for development.

## What makes a good contribution

- A focused change with a clear user outcome.
- Tests for non-trivial behavior.
- Evidence-backed checks that identify paths and observations.
- Explicit handling of missing evidence as `unknown` or `manual_review`.
- Documentation updates when CLI behavior, profiles, reports, or scope changes.
- No claims of scientific, clinical, security, or AI certification that the evidence model cannot support.

## Adding a check

1. Define the narrow claim and stable rule ID.
2. Return a `Finding` with status, severity, confidence, evidence, limitations, and recommendation.
3. Use an explicit absence observation when the artifact is not found.
4. Add positive, negative, and ambiguous fixtures where practical.
5. Add or update the rule catalog, JSON schema expectations, tests, and user documentation.
6. Explain domain assumptions and false-positive risks in the change description.

## Adding a profile

Profiles should combine existing checks or add narrowly scoped domain checks. Keep genomic rules behind genomic profiles. A new profile should have:

- a documented purpose and detector;
- representative fixture repositories;
- explicit selection behavior in `auto`;
- tests proving it does not affect unrelated profiles;
- an ADR when the profile changes the product boundary or report semantics.

## Pull requests

Include:

- what changed and why;
- commands run and their results;
- affected profiles, rule IDs, and report formats;
- assumptions and known limitations;
- screenshots or sample output when presentation changed.

Keep external repository scans and generated PDFs local unless a maintainer explicitly requests a checked-in artifact.
