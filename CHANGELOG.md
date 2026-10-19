# Changelog

## Unreleased

- Improved precision for bioinformatics libraries by ignoring ordinary changelog/source identifiers as genome references.
- Restricted portability detection to actual container/image declarations and Dockerfile `FROM` lines.
- Marked workflow, reference, and known-answer checks as not applicable when a repository does not contain those artifact types.
- Added regression coverage based on the scikit-bio demonstration repository.

## 0.4.0 - Public biological software scope

- Broadened the product positioning from genomic-only repositories to open-source biological and scientific software.
- Added the broad `biology` profile for biological repositories without genomic assumptions.
- Changed automatic profile selection to workflow -> bioinformatics -> biology -> generic.
- Changed the default `scan` profile to `auto`.
- Kept existing genomic profiles and `DNA-*` rule IDs backward-compatible.
- Added broad biology detection fixtures and CI coverage.
- Added public launch documentation, contribution guidance, Apache-2.0 licensing, and LinkedIn announcement copy.
- Added install and release documentation plus a GitHub Release workflow that builds source and wheel artifacts.
