workflow {
  reads = channel.fromPath('tests/reads.fastq')
  CALL(reads)
}

process CALL {
  input:
  path reads
  output:
  path 'out.vcf'
  script:
  """
  caller --reference references/missing.fa --reads ${reads} > out.vcf
  """
}

