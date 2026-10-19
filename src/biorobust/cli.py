"""Command-line interface for BioRobust."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from . import __version__
from .reporting import write_html, write_json, write_markdown, write_pdf
from .rules import RULE_BY_ID, RULE_PACK_VERSION, RULES
from .scanner import PROFILES, scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="biorobust", description="Evidence-first repository analysis for open-source biological and scientific software.")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a local repository without executing its code")
    scan_parser.add_argument("path", nargs="?", default=".", help="Repository directory")
    scan_parser.add_argument("--profile", choices=["auto", *sorted(PROFILES)], default="auto", help="Check profile")
    scan_parser.add_argument("--format", choices=("json", "html", "markdown", "pdf"), default="json", help="Report format")
    scan_parser.add_argument("--output", type=Path, help="Write the report to a file instead of stdout")

    start_parser = subparsers.add_parser("start", help="Create a first-pass report from a local repository or Git URL")
    start_parser.add_argument("path", nargs="?", default=".", help="Repository directory or Git URL")
    start_parser.add_argument("--profile", choices=["auto", *sorted(PROFILES)], default="auto", help="Check profile")
    start_parser.add_argument("--format", choices=("json", "html", "markdown", "pdf"), default="markdown", help="Report format")
    start_parser.add_argument("--output", type=Path, help="Write the report to a file instead of stdout")

    subparsers.add_parser("rules", help="List the versioned rule pack")
    subparsers.add_parser("profiles", help="List available domain profiles")
    explain_parser = subparsers.add_parser("explain", help="Explain one rule")
    explain_parser.add_argument("rule_id", help="Rule ID, for example DNA-REF-001")
    ask_parser = subparsers.add_parser("ask", help="Answer a question from a local evidence report")
    ask_parser.add_argument("path", help="Repository directory that has already been cloned or downloaded")
    ask_parser.add_argument("question", nargs="+", help="Question to answer from detected evidence")
    ask_parser.add_argument("--profile", choices=["auto", *sorted(PROFILES)], default="auto", help="Check profile")
    return parser


def _start_target(source: str) -> str:
    """Return a local path, cloning an HTTP(S) Git URL when necessary."""
    parsed = urlparse(source)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return source

    name = Path(parsed.path.rstrip("/")).name
    if name.endswith(".git"):
        name = name[:-4]
    if not name or name in {".", ".."}:
        raise ValueError("Could not determine a repository name from the Git URL")

    destination = Path.cwd() / ".biorobust" / "repos" / name
    if destination.exists():
        if not destination.is_dir():
            raise ValueError(f"Repository destination is not a directory: {destination}")
        return str(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Cloning {source} to {destination}", file=sys.stderr)
    try:
        subprocess.run(["git", "clone", "--depth", "1", source, str(destination)], check=True)
    except FileNotFoundError as exc:
        raise ValueError("Git is required when starting from a URL") from exc
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"Could not clone repository (git exited with {exc.returncode})") from exc
    return str(destination)


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
        "test": {"TEST-001", "DNA-VAL-001"},
        "valid": {"DNA-VAL-001"},
        "reference": {"DNA-REF-001"},
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


def _write_report(report, report_format: str, output: Path | None) -> None:
    if report_format == "pdf":
        if output:
            with output.open("wb") as stream:
                write_pdf(report, stream)
        else:
            write_pdf(report, sys.stdout.buffer)
        return

    writer = {"json": write_json, "html": write_html, "markdown": write_markdown}[report_format]
    if output:
        with output.open("w", encoding="utf-8") as stream:
            writer(report, stream)
    else:
        writer(report, sys.stdout)


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
    if args.command not in {"scan", "start"}:
        return 2
    try:
        target = _start_target(args.path) if args.command == "start" else args.path
        report = scan(target, args.profile)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
        _write_report(report, args.format, args.output)
        return 0
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"biorobust: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


