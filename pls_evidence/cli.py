"""Command line entry: ``python -m pls_evidence {verify,report} ...``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pls_evidence.clipping import scan_clippings
from pls_evidence.report import build_report, render_csv, render_markdown
from pls_evidence.table import parse_evidence_table
from pls_evidence.verify import FAIL, summarize, verify_rows, write_log


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pls_evidence",
        description="Offline, read-only evidence tools for local clippings.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="check evidence rows against local clippings")
    verify.add_argument("--evidence", type=Path, required=True, help="Markdown evidence table")
    verify.add_argument("--clippings", type=Path, required=True, help="directory with clippings")
    verify.add_argument("--log", type=Path, required=True, help="JSON log to write")
    verify.add_argument("--overwrite", action="store_true", help="replace an existing log")
    verify.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 also when a row has no clipping (NO_SNAPSHOT)",
    )

    report = sub.add_parser("report", help="list clippings with heuristic flags")
    report.add_argument("--clippings", type=Path, required=True, help="directory with clippings")
    report.add_argument("--format", choices=["md", "csv"], default="md")
    report.add_argument("--out", type=Path, help="write to a file instead of stdout")
    report.add_argument("--overwrite", action="store_true", help="replace an existing output file")
    return parser


def _run_verify(args: argparse.Namespace) -> int:
    if not args.evidence.is_file():
        print(f"error: evidence file not found: {args.evidence}", file=sys.stderr)
        return 2
    if not args.clippings.is_dir():
        print(f"error: clippings directory not found: {args.clippings}", file=sys.stderr)
        return 2
    rows = parse_evidence_table(args.evidence.read_text(encoding="utf-8"))
    if not rows:
        print("error: no evidence rows (E-NNN) found", file=sys.stderr)
        return 2
    clippings, skipped = scan_clippings(args.clippings)
    results = verify_rows(rows, clippings)
    try:
        write_log(
            args.log,
            evidence_path=args.evidence,
            clippings_dir=args.clippings,
            results=results,
            skipped=skipped,
            overwrite=args.overwrite,
        )
    except (ValueError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    counts = summarize(results)
    print(
        f"PASS={counts['PASS']} FAIL={counts['FAIL']} NO_SNAPSHOT={counts['NO_SNAPSHOT']} "
        f"SKIPPED_CLIPPINGS={len(skipped)} log={args.log}"
    )
    for item in skipped:
        print(f"SKIPPED {item.path.name}: {item.reason}")
    for result in results:
        if result.status == FAIL:
            print(f"FAIL {result.id}: {result.note or result.fields}")
        for warning in result.warnings:
            print(f"WARN {result.id}: {warning}")
    if counts["FAIL"]:
        return 1
    if args.strict and counts["NO_SNAPSHOT"]:
        return 1
    return 0


def _run_report(args: argparse.Namespace) -> int:
    if not args.clippings.is_dir():
        print(f"error: clippings directory not found: {args.clippings}", file=sys.stderr)
        return 2
    clippings, skipped = scan_clippings(args.clippings)
    rows = build_report(clippings, skipped)
    text = render_csv(rows) if args.format == "csv" else render_markdown(rows)
    if args.out is None:
        sys.stdout.write(text)
        return 0
    out_resolved = args.out.resolve()
    if args.clippings.resolve() in out_resolved.parents:
        print("error: output must not be inside the clippings directory", file=sys.stderr)
        return 2
    if args.out.exists() and not args.overwrite:
        print(f"error: {args.out} already exists (use --overwrite)", file=sys.stderr)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "verify":
        return _run_verify(args)
    return _run_report(args)


if __name__ == "__main__":
    raise SystemExit(main())
