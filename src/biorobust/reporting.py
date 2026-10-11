"""JSON, document, and human-readable report rendering."""

from __future__ import annotations

import html
import json
from typing import BinaryIO, TextIO

from .models import ScanReport


def write_json(report: ScanReport, stream: TextIO) -> None:
    json.dump(report.as_dict(), stream, indent=2, sort_keys=True)
    stream.write("\n")


def _evidence_html(report: ScanReport, finding) -> str:
    rows = []
    for item in finding.evidence:
        location = html.escape(item.path or "(no path: absence observation)")
        if item.start_line:
            location += f":{item.start_line}" + (f"-{item.end_line}" if item.end_line and item.end_line != item.start_line else "")
        rows.append(f"<li><code>{location}</code> — {html.escape(item.observation)} <small>({html.escape(item.evidence_type)}, confidence {item.detector_confidence:.2f})</small></li>")
    return "<ul>" + "".join(rows) + "</ul>"


def render_html(report: ScanReport) -> str:
    rows = []
    for finding in report.findings:
        limitations = " ".join(html.escape(value) for value in finding.limitations)
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(finding.rule_id)}</code></td>"
            f"<td>{html.escape(finding.title)}<br><small>{html.escape(finding.claim)}</small></td>"
            f"<td><span class=\"status {html.escape(finding.status)}\">{html.escape(finding.status)}</span><br><small>{html.escape(finding.severity)}, confidence {finding.confidence:.2f}</small></td>"
            f"<td>{html.escape(finding.message)}{_evidence_html(report, finding)}<small><strong>Limitation:</strong> {limitations}</small></td>"
            f"<td>{html.escape(finding.recommendation or '—')}</td>"
            "</tr>"
        )
    counts = " ".join(f"<span>{status}: <strong>{count}</strong></span>" for status, count in report.counts.items())
    limitations = "".join(f"<li>{html.escape(value)}</li>" for value in report.scanner_limitations)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BioRobust report</title><style>
body{{font-family:system-ui,sans-serif;max-width:1400px;margin:2rem auto;padding:0 1rem;color:#17202a;background:#fbfcfd}}
h1{{margin-bottom:.2rem}} .meta{{color:#58636f}} .summary{{display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0}}
.summary span{{padding:.45rem .7rem;background:#eef2f5;border-radius:.4rem}} table{{border-collapse:collapse;width:100%;background:white}}
th,td{{border:1px solid #dce2e7;padding:.7rem;text-align:left;vertical-align:top}} th{{background:#eef2f5}}
.status{{font-weight:700;padding:.2rem .45rem;border-radius:.3rem}} .pass{{color:#146c43;background:#d1e7dd}} .fail{{color:#842029;background:#f8d7da}}
.unknown,.manual_review{{color:#664d03;background:#fff3cd}} .not_applicable{{color:#41464b;background:#e2e3e5}}
small{{color:#58636f}} code{{font-size:.9em}} ul{{padding-left:1.2rem;margin:.4rem 0}}
</style></head><body><h1>BioRobust evidence report</h1>
<p class="meta"><strong>Target:</strong> {html.escape(report.target)}<br><strong>Profile:</strong> {html.escape(report.profile)}<br>
<strong>Decision:</strong> {html.escape(report.decision)}<br><strong>Generated:</strong> {html.escape(report.generated_at)}<br>
<strong>Rule pack:</strong> {html.escape(report.rule_pack_version)}<br><strong>Manifest hash:</strong> <code>{html.escape(report.manifest_hash)}</code></p>
<div class="summary">{counts}</div><table><thead><tr><th>Rule</th><th>Claim</th><th>Status</th><th>Evidence and limitations</th><th>Recommendation</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Scanner limitations</h2><ul>{limitations}</ul><h2>Notes</h2><ul>{''.join(f'<li>{html.escape(note)}</li>' for note in report.notes)}</ul></body></html>"""


def write_html(report: ScanReport, stream: TextIO) -> None:
    stream.write(render_html(report))
    stream.write("\n")

def render_markdown(report: ScanReport) -> str:
    """Render a portable review document without hiding uncertainty."""
    lines = [
        "# BioRobust evidence report",
        "",
        f"- **Target:** `{report.target}`",
        f"- **Profile:** `{report.profile}`",
        f"- **Decision:** `{report.decision}`",
        f"- **Generated:** `{report.generated_at}`",
        f"- **Rule pack:** `{report.rule_pack_version}`",
        f"- **Manifest hash:** `{report.manifest_hash}`",
        "",
        "## Summary",
        "",
        " | ".join(f"**{status}**: {count}" for status, count in report.counts.items()),
        "",
        "## Findings",
        "",
        "| Rule | Status | Claim | Evidence | Recommendation |",
        "|---|---|---|---|---|",
    ]
    for finding in report.findings:
        evidence = "<br>".join(
            f"`{item.path or '(absence)'}`: {item.observation}"
            for item in finding.evidence[:5]
        )
        lines.append(
            f"| `{finding.rule_id}` | **{finding.status}** | {finding.claim} | {evidence} | {finding.recommendation or '—'} |"
        )
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report.scanner_limitations)
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in report.notes)
    return "\n".join(lines) + "\n"


def write_markdown(report: ScanReport, stream: TextIO) -> None:
    stream.write(render_markdown(report))


def _pdf_escape(value: object) -> str:
    """Escape text for ReportLab and keep generated PDFs broadly portable."""
    text = str(value).replace("—", "-").replace("–", "-")
    return html.escape(text)


def write_pdf(report: ScanReport, stream: BinaryIO) -> None:
    """Write a paginated evidence report as a PDF document.

    The PDF is generated directly from the structured report rather than by
    printing HTML. This keeps evidence, limitations, and uncertainty visible
    when the report is shared outside a terminal or browser.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:  # pragma: no cover - dependency is declared in pyproject.toml
        raise RuntimeError("PDF output requires ReportLab; install with 'python -m pip install biorobust'") from exc

    pagesize = landscape(A4)
    left_margin = 14 * mm
    right_margin = 14 * mm
    top_margin = 13 * mm
    bottom_margin = 14 * mm
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BioRobustTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=colors.HexColor("#143642"),
        alignment=TA_LEFT,
        spaceAfter=5,
    )
    subtitle_style = ParagraphStyle(
        "BioRobustSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#53636d"),
        spaceAfter=2,
    )
    section_style = ParagraphStyle(
        "BioRobustSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#143642"),
        spaceBefore=8,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "BioRobustBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.2,
        leading=10.3,
        textColor=colors.HexColor("#17202a"),
        spaceAfter=2,
    )
    small_style = ParagraphStyle(
        "BioRobustSmall",
        parent=body_style,
        fontSize=7.2,
        leading=8.8,
        textColor=colors.HexColor("#53636d"),
    )
    table_header_style = ParagraphStyle(
        "BioRobustTableHeader",
        parent=body_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    def p(value: object, style: ParagraphStyle = body_style) -> Paragraph:
        return Paragraph(_pdf_escape(value), style)

    def rich(value: str, style: ParagraphStyle = body_style) -> Paragraph:
        return Paragraph(value, style)

    def evidence_text(finding) -> str:
        entries = []
        for item in finding.evidence[:5]:
            location = item.path or "(absence observation)"
            if item.start_line:
                location += f":{item.start_line}"
                if item.end_line and item.end_line != item.start_line:
                    location += f"-{item.end_line}"
            entries.append(
                f"<b>{_pdf_escape(location)}</b>: {_pdf_escape(item.observation)} "
                f"<font color='#53636d'>({_pdf_escape(item.evidence_type)}, confidence {item.detector_confidence:.2f})</font>"
            )
        return "<br/>".join(entries)

    def limitations_text(finding) -> str:
        if not finding.limitations:
            return "None recorded."
        return "<br/>".join(f"- {_pdf_escape(value)}" for value in finding.limitations)

    def footer(canvas, document) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#dce2e7"))
        canvas.line(document.leftMargin, 9 * mm, pagesize[0] - document.rightMargin, 9 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#53636d"))
        canvas.drawString(document.leftMargin, 5.5 * mm, "BioRobust - static, evidence-first repository review")
        canvas.drawRightString(pagesize[0] - document.rightMargin, 5.5 * mm, f"Page {document.page}")
        canvas.restoreState()

    document = SimpleDocTemplate(
        stream,
        pagesize=pagesize,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
        title="BioRobust evidence report",
        author="BioRobust",
    )
    story = [
        Paragraph("BioRobust evidence report", title_style),
        rich(
            f"<b>Target:</b> {_pdf_escape(report.target)} &nbsp;&nbsp; "
            f"<b>Profile:</b> {_pdf_escape(report.profile)} &nbsp;&nbsp; "
            f"<b>Decision:</b> {_pdf_escape(report.decision)}",
            subtitle_style,
        ),
        rich(
            f"<b>Generated:</b> {_pdf_escape(report.generated_at)} &nbsp;&nbsp; "
            f"<b>Rule pack:</b> {_pdf_escape(report.rule_pack_version)} &nbsp;&nbsp; "
            f"<b>Manifest hash:</b> {_pdf_escape(report.manifest_hash)}",
            subtitle_style,
        ),
        Spacer(1, 5),
        Paragraph("Summary", section_style),
    ]

    summary_cells = []
    status_colors = {
        "pass": "#d1e7dd",
        "fail": "#f8d7da",
        "unknown": "#fff3cd",
        "manual_review": "#fff3cd",
        "not_applicable": "#e2e3e5",
    }
    for status, count in report.counts.items():
        summary_cells.append(
            rich(
                f"<b>{_pdf_escape(status)}</b><br/><font size='14'>{count}</font>",
                body_style,
            )
        )
    summary_table = Table([summary_cells], colWidths=[53.8 * mm] * len(summary_cells))
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (index, 0), (index, 0), colors.HexColor(status_colors[status]))
                for index, status in enumerate(report.counts)
            ]
            + [
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce2e7")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce2e7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([summary_table, Paragraph("Findings", section_style)])

    finding_rows = [[
        p("Rule", table_header_style),
        p("Claim and message", table_header_style),
        p("Status", table_header_style),
        p("Evidence and limitations", table_header_style),
        p("Recommendation", table_header_style),
    ]]
    for finding in report.findings:
        claim_message = (
            f"<b>{_pdf_escape(finding.title)}</b><br/>"
            f"{_pdf_escape(finding.claim)}<br/><br/>"
            f"{_pdf_escape(finding.message)}<br/>"
            f"<font color='#53636d'>Severity: {_pdf_escape(finding.severity)}; confidence: {finding.confidence:.2f}</font>"
        )
        evidence = (
            f"{evidence_text(finding)}<br/><br/>"
            f"<b>Limitations</b><br/>{limitations_text(finding)}"
        )
        finding_rows.append([
            p(finding.rule_id),
            rich(claim_message),
            rich(
                f"<b>{_pdf_escape(finding.status)}</b>",
                body_style,
            ),
            rich(evidence),
            p(finding.recommendation or "-"),
        ])

    findings_table = Table(
        finding_rows,
        colWidths=[24 * mm, 58 * mm, 27 * mm, 105 * mm, 55 * mm],
        repeatRows=1,
        splitByRow=1,
    )
    finding_style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#275d6b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5db")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for row_index, finding in enumerate(report.findings, start=1):
        finding_style_commands.append(
            ("BACKGROUND", (2, row_index), (2, row_index), colors.HexColor(status_colors[finding.status]))
        )
        if row_index % 2:
            finding_style_commands.append(("BACKGROUND", (0, row_index), (1, row_index), colors.HexColor("#f7f9fa")))
            finding_style_commands.append(("BACKGROUND", (3, row_index), (4, row_index), colors.HexColor("#f7f9fa")))
    findings_table.setStyle(TableStyle(finding_style_commands))
    story.append(findings_table)

    story.append(Paragraph("Scanner limitations", section_style))
    story.extend(rich(f"- {_pdf_escape(value)}", body_style) for value in report.scanner_limitations)
    story.append(Paragraph("Notes", section_style))
    story.extend(rich(f"- {_pdf_escape(value)}", body_style) for value in report.notes)
    document.build(story, onFirstPage=footer, onLaterPages=footer)
