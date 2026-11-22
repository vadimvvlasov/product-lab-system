"""Deterministic intake report for local clippings.

Flags are simple text heuristics to help a human triage a folder of clippings.
They are not verdicts: a flagged post may still hold a genuine L2 case, and an
unflagged one may be promotion.
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass

from pls_evidence.clipping import Clipping

_BUILDER = re.compile(
    r"\b(?:I|we)(?:'ve| have)?\s+(?:built|made|created|launched)\b"
    r"|\bShowoff\b|\bI'm building\b|\bwe(?:'re| are) building\b",
    re.I,
)
_HIRING = re.compile(r"\[\s*hiring\s*\]|\bwe are looking for\b|\bhiring\b", re.I)
_URL = re.compile(r"https?://[^\s)\]>]+")
_REDDIT_HOST = re.compile(r"https?://(?:[\w.-]+\.)?(?:reddit\.com|redd\.it)\b", re.I)
_SUBREDDIT = re.compile(r"reddit\.com/r/([^/]+)/", re.I)

COLUMNS = ["file", "source_name", "published", "author", "title", "comments", "flags"]


@dataclass
class ReportRow:
    file: str
    source_name: str
    published: str
    author: str
    title: str
    comments: int
    flags: list[str]


def _flags(clipping: Clipping) -> list[str]:
    text = f"{clipping.title}\n{clipping.post_text}"
    flags: list[str] = []
    if _BUILDER.search(text):
        flags.append("builder_post")
    if _HIRING.search(text):
        flags.append("hiring")
    external = [u for u in _URL.findall(clipping.post_text) if not _REDDIT_HOST.match(u)]
    if external:
        flags.append(f"external_link:{len(external)}")
    return flags


def _source_name(clipping: Clipping) -> str:
    match = _SUBREDDIT.search(clipping.source)
    if match:
        return f"r/{match.group(1)}"
    host = re.match(r"https?://([^/]+)", clipping.source)
    return host.group(1) if host else ""


def build_report(clippings: list[Clipping]) -> list[ReportRow]:
    return [
        ReportRow(
            file=c.path.name,
            source_name=_source_name(c),
            published=c.published,
            author=c.author,
            title=c.title,
            comments=len(c.comments),
            flags=_flags(c),
        )
        for c in clippings
    ]


def render_markdown(rows: list[ReportRow]) -> str:
    lines = ["| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for row in rows:
        cells = [
            row.file,
            row.source_name,
            row.published,
            row.author,
            row.title,
            str(row.comments),
            ", ".join(row.flags),
        ]
        lines.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
    return "\n".join(lines) + "\n"


def render_csv(rows: list[ReportRow]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(COLUMNS)
    for row in rows:
        writer.writerow(
            [row.file, row.source_name, row.published, row.author, row.title, row.comments, ";".join(row.flags)]
        )
    return buffer.getvalue()
