# BioRobust scientific calibration plan

BioRobust is not scientifically validated by the existence of this plan. The purpose of this document is to define a reproducible pilot before making claims about calibration or usefulness.

## Pilot corpus

Assemble 15–30 public biological and scientific software repositories, pinned to
a release tag or commit. Cover:

- Genomics, variant calling, RNA-seq, metagenomics, and sequence analysis.
- Proteomics, metabolomics, synthetic biology, neuroscience, imaging, systems
  biology, ecology, and computational biology.
- Nextflow and Snakemake, with a smaller CWL/WDL sample if available.
- Strong, mixed, and weak documentation/reproducibility practices.
- Stand-alone libraries, command-line tools, specifications, and end-to-end
  workflows.

Record repository URL, pinned commit/release, license, workflow engine, domain, and the reason for inclusion. Do not place external repositories in the normal unit-test suite; they change independently and may be unavailable.

## Review protocol

For each repository and rule:

1. A reviewer records the expected human judgment before reading the BioRobust result.
2. BioRobust scans the pinned checkout with the network disabled.
3. A reviewer records the observed output and whether the cited evidence supports the claim.
4. Disagreements are discussed and retained, rather than silently resolved in favor of the tool.
5. Rule changes are versioned and re-run against the complete corpus.

## Measures

Track per rule:

- True/false positive and negative counts relative to the documented human judgment.
- Evidence completeness: whether a reviewer can locate the cited artifact.
- Reviewer disagreement rate and the reason for disagreement.
- Unknown/manual-review rate.
- Changes in results across rule-pack versions.

Do not aggregate these measures into a global repository quality score. Report each rule's behavior and uncertainty separately.

## Calibration record

Store a versioned table outside the unit-test fixtures with columns for repository, pinned revision, rule ID, expected judgment, BioRobust status, evidence review, reviewer, disagreement reason, and rule-pack version. A future release may add a checked-in template such as `docs/validation-record.csv` after the pilot corpus and reviewers are selected.

## Claim boundary

Until this pilot is completed and reviewed, describe BioRobust as an evidence
profiler under calibration. Do not describe it as scientifically validated,
clinically certified, or a proof of reproducibility.


