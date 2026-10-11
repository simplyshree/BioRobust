from pathlib import Path
import tempfile
import unittest

from biorobust.scanner import scan


FIXTURE = Path(__file__).parent / "fixtures" / "genomics_repo"


class ScannerTests(unittest.TestCase):
    def test_genomics_fixture_produces_evidence(self) -> None:
        report = scan(FIXTURE, "genomics")
        by_id = {finding.rule_id: finding for finding in report.findings}

        self.assertEqual(by_id["DOC-001"].status, "pass")
        self.assertEqual(by_id["META-001"].status, "pass")
        self.assertEqual(by_id["DNA-WF-001"].status, "pass")
        self.assertEqual(by_id["DNA-REF-001"].status, "pass")
        self.assertEqual(by_id["DNA-VAL-001"].status, "pass")
        self.assertEqual(by_id["SEC-001"].status, "pass")
        self.assertEqual(report.decision, "evidence_found")


    def test_missing_evidence_is_not_a_false_failure(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent, ignore_cleanup_errors=True) as directory:
            tmp_path = Path(directory)
            (tmp_path / "README.md").write_text("A tiny project", encoding="utf-8")
            (tmp_path / "LICENSE").write_text("Apache-2.0", encoding="utf-8")
            report = scan(tmp_path, "genomics")
            by_id = {finding.rule_id: finding for finding in report.findings}

            self.assertEqual(by_id["DOC-001"].status, "pass")
            self.assertEqual(by_id["DNA-REF-001"].status, "manual_review")
            self.assertEqual(by_id["DNA-VAL-001"].status, "unknown")
            self.assertEqual(report.decision, "review_required")

    def test_secret_pattern_is_high_severity(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent, ignore_cleanup_errors=True) as directory:
            tmp_path = Path(directory)
            (tmp_path / "README.md").write_text("Project", encoding="utf-8")
            (tmp_path / "config.py").write_text('api_key = "definitely-not-safe-secret"\n', encoding="utf-8")
            report = scan(tmp_path, "generic")
            finding = next(item for item in report.findings if item.rule_id == "SEC-001")
            self.assertEqual(finding.status, "fail")
            self.assertEqual(finding.severity, "high")

