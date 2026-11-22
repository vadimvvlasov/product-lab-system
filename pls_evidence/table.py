"""Parse the evidence table of ``templates/evidence.md`` from Markdown."""

from __future__ import annotations

import re

_ID = re.compile(r"^E-\d+$")
_PIPE_PLACEHOLDER = "\u0000"


def _split_row(line: str) -> list[str]:
    line = line.strip().replace("\\|", _PIPE_PLACEHOLDER)
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip().replace(_PIPE_PLACEHOLDER, "|") for cell in line.split("|")]


def parse_evidence_table(text: str) -> list[dict[str, str]]:
    """Return evidence rows (``E-NNN``) as dicts keyed by the header names.

    A literal pipe inside a cell must be written ``\\|``. Rows whose first
    cell is not an ``E-NNN`` id (the separator row, the template placeholder)
    are ignored.
    """
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if header is not None and rows:
                break
            continue
        cells = _split_row(stripped)
        if header is None:
            if cells and cells[0] == "id" and "source_url" in cells:
                header = cells
            continue
        if not cells or not _ID.match(cells[0]):
            continue
        padded = cells + [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, padded[: len(header)])))
    return rows
