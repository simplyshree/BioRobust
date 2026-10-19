"""JSON, document, and human-readable report rendering."""

from __future__ import annotations

import html
import json
from typing import BinaryIO, TextIO

from .models import ScanReport
from .pdf_layout import write_pdf_document
from .pdf_styles import palette_for, status_label
from .report_options import RenderOptions


def write_json(report: ScanReport, stream: TextIO) -> None:
    """Write the complete structured report without presentation filtering."""
    json.dump(report.as_dict(), stream, indent=2, sort_keys=True)
    stream.write("\n")


def _evidence_html(finding, evidence_limit: int | None) -> str:
    evidence = finding.evidence if evidence_limit is None else finding.evidence[:evidence_limit]
    if not evidence:
        return "<p><em>No evidence observations selected for this detail level.</em></p>"
    rows = []
    for item in evidence:
        location = html.escape(item.path or "(no path: absence observation)")
        if item.start_line:
            location += f":{item.start_line}" + (f"-{item.end_line}" if item.end_line and item.end_line != item.start_line else "")
        rows.append(
            f"<li><code>{location}</code> &mdash; {html.escape(item.observation)} "
            f"<small>({html.escape(item.evidence_type)}, confidence {item.detector_confidence:.2f})</small></li>"
        )
    return "<ul>" + "".join(rows) + "</ul>"


def render_html(report: ScanReport, options: RenderOptions | None = None) -> str:
    """Render a semantic, self-contained HTML report."""
    options = options or RenderOptions()
    palette = palette_for(options.theme)
    rows = []
    for finding in report.findings:
        limitations = " ".join(html.escape(value) for value in finding.limitations) or "None recorded."
        status = status_label(finding.status)
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(finding.rule_id)}</code></td>"
            f"<td><strong>{html.escape(finding.title)}</strong><br><small>{html.escape(finding.claim)}</small></td>"
            f"<td><span class=\"status {html.escape(finding.status)}\">{html.escape(status)}</span><br>"
            f"<small>{html.escape(finding.severity)}, confidence {finding.confidence:.2f}</small></td>"
            f"<td><p>{html.escape(finding.message)}</p>{_evidence_html(finding, options.evidence_limit)}"
            f"<small><strong>Limitation:</strong> {limitations}</small></td>"
            f"<td>{html.escape(finding.recommendation or '—')}</td>"
            "</tr>"
        )
    counts = " ".join(
        f"<span>{html.escape(status_label(status))}: <strong>{count}</strong></span>"
        for status, count in report.counts.items()
    )
    limitations = "".join(f"<li>{html.escape(value)}</li>" for value in report.scanner_limitations)
    notes = "".join(f"<li>{html.escape(note)}</li>" for note in report.notes)
    status_css = "".join(
        f".status.{status}{{color:{palette.status_foreground(status)};background:{palette.status_background(status)}}}"
        for status in report.counts
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BioRobust report</title><style>
body{{font-family:system-ui,sans-serif;max-width:1400px;margin:2rem auto;padding:0 1rem;color:{palette.body};background:{palette.page_background}}}
h1,h2{{color:{palette.heading}}} h1{{margin-bottom:.2rem}} .meta{{color:{palette.muted}}}
.summary{{display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0}} .summary span{{padding:.45rem .7rem;background:{palette.panel};border:1px solid {palette.border};border-radius:.4rem}}
table{{border-collapse:collapse;width:100%;background:{palette.page_background}}} th,td{{border:1px solid {palette.border};padding:.7rem;text-align:left;vertical-align:top}} th{{background:{palette.panel};color:{palette.heading}}}
.status{{font-weight:700;padding:.2rem .45rem;border:1px solid {palette.border};border-radius:.3rem}} {status_css}
small{{color:{palette.muted}}} code{{font-size:.9em}} ul{{padding-left:1.2rem;margin:.4rem 0}}
</style></head><body><h1>BioRobust evidence report</h1>
<p class="meta"><strong>Target:</strong> {html.escape(report.target)}<br><strong>Profile:</strong> {html.escape(report.profile)}<br>
<strong>Decision:</strong> {html.escape(report.decision)}<br><strong>Generated:</strong> {html.escape(report.generated_at)}<br>
<strong>Rule pack:</strong> {html.escape(report.rule_pack_version)}<br><strong>Manifest hash:</strong> <code>{html.escape(report.manifest_hash)}</code><br>
<strong>Presentation:</strong> {html.escape(options.theme)}, {html.escape(options.detail)}</p>
<div class="summary">{counts}</div><table><caption>Evidence findings by rule</caption><thead><tr><th scope="col">Rule</th><th scope="col">Claim</th><th scope="col">Status</th><th scope="col">Evidence and limitations</th><th scope="col">Recommendation</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Scanner limitations</h2><ul>{limitations}</ul><h2>Notes</h2><ul>{notes}</ul></body></html>"""


def write_html(report: ScanReport, stream: TextIO, options: RenderOptions | None = None) -> None:
    stream.write(render_html(report, options))
    stream.write("\n")


def render_markdown(report: ScanReport, options: RenderOptions | None = None) -> str:
    """Render a portable review document without hiding uncertainty."""
    options = options or RenderOptions()
    evidence_limit = options.evidence_limit
    lines = [
        "# BioRobust evidence report",
        "",
        f"- **Target:** `{report.target}`",
        f"- **Profile:** `{report.profile}`",
        f"- **Decision:** `{report.decision}`",
        f"- **Generated:** `{report.generated_at}`",
        f"- **Rule pack:** `{report.rule_pack_version}`",
        f"- **Manifest hash:** `{report.manifest_hash}`",
        f"- **Presentation:** `{options.theme}`, `{options.detail}`",
        "",
        "## Summary",
        "",
        " | ".join(f"**{status_label(status)}**: {count}" for status, count in report.counts.items()),
        "",
        "## Findings",
        "",
        "| Rule | Status | Claim | Evidence | Recommendation |",
        "|---|---|---|---|---|",
    ]
    for finding in report.findings:
        evidence_items = finding.evidence if evidence_limit is None else finding.evidence[:evidence_limit]
        evidence = "<br>".join(
            f"`{item.path or '(absence)'}`: {item.observation}" for item in evidence_items
        ) or "(no evidence selected)"
        lines.append(
            f"| `{finding.rule_id}` | **{status_label(finding.status)}** | {finding.claim} | {evidence} | {finding.recommendation or '—'} |"
        )
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in report.scanner_limitations)
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in report.notes)
    return "\n".join(lines) + "\n"


def write_markdown(report: ScanReport, stream: TextIO, options: RenderOptions | None = None) -> None:
    stream.write(render_markdown(report, options))


def write_pdf(report: ScanReport, stream: BinaryIO, options: RenderOptions | None = None) -> None:
    """Write a readable, paginated PDF while keeping the historical API stable."""
    write_pdf_document(report, stream, options or RenderOptions())
