nextflow.enable.dsl=2

workflow {
  reads = channel.fromPath('tests/reads.fastq.gz')
  CALL_VARIANTS(reads, params.reference)
}

process CALL_VARIANTS {
  input:
  path reads
  output:
  path 'variants.vcf'
  script:
  """
  tool --reference references/GRCh38.fa --reads ${reads} > variants.vcf
  """
}

