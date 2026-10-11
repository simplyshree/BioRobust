from pathlib import Path

ROOT = Path(__file__).parent

def test_validation():
    assert (ROOT / "reads.fastq").exists()
    assert (ROOT / "actual.vcf").read_text() == (ROOT / "expected.vcf").read_text()

