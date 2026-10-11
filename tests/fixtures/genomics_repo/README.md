# Example variant workflow

This example maps FASTQ reads to the GRCh38 reference and emits a VCF.
The reference FASTA is downloaded from the project release and verified with
the SHA256 checksum recorded in `references/SHA256SUMS`.

The smoke test compares the output with `tests/expected.vcf`.

