from pathlib import Path


ROOT = Path(__file__).parent


def test_known_answer():
    input_reads = ROOT / "reads.fastq"
    actual = ROOT / "actual.vcf"
    expected = ROOT / "expected.vcf"
    assert input_reads.exists()
    assert actual.read_text(encoding="utf-8") == expected.read_text(encoding="utf-8")


