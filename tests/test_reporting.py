import copy
import io
import json
import unittest
from pathlib import Path

from pypdf import PdfReader

from biorobust.models import Evidence, Finding, ScanReport
from biorobust.pdf_styles import status_label
from biorobust.report_options import DETAIL_LEVELS, THEME_NAMES, RenderOptions
from biorobust.reporting import render_html, render_markdown, write_json, write_pdf
from biorobust.scanner import scan


ROOT = Path(__file__).parent
FIXTURE = ROOT / "fixtures" / "genomics_repo"


def _pdf_text(stream: io.BytesIO) -> str:
    stream.seek(0)
    return "\n".join(page.extract_text() or "" for page in PdfReader(stream).pages)


class ReportingTests(unittest.TestCase):
    def test_render_options_are_immutable_and_bounded(self) -> None:
        options = RenderOptions(theme="minimal", detail="minimal")
        self.assertEqual(options.evidence_limit, 2)
        with self.assertRaises(Exception):
            options.theme = "scientific"
        self.assertEqual(set(THEME_NAMES), {"scientific", "minimal", "high-contrast"})
        self.assertEqual(set(DETAIL_LEVELS), {"minimal", "standard", "verbose"})

    def test_pdf_matrix_is_readable_and_uses_text_statuses(self) -> None:
        report = scan(FIXTURE, "genomics")
        for theme in THEME_NAMES:
            for detail in DETAIL_LEVELS:
                with self.subTest(theme=theme, detail=detail):
                    stream = io.BytesIO()
                    write_pdf(report, stream, RenderOptions(theme=theme, detail=detail))
                    text = _pdf_text(stream)
                    self.assertIn("BioRobust Evidence Report", text)
                    self.assertIn("DNA-REF-001", text)
                    self.assertIn(status_label("pass"), text)

    def test_pdf_rendering_does_not_mutate_report(self) -> None:
        report = scan(FIXTURE, "genomics")
        before = copy.deepcopy(report.as_dict())
        write_pdf(report, io.BytesIO(), RenderOptions(detail="minimal"))
        self.assertEqual(report.as_dict(), before)

    def test_detail_level_controls_human_evidence_without_changing_json(self) -> None:
        report = ScanReport.create(
            target="fixture",
            profile="biology",
            tool_version="0.4.1",
            rule_pack_version="0.4.1",
            manifest_hash="0" * 64,
            generated_at="2026-01-01T00:00:00+00:00",
            findings=[
                Finding(
                    "TEST-001",
                    "Synthetic evidence",
                    "A test claim",
                    "pass",
                    "low",
                    0.9,
                    "An assessment.",
                    evidence=[
                        Evidence(f"evidence-{index}.txt", f"Observation {index}", "artifact", 0.8)
                        for index in range(1, 8)
                    ],
                    limitations=["This is a test fixture."],
                    recommendation="Review the evidence.",
                )
            ],
        )
        before = copy.deepcopy(report.as_dict())
        minimal = io.BytesIO()
        verbose = io.BytesIO()
        write_pdf(report, minimal, RenderOptions(detail="minimal"))
        write_pdf(report, verbose, RenderOptions(detail="verbose"))
        minimal_text = _pdf_text(minimal)
        verbose_text = _pdf_text(verbose)
        self.assertIn("evidence-1.txt", minimal_text)
        self.assertIn("evidence-2.txt", minimal_text)
        self.assertNotIn("evidence-3.txt", minimal_text)
        self.assertIn("evidence-7.txt", verbose_text)
        self.assertEqual(report.as_dict(), before)

    def test_html_has_accessible_table_and_escaped_content(self) -> None:
        report = ScanReport.create(
            target="fixture",
            profile="biology",
            tool_version="0.4.1",
            rule_pack_version="0.4.1",
            manifest_hash="0" * 64,
            generated_at="2026-01-01T00:00:00+00:00",
            findings=[Finding("TEST-001", "Title", "<unsafe claim>", "fail", "high", 1.0, "Message")],
        )
        output = render_html(report, RenderOptions(theme="high-contrast", detail="minimal"))
        self.assertIn('<html lang="en">', output)
        self.assertIn("<caption>Evidence findings by rule</caption>", output)
        self.assertIn('scope="col"', output)
        self.assertIn("FAIL", output)
        self.assertIn("&lt;unsafe claim&gt;", output)

    def test_markdown_and_json_keep_expected_contracts(self) -> None:
        report = scan(FIXTURE, "genomics")
        markdown = render_markdown(report, RenderOptions(detail="minimal"))
        self.assertIn("Presentation:", markdown)
        self.assertIn("PASS", markdown)
        before = report.as_dict()
        stream = io.StringIO()
        write_json(report, stream)
        self.assertEqual(json.loads(stream.getvalue()), before)
