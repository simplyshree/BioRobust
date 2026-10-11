"""Command-line interface for BioRobust."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .reporting import write_html, write_json, write_markdown
from .rules import RULE_BY_ID, RULE_PACK_VERSION, RULES
from .scanner import PROFILES, scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="biorobust", description="Evidence-based robustness profiling for genomic repositories.")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a local repository without executing its code")
    scan_parser.add_argument("path", nargs="?", default=".", help="Repository directory")
    scan_parser.add_argument("--profile", choices=["auto", *sorted(PROFILES)], default="genomics", help="Check profile")
    scan_parser.add_argument("--format", choices=("json", "html", "markdown"), default="json", help="Report format")
    scan_parser.add_argument("--output", type=Path, help="Write the report to a file instead of stdout")

    subparsers.add_parser("rules", help="List the versioned rule pack")
    subparsers.add_parser("profiles", help="List available domain profiles")
    explain_parser = subparsers.add_parser("explain", help="Explain one rule")
    explain_parser.add_argument("rule_id", help="Rule ID, for example DNA-REF-001")
    ask_parser = subparsers.add_parser("ask", help="Answer a question from a local evidence report")
    ask_parser.add_argument("path", help="Repository directory that has already been cloned or downloaded")
    ask_parser.add_argument("question", nargs="+", help="Question to answer from detected evidence")
    ask_parser.add_argument("--profile", choices=["auto", *sorted(PROFILES)], default="auto", help="Check profile")
    return parser


def _print_rules() -> None:
    print(f"BioRobust rule pack {RULE_PACK_VERSION}")
    for rule in RULES:
        print(f"{rule.rule_id:13} [{rule.profile:8}] {rule.title}: {rule.claim}")


def _print_profiles() -> None:
    for name, definition in sorted(PROFILES.items()):
        print(f"{name:18} {definition.description}")


def _print_explanation(rule_id: str) -> int:
    rule = RULE_BY_ID.get(rule_id.upper())
    if rule is None:
        print(f"biorobust: unknown rule {rule_id!r}", file=sys.stderr)
        return 2
    print(f"{rule.rule_id}: {rule.title}")
    print(f"Profile: {rule.profile}")
    print(f"Claim: {rule.claim}")
    print(f"What it checks: {rule.description}")
    print("Limitations:")
    for limitation in rule.limitations:
        print(f"- {limitation}")
    return 0


def _answer_question(path: str, question: str, profile: str) -> int:
    report = scan(path, profile)
    lowered = question.lower()
    keyword_groups = {
        "reproducibility": {"REPRO-001", "DNA-PORT-001", "CI-001"},
        "portable": {"DNA-PORT-001", "REPRO-001"},
        "test": {"TEST-001", "DNA-VAL-001", "SBOL-004"},
        "valid": {"DNA-VAL-001", "SBOL-002", "SBOL-004"},
        "reference": {"DNA-REF-001"},
        "sbol": {"SBOL-001", "SBOL-002", "SBOL-003", "SBOL-004", "SBOL-005"},
        "license": {"META-001"},
        "document": {"DOC-001", "META-002"},
        "security": {"SEC-001"},
        "secret": {"SEC-001"},
    }
    selected_ids: set[str] = set()
    for keyword, rule_ids in keyword_groups.items():
        if keyword in lowered:
            selected_ids.update(rule_ids)
    findings = [finding for finding in report.findings if not selected_ids or finding.rule_id in selected_ids]
    print(f"BioRobust answer for: {question}")
    print(f"Profile: {report.profile}; decision: {report.decision}")
    for finding in findings:
        print(f"- {finding.rule_id} [{finding.status}] {finding.message}")
        for evidence in finding.evidence[:3]:
            location = evidence.path or "(absence)"
            print(f"  evidence: {location} — {evidence.observation}")
    print("This is a static, evidence-grounded answer; it does not execute the repository or prove biological correctness.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "rules":
        _print_rules()
        return 0
    if args.command == "profiles":
        _print_profiles()
        return 0
    if args.command == "explain":
        return _print_explanation(args.rule_id)
    if args.command == "ask":
        try:
            return _answer_question(args.path, " ".join(args.question), args.profile)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"biorobust: {exc}", file=sys.stderr)
            return 2
    if args.command != "scan":
        return 2
    try:
        report = scan(args.path, args.profile)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8") as stream:
                writer = {"json": write_json, "html": write_html, "markdown": write_markdown}[args.format]
                writer(report, stream)
        elif args.format == "json":
            write_json(report, sys.stdout)
        elif args.format == "html":
            write_html(report, sys.stdout)
        else:
            write_markdown(report, sys.stdout)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"biorobust: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


