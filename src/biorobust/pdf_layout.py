"""Readable, evidence-preserving PDF layout for BioRobust reports."""

from __future__ import annotations

from typing import BinaryIO

from .models import ScanReport
from .pdf_styles import _pdf_escape, make_pdf_styles, status_label
from .report_options import RenderOptions


def _paragraph(value: object, style):
    from reportlab.platypus import Paragraph

    return Paragraph(_pdf_escape(value), style)


def _rich(value: str, style):
    from reportlab.platypus import Paragraph

    return Paragraph(value, style)


def _location(evidence) -> str:
    location = evidence.path or "(absence observation)"
    if evidence.start_line:
        location += f":{evidence.start_line}"
        if evidence.end_line and evidence.end_line != evidence.start_line:
            location += f"-{evidence.end_line}"
    return location


def _evidence_blocks(finding, options: RenderOptions, styles):
    palette = styles.palette
    evidence = finding.evidence if options.evidence_limit is None else finding.evidence[: options.evidence_limit]
    blocks = []
    for item in evidence:
        blocks.append(
            _rich(
                f"<b>{_pdf_escape(_location(item))}</b>: {_pdf_escape(item.observation)} "
                f"<font color='{palette.muted}'>({_pdf_escape(item.evidence_type)}, confidence {item.detector_confidence:.2f})</font>",
                styles.secondary,
            )
        )
    return blocks


def _finding_block(finding, options: RenderOptions, styles):
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, Table, TableStyle

    palette = styles.palette
    status = status_label(finding.status)
    header = Table(
        [[
            _rich(
                f"<b>{_pdf_escape(finding.rule_id)}</b><br/>{_pdf_escape(finding.title)}",
                styles.finding_header,
            ),
            _rich(
                f"<b><font color='{palette.status_foreground(finding.status)}'>{_pdf_escape(status)}</font></b><br/>"
                f"{_pdf_escape(finding.severity)} severity; confidence {finding.confidence:.2f}",
                styles.secondary,
            ),
        ]],
        colWidths=[124 * mm, 52 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(palette.panel)),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor(palette.status_background(finding.status))),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(palette.border)),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor(palette.border)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    blocks = [
        header,
        _rich(f"<b>Claim:</b> {_pdf_escape(finding.claim)}", styles.body),
        _rich(f"<b>Assessment:</b> {_pdf_escape(finding.message)}", styles.body),
        _rich("<b>Evidence</b>", styles.body),
    ]
    blocks.extend(_evidence_blocks(finding, options, styles))
    if finding.recommendation:
        blocks.append(_rich(f"<b>Recommendation:</b> {_pdf_escape(finding.recommendation)}", styles.body))
    if finding.limitations:
        blocks.append(_rich("<b>Limitations</b>", styles.body))
        blocks.extend(_rich(f"- {_pdf_escape(value)}", styles.secondary) for value in finding.limitations)
    blocks.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor(palette.border), spaceBefore=4, spaceAfter=7))
    return blocks


def build_story(report: ScanReport, options: RenderOptions):
    """Build the ReportLab story without mutating ``report``."""
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    styles = make_pdf_styles(options)
    palette = styles.palette
    story = [
        Paragraph("BioRobust Evidence Report", styles.title),
        _rich(f"<b>Target:</b> {_pdf_escape(report.target)}", styles.meta),
        _rich(
            f"<b>Profile:</b> {_pdf_escape(report.profile)} &nbsp;&nbsp; "
            f"<b>Decision:</b> {_pdf_escape(report.decision)} &nbsp;&nbsp; "
            f"<b>Generated:</b> {_pdf_escape(report.generated_at)}",
            styles.meta,
        ),
        _rich(
            f"<b>Rule pack:</b> {_pdf_escape(report.rule_pack_version)} &nbsp;&nbsp; "
            f"<b>Manifest hash:</b> {_pdf_escape(report.manifest_hash)}",
            styles.meta,
        ),
        Spacer(1, 4),
        Paragraph("Summary", styles.section),
    ]

    summary_cells = []
    for status, count in report.counts.items():
        foreground = palette.status_foreground(status)
        summary_cells.append(
            _rich(
                f"<b><font color='{foreground}'>{_pdf_escape(status_label(status))}</font></b><br/>"
                f"<font size='15'>{count}</font>",
                styles.body,
            )
        )
    summary_table = Table([summary_cells], colWidths=[35.2 * mm] * len(summary_cells))
    summary_table.setStyle(
        TableStyle(
            [
                *[("BACKGROUND", (index, 0), (index, 0), colors.HexColor(palette.status_background(status))) for index, status in enumerate(report.counts)],
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(palette.border)),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor(palette.border)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([summary_table, Paragraph("Findings", styles.section)])
    for finding in report.findings:
        story.extend(_finding_block(finding, options, styles))

    story.append(Paragraph("Scanner limitations", styles.section))
    story.extend(_rich(f"- {_pdf_escape(value)}", styles.body) for value in report.scanner_limitations)
    story.append(Paragraph("Notes", styles.section))
    story.extend(_rich(f"- {_pdf_escape(value)}", styles.body) for value in report.notes)
    return story, styles


def write_pdf_document(report: ScanReport, stream: BinaryIO, options: RenderOptions) -> None:
    """Write a portrait A4 PDF using the selected readable layout."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate
    except ImportError as exc:  # pragma: no cover - dependency is declared in pyproject.toml
        raise RuntimeError("PDF output requires ReportLab; install with 'python -m pip install biorobust'") from exc

    story, styles = build_story(report, options)
    pagesize = A4
    left_margin = 17 * mm
    right_margin = 17 * mm
    top_margin = 15 * mm
    bottom_margin = 17 * mm

    document = SimpleDocTemplate(
        stream,
        pagesize=pagesize,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
        title="BioRobust Evidence Report",
        author="BioRobust",
    )

    def footer(canvas, doc) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor(styles.palette.border))
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, 10 * mm, pagesize[0] - doc.rightMargin, 10 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor(styles.palette.muted))
        canvas.drawString(doc.leftMargin, 5.5 * mm, "BioRobust - static, evidence-first repository review")
        canvas.drawRightString(pagesize[0] - doc.rightMargin, 5.5 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=footer, onLaterPages=footer)
