"""Verify evidence rows against local clippings.

The check is purely textual: a row passes when its ``verbatim_excerpt`` is
present in the clipping and the stated URL, date and author match the
clipping. It says nothing about whether the claim is true or whether the
clipping itself is genuine; both stay with the human reviewer.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from pls_evidence.clipping import (
    Clipping,
    normalize,
    normalize_name,
    normalize_url,
)

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"
NO_SNAPSHOT = "NO_SNAPSHOT"

_UNKNOWN = {"", "unknown", "n/a", "-"}


@dataclass
class Location:
    kind: str  # "post" or "comment"
    author: str
    date: str


@dataclass
class RowResult:
    id: str
    status: str
    snapshot: str = ""
    content_hash: str = ""
    found_in: str = ""
    fields: dict[str, str] = field(default_factory=dict)
    note: str = ""


def _locations(clipping: Clipping, excerpt: str) -> list[Location]:
    found: list[Location] = []
    if excerpt in normalize(clipping.post_text):
        found.append(Location("post", clipping.author, clipping.published))
    for comment in clipping.comments:
        if excerpt in normalize(comment.text):
            found.append(Location("comment", comment.author, comment.date))
    return found


def _compare(row_value: str, actual: str, *, name: bool = False) -> str:
    if row_value.strip().lower() in _UNKNOWN:
        return SKIP
    if name:
        return PASS if normalize_name(row_value) == normalize_name(actual) else FAIL
    return PASS if row_value.strip() == actual.strip() else FAIL


def _check_location(row: dict[str, str], location: Location) -> dict[str, str]:
    return {
        "published_at": _compare(row.get("published_at", ""), location.date),
        "author_id": _compare(row.get("author_id", ""), location.author, name=True),
    }


def verify_row(row: dict[str, str], clippings: list[Clipping]) -> RowResult:
    """Verify a single evidence row against the loaded clippings."""
    row_id = row.get("id", "")
    excerpt = normalize(row.get("verbatim_excerpt", ""))
    url = normalize_url(row.get("source_url", ""))
    if not excerpt:
        return RowResult(row_id, FAIL, fields={"verbatim_excerpt": FAIL}, note="empty verbatim_excerpt")
    if not url:
        return RowResult(row_id, FAIL, fields={"source_url": FAIL}, note="empty source_url")

    same_url = [c for c in clippings if normalize_url(c.source) == url]
    if not same_url:
        for other in clippings:
            if _locations(other, excerpt):
                return RowResult(
                    row_id,
                    FAIL,
                    snapshot=other.path.name,
                    content_hash=other.content_hash,
                    fields={"source_url": FAIL},
                    note=f"excerpt found in a clipping with a different source: {other.source}",
                )
        return RowResult(row_id, NO_SNAPSHOT, note="no clipping with this source_url")

    best: RowResult | None = None
    for clipping in same_url:
        locations = _locations(clipping, excerpt)
        if not locations:
            continue
        for location in locations:
            fields = {"source_url": PASS, "verbatim_excerpt": PASS}
            fields.update(_check_location(row, location))
            status = FAIL if FAIL in fields.values() else PASS
            result = RowResult(
                row_id,
                status,
                snapshot=clipping.path.name,
                content_hash=clipping.content_hash,
                found_in=location.kind,
                fields=fields,
            )
            if status == PASS:
                return result
            if best is None:
                best = result
    if best is not None:
        best.note = "excerpt found, but a field does not match the clipping"
        return best
    first = same_url[0]
    return RowResult(
        row_id,
        FAIL,
        snapshot=first.path.name,
        content_hash=first.content_hash,
        fields={"source_url": PASS, "verbatim_excerpt": FAIL},
        note="excerpt not found in the clipping",
    )


def verify_rows(rows: list[dict[str, str]], clippings: list[Clipping]) -> list[RowResult]:
    return [verify_row(row, clippings) for row in rows]


def summarize(results: list[RowResult]) -> dict[str, int]:
    counts = {PASS: 0, FAIL: 0, NO_SNAPSHOT: 0}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    return counts


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_log(
    log_path: Path,
    *,
    evidence_path: Path,
    clippings_dir: Path,
    results: list[RowResult],
    overwrite: bool = False,
    clock: Callable[[], str] = _utc_now,
) -> None:
    """Write the verification log; refuse to touch inputs or existing files."""
    log_resolved = log_path.resolve()
    if log_resolved == evidence_path.resolve():
        raise ValueError("log path must not be the evidence file")
    if clippings_dir.resolve() in log_resolved.parents:
        raise ValueError("log path must not be inside the clippings directory")
    if log_path.exists() and not overwrite:
        raise FileExistsError(f"{log_path} already exists (use --overwrite)")
    payload = {
        "tool": "pls_evidence verify",
        "verified_at": clock(),
        "evidence_file": str(evidence_path),
        "clippings_dir": str(clippings_dir),
        "scope": "textual check of excerpt, URL, date and author against a local clipping; "
        "does not confirm the claim and does not replace human verification",
        "summary": summarize(results),
        "results": [
            {
                "id": r.id,
                "status": r.status,
                "snapshot": r.snapshot,
                "content_hash": r.content_hash,
                "found_in": r.found_in,
                "fields": r.fields,
                "note": r.note,
            }
            for r in results
        ],
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
