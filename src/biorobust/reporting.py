"""JSON and human-readable HTML report rendering."""

from __future__ import annotations

import html
import json
from typing import TextIO

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


