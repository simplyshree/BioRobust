# External pilot scan results

These pilots are static calibration exercises, not scientific validation of
BioRobust or of the target projects. Repositories were cloned locally and
scanned without executing their code or making network requests from the
scanner.

## What the pilots test

The first external pilots are used to check whether a new user can:

1. clone a genomic or bioinformatics repository;
2. run `biorobust start PATH --output report.md`;
3. understand the repository’s purpose, entry points, tests, dependencies,
   data, and workflow signals from the report;
4. identify missing evidence before attempting a controlled replication; and
5. ask focused questions with `biorobust ask` in the terminal.

## Interpretation

Pilot results should be read as evidence about observable repository practice,
not as a quality score or a claim that the scientific method is correct. A
`pass` means only that a narrow artifact or signal was detected. `unknown` and
`manual_review` identify the next questions a maintainer or researcher should
answer.

Future pilots should cover command-line tools, Python/R libraries, reference
data packages, sequencing workflows, variant callers, annotation tools, and
repositories with no bundled sequence data. Each pilot should record the pinned
revision, selected profile, report, limitations, and the human interpretation.
