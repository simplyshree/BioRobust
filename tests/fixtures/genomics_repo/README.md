# Example variant workflow

This example maps FASTQ reads to the GRCh38 reference and emits a VCF.
The reference FASTA is the local deterministic mock reference recorded in
`references/SHA256SUMS`.

The smoke test compares `tests/actual.vcf` with `tests/expected.vcf` and
checks that the input fixture exists.


