nextflow.enable.dsl=2

params.reference = 'references/GRCh38.fa'

workflow {
  reads = channel.fromPath('tests/reads.fastq')
  reference = file(params.reference)
  CALL_VARIANTS(reads, reference)
}

process CALL_VARIANTS {
  input:
  path reads
  path reference
  output:
  path 'variants.vcf'
  script:
  """
  deterministic-mock-caller --assembly GRCh38 --reference ${reference} --reads ${reads} > variants.vcf
  """
}


