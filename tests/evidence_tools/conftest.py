"""Synthetic fixtures: no real clippings or third-party text are used."""

from pathlib import Path

import pytest

CLIPPING = """---
title: "Sample freelancer thread"
source: "https://forum.example/r/sample/comments/abc1/sample_freelancer_thread/"
author:
  - "[[poster_one]]"
published: 2026-01-10
created: 2026-02-01
tags:
  - "clippings"
---
I built a tiny scheduler and the client said "just one more thing" twice.
The   invoice stayed open for 60 days \\- every week the same excuse.
Check https://shop.example/tool for details.

---

## Comments

> **commenter\\_two** · [2026-01-11](https://forum.example/c/1) · 4 points
>
> We use a change order for every extra request.
>
> > **third\\_user** · [2026-01-12](https://forum.example/c/2) · 1 points
> >
> > It’s called “scope control” and it works.

> **\\[deleted\\]** · [2026-01-13](https://forum.example/c/3) · 0 points
>
> Hiring a designer, DM me.
"""

OTHER_CLIPPING = """---
title: "Unrelated thread"
source: "https://forum.example/r/other/comments/zzz9/unrelated/"
author:
  - "[[someone_else]]"
published: 2026-03-01
---
Completely different text about gardening.
"""

TABLE_HEADER = (
    "| id | source_url | source_name | source_type | published_at | event_date | author_or_thread "
    "| author_id | verbatim_excerpt | paraphrase | evidence_type | signal | target_segment "
    "| current_workaround | time_or_money_cost | payment_signal | counter_evidence | source_quality "
    "| cluster | verified_by | verified_at | notes |"
)
TABLE_SEPARATOR = "|" + "---|" * 22


def make_row(
    row_id="E-001",
    url="https://forum.example/r/sample/comments/abc1/sample_freelancer_thread/",
    published="2026-01-10",
    author="poster_one",
    excerpt="the client said \"just one more thing\" twice",
) -> str:
    cells = [
        row_id, url, "forum", "primary", published, "unknown", "thread", author, excerpt, "",
        "pain", "L2", "freelancer", "", "", "none", "", "ok", "C-01", "", "", "",
    ]
    return "| " + " | ".join(cells) + " |"


def make_table(*rows: str) -> str:
    return "\n".join([TABLE_HEADER, TABLE_SEPARATOR, *rows]) + "\n"


@pytest.fixture
def clippings_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "clips"
    directory.mkdir()
    (directory / "sample.md").write_text(CLIPPING, encoding="utf-8")
    (directory / "other.md").write_text(OTHER_CLIPPING, encoding="utf-8")
    return directory
