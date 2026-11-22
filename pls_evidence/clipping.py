"""Parse locally saved web clippings (Obsidian Web Clipper style).

A clipping is a Markdown file with a YAML-like frontmatter (``title``,
``source``, ``author``, ``published``), the post text, and an optional
``## Comments`` section whose comments start with a header line such as
``> **name** · [2026-04-06](url) · 4 points``.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.S)
_COMMENTS_SPLIT = re.compile(r"^## Comments\s*$", re.M)
_COMMENT_HEAD = re.compile(
    r"^(?:>\s*)+\*\*(?P<author>.+?)\*\*\s*·\s*\[(?P<date>\d{4}-\d{2}-\d{2})\]\([^)]*\)"
)
_BLOCKQUOTE_PREFIX = re.compile(r"^(?:>\s?)+")
_LINE_BLOCKQUOTE = re.compile(r"^[ \t]*(?:>[ \t]?)+", re.M)
_MD_LINK = re.compile(r"\[([^\]]*)\]\(((?:[^()\s]|\([^()]*\))*)\)")
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")
_NAME_PREFIX = re.compile(r"^(?:/?u/|@)")
_QUOTE_TABLE = str.maketrans(
    {
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        " ": " ",
    }
)


def normalize(text: str) -> str:
    """Normalize text for excerpt matching.

    Documented rules (applied identically to the excerpt and the clipping):

    1. curly quotes and non-breaking spaces become straight quotes and spaces;
    2. Markdown blockquote markers (``>``) at the start of a line are removed;
    3. Markdown links ``[text](url)`` become ``text`` (a URL may contain one
       level of parentheses);
    4. Markdown backslash escapes (``\\_``, ``\\$``) are removed;
    5. ``**`` and ``__`` emphasis markers are removed;
    6. runs of whitespace collapse to one space; leading/trailing space is cut.

    Case, punctuation and word order are never altered.
    """
    text = text.translate(_QUOTE_TABLE)
    text = _LINE_BLOCKQUOTE.sub("", text)
    text = _MD_LINK.sub(r"\1", text)
    text = re.sub(r"\\(.)", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", text).strip()


def normalize_name(name: str) -> str:
    """Normalize an author handle for comparison.

    Escapes are removed, a leading ``u/``, ``/u/`` or ``@`` is dropped, the
    case is folded.
    """
    name = re.sub(r"\\(.)", r"\1", name).strip()
    return _NAME_PREFIX.sub("", name).casefold()


def normalize_url(url: str) -> str:
    """Normalize a URL for comparison: trim spaces and a trailing slash."""
    return url.strip().rstrip("/")


def date_part(value: str) -> str:
    """Return the ISO date prefix of a timestamp, or the trimmed value."""
    value = value.strip()
    match = _ISO_DATE.match(value)
    return match.group(0) if match else value


@dataclass
class Comment:
    author: str
    date: str
    text: str


@dataclass
class Clipping:
    path: Path
    content_hash: str
    title: str
    source: str
    author: str
    published: str
    post_text: str
    comments: list[Comment] = field(default_factory=list)


@dataclass
class SkippedClipping:
    path: Path
    reason: str


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', frontmatter, re.M)
    return match.group(1).replace('\\"', '"') if match else ""


def _frontmatter_author(frontmatter: str) -> str:
    """Read the author from ``[[wikilink]]``, a plain or quoted list item, or an inline value."""
    block = re.search(r"^author:[ \t]*(.*)$", frontmatter, re.M)
    if not block:
        return ""
    inline = block.group(1).strip()
    if inline:
        value = inline
    else:
        item = re.search(r"^author:[ \t]*\n[ \t]*-[ \t]*(.+)$", frontmatter, re.M)
        value = item.group(1).strip() if item else ""
    wikilink = re.search(r"\[\[(.+?)\]\]", value)
    if wikilink:
        return wikilink.group(1)
    return value.strip().strip('"').strip("'").strip()


def _parse_comments(section: str) -> list[Comment]:
    comments: list[Comment] = []
    current: Comment | None = None
    lines: list[str] = []

    def flush() -> None:
        if current is not None:
            current.text = "\n".join(lines).strip()
            comments.append(current)

    for raw in section.splitlines():
        head = _COMMENT_HEAD.match(raw.strip())
        if head:
            flush()
            current = Comment(author=head.group("author"), date=head.group("date"), text="")
            lines = []
        elif current is not None:
            lines.append(_BLOCKQUOTE_PREFIX.sub("", raw.strip()))
    flush()
    return comments


def _clean(text: str) -> str:
    """Strip a BOM and unify line endings (CRLF and lone CR become LF)."""
    return text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")


def parse_clipping_text(text: str, path: Path, content_hash: str) -> tuple[Clipping | None, str]:
    """Parse clipping text; return ``(clipping, "")`` or ``(None, reason)``."""
    match = _FRONTMATTER.match(_clean(text))
    if not match:
        return None, "no frontmatter"
    frontmatter, body = match.group(1), match.group(2)
    source = _frontmatter_value(frontmatter, "source")
    if not source:
        return None, "no source in frontmatter"
    parts = _COMMENTS_SPLIT.split(body, maxsplit=1)
    post = parts[0].strip()
    post = re.sub(r"\n-{3,}\s*\Z", "", post).strip()
    comments = _parse_comments(parts[1]) if len(parts) > 1 else []
    return (
        Clipping(
            path=path,
            content_hash=content_hash,
            title=_frontmatter_value(frontmatter, "title"),
            source=source,
            author=_frontmatter_author(frontmatter),
            published=_frontmatter_value(frontmatter, "published"),
            post_text=post,
            comments=comments,
        ),
        "",
    )


def load_clipping(path: Path) -> Clipping | None:
    """Read one clipping file; the hash is sha256 of the raw file bytes."""
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    clipping, _ = parse_clipping_text(data.decode("utf-8", errors="replace"), path, digest)
    return clipping


def scan_clippings(directory: Path) -> tuple[list[Clipping], list[SkippedClipping]]:
    """Load every ``*.md`` under ``directory`` (recursive, sorted).

    Files that cannot be used are returned with a reason instead of being
    dropped silently.
    """
    clippings: list[Clipping] = []
    skipped: list[SkippedClipping] = []
    for path in sorted(directory.rglob("*.md")):
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            skipped.append(SkippedClipping(path, f"unreadable: {exc.strerror or exc}"))
            continue
        digest = hashlib.sha256(data).hexdigest()
        clipping, reason = parse_clipping_text(data.decode("utf-8", errors="replace"), path, digest)
        if clipping is None:
            skipped.append(SkippedClipping(path, reason))
        else:
            clippings.append(clipping)
    return clippings, skipped


def load_clippings(directory: Path) -> list[Clipping]:
    """Load usable clippings only; use :func:`scan_clippings` to see skipped files."""
    return scan_clippings(directory)[0]
