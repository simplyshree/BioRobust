import contextlib
import copy
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from biorobust.cli import main
from biorobust.models import EVIDENCE_TYPES, SEVERITIES, STATUSES, Evidence, Finding
from biorobust.scanner import scan


ROOT = Path(__file__).parent
FIXTURE = ROOT / "fixtures" / "genomics_repo"
SCHEMA = ROOT.parent / "schemas" / "report.schema.json"


class ScannerTests(unittest.TestCase):
    def test_scientific_fixture_produces_evidence(self) -> None:
        report = scan(FIXTURE, "genomics")
        by_id = {finding.rule_id: finding for finding in report.findings}

        self.assertEqual(by_id["DNA-WF-001"].status, "pass")
        self.assertEqual(by_id["DNA-WF-002"].status, "pass")
        self.assertEqual(by_id["DNA-REF-001"].status, "pass")
        self.assertEqual(by_id["DNA-VAL-001"].status, "pass")
        self.assertEqual(by_id["DNA-PORT-001"].status, "pass")
        self.assertEqual(by_id["SEC-001"].status, "pass")
        self.assertEqual(report.decision, "evidence_found")

    def test_generated_report_validates_against_schema(self) -> None:
        report = scan(FIXTURE, "genomics")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(report.as_dict()), key=lambda error: error.path)
        self.assertEqual(errors, [], "\n".join(error.message for error in errors))

        malformed = copy.deepcopy(report.as_dict())
        malformed["findings"][0]["status"] = "maybe"
        self.assertTrue(list(validator.iter_errors(malformed)))

    def test_structured_evidence_and_all_enums(self) -> None:
        for status in STATUSES:
            for severity in SEVERITIES:
                finding = Finding("TEST-001", "Test", "A test claim", status, severity, 0.5, "Message")
                self.assertEqual(finding.as_dict()["evidence"][0]["evidence_type"], "absence")
        for evidence_type in EVIDENCE_TYPES:
            evidence = Evidence("README.md", "Observation", evidence_type, 0.5)
            self.assertEqual(evidence.as_dict()["path"], "README.md")
        with self.assertRaises(ValueError):
            Finding("TEST-001", "Test", "Claim", "invalid", "low", 0.5, "Message")
        with self.assertRaises(ValueError):
            Evidence(None, "Observation", "artifact", 2.0)

    def test_manifest_is_stable_and_only_timestamp_changes(self) -> None:
        first = scan(FIXTURE, "genomics").as_dict()
        second = scan(FIXTURE, "genomics").as_dict()
        self.assertEqual(first["manifest_hash"], second["manifest_hash"])
        first["generated_at"] = "fixed"
        second["generated_at"] = "fixed"
        self.assertEqual(first, second)

    def test_cli_json_and_html_output(self) -> None:
        json_stdout = io.StringIO()
        with contextlib.redirect_stdout(json_stdout):
            self.assertEqual(main(["scan", str(FIXTURE), "--profile", "genomics", "--format", "json"]), 0)
        payload = json.loads(json_stdout.getvalue())
        self.assertEqual(payload["schema_version"], "0.2")
        self.assertIn("manifest_hash", payload)

        html_stdout = io.StringIO()
        with contextlib.redirect_stdout(html_stdout):
            self.assertEqual(main(["scan", str(FIXTURE), "--profile", "genomics", "--format", "html"]), 0)
        self.assertIn("BioRobust evidence report", html_stdout.getvalue())
        self.assertIn("DNA-REF-001", html_stdout.getvalue())

    def test_cli_rules_and_explain(self) -> None:
        rules_stdout = io.StringIO()
        with contextlib.redirect_stdout(rules_stdout):
            self.assertEqual(main(["rules"]), 0)
        self.assertIn("DNA-REF-001", rules_stdout.getvalue())

        explain_stdout = io.StringIO()
        with contextlib.redirect_stdout(explain_stdout):
            self.assertEqual(main(["explain", "DNA-REF-001"]), 0)
        self.assertIn("Reference genome provenance", explain_stdout.getvalue())

        profiles_stdout = io.StringIO()
        with contextlib.redirect_stdout(profiles_stdout):
            self.assertEqual(main(["profiles"]), 0)
        self.assertIn("sbol", profiles_stdout.getvalue())

    def test_sbol_profile_is_conservative_and_auto_detected(self) -> None:
        fixture = ROOT / "fixtures" / "sbol_repo"
        report = scan(fixture, "sbol")
        by_id = {finding.rule_id: finding for finding in report.findings}
        self.assertEqual(by_id["SBOL-001"].status, "pass")
        self.assertEqual(by_id["SBOL-002"].status, "pass")
        self.assertEqual(by_id["SBOL-003"].status, "pass")
        self.assertEqual(by_id["SBOL-004"].status, "manual_review")
        self.assertEqual(by_id["SBOL-005"].status, "manual_review")
        auto = scan(fixture, "auto")
        self.assertEqual(auto.profile, "sbol")

    def test_markdown_report_and_grounded_question(self) -> None:
        markdown_stdout = io.StringIO()
        with contextlib.redirect_stdout(markdown_stdout):
            self.assertEqual(main(["scan", str(FIXTURE), "--format", "markdown"]), 0)
        self.assertIn("# BioRobust evidence report", markdown_stdout.getvalue())

        answer_stdout = io.StringIO()
        with contextlib.redirect_stdout(answer_stdout):
            self.assertEqual(main(["ask", str(FIXTURE), "Is this repository reproducible?"]), 0)
        self.assertIn("REPRO-001", answer_stdout.getvalue())
        self.assertIn("static, evidence-grounded", answer_stdout.getvalue())

    def test_invalid_profile_and_missing_path(self) -> None:
        with self.assertRaises(ValueError):
            scan(FIXTURE, "not-a-profile")
        with self.assertRaises(ValueError):
            scan(ROOT / "fixtures" / "does-not-exist", "genomics")
        self.assertEqual(main(["scan", str(ROOT / "fixtures" / "does-not-exist")]), 2)

    def test_credential_placeholder_is_not_a_false_positive(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT, ignore_cleanup_errors=True) as directory:
            path = Path(directory)
            (path / "README.md").write_text("Project", encoding="utf-8")
            (path / "LICENSE").write_text("Apache-2.0", encoding="utf-8")
            (path / "config.py").write_text('api_key = "${API_KEY}"\n', encoding="utf-8")
            finding = next(item for item in scan(path, "generic").findings if item.rule_id == "SEC-001")
            self.assertEqual(finding.status, "pass")

    def test_ignored_directories_and_symlinks_are_not_scanned_or_executed(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT, ignore_cleanup_errors=True) as directory:
            path = Path(directory)
            (path / "README.md").write_text("Project", encoding="utf-8")
            (path / ".git").mkdir()
            (path / ".git" / "secret.py").write_text('raise RuntimeError("must not execute")', encoding="utf-8")
            (path / "node_modules").mkdir()
            (path / "node_modules" / "ignored.txt").write_text("ignored", encoding="utf-8")
            outside = path / "outside.txt"
            outside.write_text("outside", encoding="utf-8")
            link = path / "linked.txt"
            try:
                os.symlink(outside, link)
            except (OSError, NotImplementedError):
                link = None
            report = scan(path, "generic")
            manifest = report.manifest_hash
            self.assertNotIn("secret.py", json.dumps(report.as_dict()))
            self.assertNotIn("ignored.txt", json.dumps(report.as_dict()))
            if link is not None:
                self.assertNotIn("linked.txt", json.dumps(report.as_dict()))
            self.assertTrue(manifest)

    def test_scientific_negative_and_ambiguous_fixtures(self) -> None:
        missing_reference = scan(ROOT / "fixtures" / "missing_reference", "genomics")
        missing_by_id = {finding.rule_id: finding for finding in missing_reference.findings}
        self.assertEqual(missing_by_id["DNA-REF-001"].status, "fail")
        self.assertEqual(missing_by_id["DNA-WF-002"].status, "fail")

        placeholder = scan(ROOT / "fixtures" / "placeholder_checksum", "genomics")
        self.assertNotEqual(next(item for item in placeholder.findings if item.rule_id == "DNA-REF-001").status, "pass")

        mutable = scan(ROOT / "fixtures" / "mutable_container", "genomics")
        self.assertEqual(next(item for item in mutable.findings if item.rule_id == "DNA-PORT-001").status, "unknown")

        missing_expected = scan(ROOT / "fixtures" / "missing_expected", "genomics")
        self.assertEqual(next(item for item in missing_expected.findings if item.rule_id == "DNA-VAL-001").status, "unknown")

        assert_true = scan(ROOT / "fixtures" / "assert_true_only", "genomics")
        self.assertEqual(next(item for item in assert_true.findings if item.rule_id == "DNA-VAL-001").status, "manual_review")

        documentation_only = scan(ROOT / "fixtures" / "documentation_only", "genomics")
        self.assertNotEqual(next(item for item in documentation_only.findings if item.rule_id == "DNA-REF-001").status, "pass")
        self.assertNotEqual(next(item for item in documentation_only.findings if item.rule_id == "DNA-VAL-001").status, "pass")


