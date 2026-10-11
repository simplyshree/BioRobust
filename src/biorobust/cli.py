"""Command-line interface for BioRobust."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .reporting import write_html, write_json
from .scanner import PROFILES, scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="biorobust", description="Evidence-based robustness profiling for genomic repositories.")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan_parser = subparsers.add_parser("scan", help="Scan a local repository without executing its code")
    scan_parser.add_argument("path", nargs="?", default=".", help="Repository directory")
    scan_parser.add_argument("--profile", choices=sorted(PROFILES), default="genomics", help="Check profile")
    scan_parser.add_argument("--format", choices=("json", "html"), default="json", help="Report format")
    scan_parser.add_argument("--output", type=Path, help="Write the report to a file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command != "scan":
        return 2
    try:
        report = scan(args.path, args.profile)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8") as stream:
                (write_json if args.format == "json" else write_html)(report, stream)
        elif args.format == "json":
            write_json(report, sys.stdout)
        else:
            write_html(report, sys.stdout)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"biorobust: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

