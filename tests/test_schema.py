import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from biorobust.scanner import scan


ROOT = Path(__file__).parent
FIXTURES = ROOT / "fixtures"
SCHEMA = ROOT.parent / "schemas" / "report.schema.json"


class SchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.validator = Draft202012Validator(schema, format_checker=FormatChecker())

    def test_supported_profiles_produce_schema_valid_reports(self) -> None:
        fixture_by_profile = {
            "generic": FIXTURES / "documentation_only",
            "biology": FIXTURES / "biology_tool_repo",
            "bioinformatics": FIXTURES / "bioinformatics_tool_repo",
            "genomics": FIXTURES / "genomics_repo",
            "genomics-workflow": FIXTURES / "genomics_repo",
        }
        for profile, path in fixture_by_profile.items():
            with self.subTest(profile=profile):
                report = scan(path, profile)
                errors = list(self.validator.iter_errors(report.as_dict()))
                self.assertEqual(errors, [], "\n".join(error.message for error in errors))

    def test_biology_is_an_explicit_schema_profile(self) -> None:
        report = scan(FIXTURES / "biology_tool_repo", "biology")
        self.assertEqual(report.profile, "biology")
        self.assertFalse(list(self.validator.iter_errors(report.as_dict())))
