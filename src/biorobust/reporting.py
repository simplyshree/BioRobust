"""JSON and compact HTML report rendering."""

from __future__ import annotations

import html
import json
from typing import TextIO

from .models import ScanReport


def write_json(report: ScanReport, stream: TextIO) -> None:
    json.dump(report.as_dict(), stream, indent=2)
    stream.write("\n")


def render_html(report: ScanReport) -> str:
    rows = []
    for finding in report.findings:
        evidence = ", ".join(finding.evidence) or "—"
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(finding.rule_id)}</code></td>"
            f"<td>{html.escape(finding.title)}</td>"
            f"<td><span class=\"status {html.escape(finding.status)}\">{html.escape(finding.status)}</span></td>"
            f"<td>{html.escape(finding.message)}<br><small>Evidence: {html.escape(evidence)}</small></td>"
            f"<td>{html.escape(finding.recommendation or '—')}</td>"
            "</tr>"
        )
    counts = " ".join(f"<span>{status}: <strong>{count}</strong></span>" for status, count in report.counts.items())
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BioRobust report</title><style>
body{{font-family:system-ui,sans-serif;max-width:1250px;margin:2rem auto;padding:0 1rem;color:#17202a;background:#fbfcfd}}
h1{{margin-bottom:.2rem}} .meta{{color:#58636f}} .summary{{display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0}}
.summary span{{padding:.45rem .7rem;background:#eef2f5;border-radius:.4rem}} table{{border-collapse:collapse;width:100%;background:white}}
th,td{{border:1px solid #dce2e7;padding:.7rem;text-align:left;vertical-align:top}} th{{background:#eef2f5}}
.status{{font-weight:700;padding:.2rem .45rem;border-radius:.3rem}} .pass{{color:#146c43;background:#d1e7dd}} .fail{{color:#842029;background:#f8d7da}}
.unknown,.manual_review{{color:#664d03;background:#fff3cd}} .not_applicable{{color:#41464b;background:#e2e3e5}}
small{{color:#58636f}} code{{font-size:.9em}}
</style></head><body><h1>BioRobust robustness report</h1>
<p class="meta"><strong>Target:</strong> {html.escape(report.target)}<br><strong>Profile:</strong> {html.escape(report.profile)}<br>
<strong>Decision:</strong> {html.escape(report.decision)}<br><strong>Generated:</strong> {html.escape(report.generated_at)}</p>
<div class="summary">{counts}</div><table><thead><tr><th>Rule</th><th>Check</th><th>Status</th><th>Evidence</th><th>Recommendation</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Notes</h2><ul>{''.join(f'<li>{html.escape(note)}</li>' for note in report.notes)}</ul></body></html>"""


def write_html(report: ScanReport, stream: TextIO) -> None:
    stream.write(render_html(report))
    stream.write("\n")

