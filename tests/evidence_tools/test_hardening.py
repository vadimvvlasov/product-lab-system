"""Edge cases from the QA of #27: skipped files, CRLF, dates, author forms, short excerpts."""

import json
import os
from pathlib import Path

import pytest

from pls_evidence.cli import main
from pls_evidence.clipping import normalize, normalize_name, scan_clippings
from pls_evidence.report import build_report, render_csv
from pls_evidence.table import parse_evidence_table
from pls_evidence.verify import FAIL, NO_SNAPSHOT, PASS, SKIP, verify_row

from .conftest import CLIPPING, make_row, make_table

POST_URL = "https://forum.example/r/sample/comments/abc1/sample_freelancer_thread/"


def verify(clippings_dir: Path, row: str):
    clippings, _ = scan_clippings(clippings_dir)
    return verify_row(parse_evidence_table(make_table(row))[0], clippings)


def write_clipping(directory: Path, name: str, text: str, *, raw: bytes | None = None) -> None:
    (directory / name).write_bytes(raw if raw is not None else text.encode("utf-8"))


# --- skipped clippings -------------------------------------------------------

def test_scan_lists_skipped_files_with_reasons(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "ok.md", CLIPPING)
    write_clipping(directory, "plain.md", "no frontmatter here")
    write_clipping(directory, "nosource.md", "---\ntitle: \"x\"\nauthor:\n  - \"[[a]]\"\n---\nbody\n")
    clippings, skipped = scan_clippings(directory)
    assert [c.path.name for c in clippings] == ["ok.md"]
    assert {s.path.name: s.reason for s in skipped} == {
        "plain.md": "no frontmatter",
        "nosource.md": "no source in frontmatter",
    }


@pytest.mark.skipif(os.name != "posix" or os.geteuid() == 0, reason="needs a non-root POSIX user")
def test_unreadable_file_is_reported(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    path = directory / "locked.md"
    path.write_text(CLIPPING, encoding="utf-8")
    path.chmod(0)
    try:
        _, skipped = scan_clippings(directory)
    finally:
        path.chmod(0o644)
    assert [s.path.name for s in skipped] == ["locked.md"]
    assert skipped[0].reason.startswith("unreadable")


def test_verify_log_and_cli_list_skipped(tmp_path, capsys):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "ok.md", CLIPPING)
    write_clipping(directory, "plain.md", "no frontmatter here")
    evidence = tmp_path / "evidence.md"
    evidence.write_text(make_table(make_row()), encoding="utf-8")
    log = tmp_path / "log.json"
    code = main(["verify", "--evidence", str(evidence), "--clippings", str(directory), "--log", str(log)])
    out = capsys.readouterr().out
    assert code == 0
    assert "SKIPPED_CLIPPINGS=1" in out
    assert "SKIPPED plain.md: no frontmatter" in out
    data = json.loads(log.read_text(encoding="utf-8"))
    assert [(Path(s["file"]).name, s["reason"]) for s in data["skipped_clippings"]] == [("plain.md", "no frontmatter")]


def test_report_includes_skipped_rows(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "ok.md", CLIPPING)
    write_clipping(directory, "plain.md", "no frontmatter here")
    clippings, skipped = scan_clippings(directory)
    rows = {r.file: r for r in build_report(clippings, skipped)}
    assert rows["plain.md"].flags == ["skipped: no frontmatter"]
    assert "plain.md" in render_csv(list(rows.values()))


# --- CRLF and BOM ---------------------------------------------------------------

def test_crlf_clipping_verifies_like_lf(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "crlf.md", "", raw=CLIPPING.replace("\n", "\r\n").encode("utf-8"))
    assert verify(directory, make_row()).status == PASS
    comment = make_row(excerpt="We use a change order for every extra request.", author="commenter_two", published="2026-01-11")
    assert verify(directory, comment).status == PASS


def test_bom_prefixed_clipping_parses(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "bom.md", "", raw=b"\xef\xbb\xbf" + CLIPPING.encode("utf-8"))
    assert verify(directory, make_row()).status == PASS


# --- dates -----------------------------------------------------------------------

def test_timestamped_published_matches_by_date_prefix(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "ts.md", CLIPPING.replace("published: 2026-01-10", "published: 2026-01-10T10:00:00Z"))
    assert verify(directory, make_row(published="2026-01-10")).status == PASS
    assert verify(directory, make_row(published="2026-01-10T23:59:59+05:00")).status == PASS
    wrong = verify(directory, make_row(published="2026-01-11"))
    assert wrong.status == FAIL and wrong.fields["published_at"] == FAIL


# --- author forms --------------------------------------------------------------------

@pytest.mark.parametrize(
    "author_block",
    [
        'author: poster_one',
        'author: "poster_one"',
        'author:\n  - poster_one',
        'author:\n  - "poster_one"',
        'author:\n  - "[[poster_one]]"',
    ],
)
def test_frontmatter_author_forms(tmp_path, author_block):
    directory = tmp_path / "clips"
    directory.mkdir()
    text = CLIPPING.replace('author:\n  - "[[poster_one]]"', author_block)
    assert author_block in text
    write_clipping(directory, "a.md", text)
    result = verify(directory, make_row(author="poster_one"))
    assert result.status == PASS and result.fields["author_id"] == PASS


@pytest.mark.parametrize("row_author", ["u/poster_one", "/u/poster_one", "@poster_one", "Poster_One"])
def test_row_author_prefixes_and_case(clippings_dir, row_author):
    assert verify(clippings_dir, make_row(author=row_author)).status == PASS


def test_normalize_name_prefixes():
    assert normalize_name("u/Someone") == "someone"
    assert normalize_name("/u/Someone") == "someone"
    assert normalize_name("@Someone") == "someone"
    assert normalize_name("user_name") == "user_name"  # only a leading u/ is a prefix


def test_missing_author_in_clipping_is_skip_with_warning(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "noauthor.md", CLIPPING.replace('author:\n  - "[[poster_one]]"\n', ""))
    result = verify(directory, make_row(author="poster_one"))
    assert result.status == PASS
    assert result.fields["author_id"] == SKIP
    assert any("no author" in w for w in result.warnings)


def test_wrong_author_still_fails(clippings_dir):
    result = verify(clippings_dir, make_row(author="someone_else"))
    assert result.status == FAIL and result.fields["author_id"] == FAIL


# --- excerpt length and normalization -----------------------------------------------------

def test_short_excerpt_warns_but_does_not_change_status(clippings_dir):
    result = verify(clippings_dir, make_row(excerpt="tiny scheduler"))
    assert result.status == PASS
    assert any("shorter than 20" in w for w in result.warnings)
    long = verify(clippings_dir, make_row())
    assert long.warnings == []


def test_blockquote_markers_in_post_are_ignored(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    text = CLIPPING.replace(
        "I built a tiny scheduler",
        "> The earlier answer said the contract was fine.\n> Then the client changed the scope.\n\nI built a tiny scheduler",
    )
    write_clipping(directory, "q.md", text)
    row = make_row(excerpt="The earlier answer said the contract was fine. Then the client changed the scope.")
    assert verify(directory, row).status == PASS
    quoted = make_row(excerpt="> The earlier answer said the contract was fine.")
    assert verify(directory, quoted).status == PASS


def test_markdown_link_with_parentheses_in_url():
    assert normalize("see [the page](http://x.example/a_(b)) now") == "see the page now"
    assert normalize("[**bold**](http://x.example/) text") == "bold text"


# --- strict mode ----------------------------------------------------------------------------

def test_strict_flag_fails_on_no_snapshot_only(clippings_dir, tmp_path, capsys):
    evidence = tmp_path / "evidence.md"
    evidence.write_text(make_table(make_row("E-001"), make_row("E-002", url="https://nowhere.example/x", excerpt="text that exists nowhere")), encoding="utf-8")
    log = tmp_path / "log.json"
    base = ["verify", "--evidence", str(evidence), "--clippings", str(clippings_dir), "--log", str(log)]
    assert main(base) == 0
    assert main(base + ["--overwrite", "--strict"]) == 1
    out = capsys.readouterr().out
    assert "NO_SNAPSHOT=1" in out
    data = json.loads(log.read_text(encoding="utf-8"))
    assert {r["id"]: r["status"] for r in data["results"]} == {"E-001": PASS, "E-002": NO_SNAPSHOT}


def test_strict_flag_passes_when_all_rows_pass(clippings_dir, tmp_path):
    evidence = tmp_path / "evidence.md"
    evidence.write_text(make_table(make_row()), encoding="utf-8")
    code = main(["verify", "--evidence", str(evidence), "--clippings", str(clippings_dir), "--log", str(tmp_path / "l.json"), "--strict"])
    assert code == 0


def test_log_contains_warnings_per_row(clippings_dir, tmp_path):
    evidence = tmp_path / "evidence.md"
    evidence.write_text(make_table(make_row(excerpt="tiny scheduler")), encoding="utf-8")
    log = tmp_path / "log.json"
    main(["verify", "--evidence", str(evidence), "--clippings", str(clippings_dir), "--log", str(log)])
    entry = json.loads(log.read_text(encoding="utf-8"))["results"][0]
    assert any("shorter than 20" in w for w in entry["warnings"])


# --- frontmatter values (QA of #33: empty values must not swallow the next line) ---------------

FRONT = '---\ntitle: "t"\nsource: "https://forum.example/x/"\nauthor:\n  - "[[poster_one]]"\npublished: 2026-01-10\ncreated: 2026-02-01\n---\nBody text that is long enough to quote here.\n'


def parse(text: str):
    from pls_evidence.clipping import parse_clipping_text

    return parse_clipping_text(text, Path("x.md"), "0" * 64)


def test_empty_source_is_skipped_not_swallowing_next_line():
    clipping, reason = parse(FRONT.replace('source: "https://forum.example/x/"', "source:"))
    assert clipping is None
    assert reason == "no source in frontmatter"


def test_empty_source_listed_as_skipped_by_scan(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "empty.md", FRONT.replace('source: "https://forum.example/x/"', "source:"))
    clippings, skipped = scan_clippings(directory)
    assert clippings == []
    assert [(s.path.name, s.reason) for s in skipped] == [("empty.md", "no source in frontmatter")]


def test_empty_published_and_title_stay_empty():
    text = FRONT.replace("published: 2026-01-10", "published:").replace('title: "t"', "title:")
    clipping, _ = parse(text)
    assert clipping.published == ""
    assert clipping.title == ""
    assert clipping.source == "https://forum.example/x/"


def test_empty_published_gives_skip_and_warning(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "nodate.md", FRONT.replace("published: 2026-01-10", "published:"))
    row = make_row(url="https://forum.example/x/", excerpt="Body text that is long enough to quote here.", published="2026-01-10")
    result = verify(directory, row)
    assert result.status == PASS
    assert result.fields["published_at"] == SKIP
    assert any("no date" in w for w in result.warnings)


@pytest.mark.parametrize(
    "author_block",
    ["author: poster_one # note", "author:\n  - poster_one # note", 'author:\n  - "[[poster_one]]" # note'],
)
def test_trailing_yaml_comment_on_author_is_ignored(author_block):
    clipping, _ = parse(FRONT.replace('author:\n  - "[[poster_one]]"', author_block))
    assert clipping.author == "poster_one"


def test_quoted_scalars_with_escapes_and_fragments():
    text = FRONT.replace('title: "t"', 'title: "He said \\"hi\\" # not a comment"')
    clipping, _ = parse(text)
    assert clipping.title == 'He said "hi" # not a comment'
    single, _ = parse(FRONT.replace('title: "t"', "title: 'it''s fine'"))
    assert single.title == "it's fine"
    fragment, _ = parse(FRONT.replace('source: "https://forum.example/x/"', "source: https://forum.example/x/#frag"))
    assert fragment.source == "https://forum.example/x/#frag"
    commented, _ = parse(FRONT.replace('source: "https://forum.example/x/"', "source: https://forum.example/x/ # saved"))
    assert commented.source == "https://forum.example/x/"


def test_lone_cr_line_endings(tmp_path):
    directory = tmp_path / "clips"
    directory.mkdir()
    write_clipping(directory, "cr.md", "", raw=CLIPPING.replace("\n", "\r").encode("utf-8"))
    assert verify(directory, make_row()).status == PASS
