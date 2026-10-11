# BioRobust pilot scan results

These are static pilot scans, not scientific validation of BioRobust or of the
target projects. The repositories were cloned locally and scanned without
executing their code or making network requests from the scanner.

## Targets

| Repository | Pinned checkout | Selected profile | Decision | Report |
|---|---|---|---|---|
| [SynBioDex/SBOL-specification](https://github.com/SynBioDex/SBOL-specification) | `d5857b8250dafe7fd35d08c95b8bdffb7f07be18` | `sbol` | `needs_attention` | `outputs/SBOL-specification-BioRobust.md` |
| [SynBioDex/SeqTrainer](https://github.com/SynBioDex/SeqTrainer) | `400934ba41d813885e4c0c81e787029a7b0a632e` | `sbol` | `review_required` | `outputs/SeqTrainer-BioRobust.md` |

## SBOL-specification

The scanner detected SBOL artifacts, SBOL version signals, and CI configuration.
It also found generic XML evidence, but marked the serialization rule for
manual review because the repository includes RDF/Turtle-like material that the
static MVP does not parse with an SBOL-aware validator. It did not detect local
tests, validator integration, or interoperability evidence. The missing standard
license artifact was reported as a failure and should be manually checked against
the repository's actual licensing conventions before drawing a legal conclusion.

## SeqTrainer

The scanner detected SBOL data, tests, a license, declared dependencies, and a
`uv.lock` lockfile. It selected the SBOL profile because the repository combines
SBOL data and tooling with machine-learning code. SBOL validation and
interoperability were both reported as `manual_review`: the repository contains
signals for those activities, but BioRobust did not execute the validator,
training pipeline, or cross-tool round trip.

## Interpretation

These results demonstrate the intended workflow: clone a repository, run a
profile, receive a Markdown review document and JSON automation artifact, and
use `biorobust ask` for focused evidence questions. They also identify the next
engineering step: add an explicit SBOL-aware validator adapter and separate
scientific ML checks from SBOL serialization checks instead of treating all
SBOL-related text as one signal.
