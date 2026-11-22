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
    2. Markdown links ``[text](url)`` become ``text``;
    3. Markdown backslash escapes (``\\_``, ``\\$``) are removed;
    4. ``**`` and ``__`` emphasis markers are removed;
    5. runs of whitespace collapse to one space; leading/trailing space is cut.

    Case, punctuation and word order are never altered.
    """
    text = text.translate(_QUOTE_TABLE)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\\(.)", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", text).strip()


def normalize_name(name: str) -> str:
    """Normalize an author handle for comparison (escapes removed, case folded)."""
    return re.sub(r"\\(.)", r"\1", name).strip().casefold()


def normalize_url(url: str) -> str:
    """Normalize a URL for comparison: trim spaces and a trailing slash."""
    return url.strip().rstrip("/")


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


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', frontmatter, re.M)
    return match.group(1).replace('\\"', '"') if match else ""


def _frontmatter_author(frontmatter: str) -> str:
    match = re.search(r'^author:\s*\n\s*-\s*"?\[\[(.+?)\]\]', frontmatter, re.M)
    if not match:
        match = re.search(r'^author:\s*"?\[\[(.+?)\]\]', frontmatter, re.M)
    return match.group(1) if match else ""


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


def parse_clipping_text(text: str, path: Path, content_hash: str) -> Clipping | None:
    """Parse clipping text; return ``None`` when there is no frontmatter."""
    match = _FRONTMATTER.match(text)
    if not match:
        return None
    frontmatter, body = match.group(1), match.group(2)
    parts = _COMMENTS_SPLIT.split(body, maxsplit=1)
    post = parts[0].strip()
    post = re.sub(r"\n-{3,}\s*\Z", "", post).strip()
    comments = _parse_comments(parts[1]) if len(parts) > 1 else []
    return Clipping(
        path=path,
        content_hash=content_hash,
        title=_frontmatter_value(frontmatter, "title"),
        source=_frontmatter_value(frontmatter, "source"),
        author=_frontmatter_author(frontmatter),
        published=_frontmatter_value(frontmatter, "published"),
        post_text=post,
        comments=comments,
    )


def load_clipping(path: Path) -> Clipping | None:
    """Read one clipping file; the hash is sha256 of the raw file bytes."""
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    return parse_clipping_text(data.decode("utf-8", errors="replace"), path, digest)


def load_clippings(directory: Path) -> list[Clipping]:
    """Load every ``*.md`` clipping under ``directory`` (recursive, sorted)."""
    clippings: list[Clipping] = []
    for path in sorted(directory.rglob("*.md")):
        if not path.is_file():
            continue
        clipping = load_clipping(path)
        if clipping is not None and clipping.source:
            clippings.append(clipping)
    return clippings
