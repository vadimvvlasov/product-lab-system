import json

import pytest

from pls_evidence.clipping import load_clippings
from pls_evidence.table import parse_evidence_table
from pls_evidence.verify import FAIL, NO_SNAPSHOT, PASS, SKIP, summarize, verify_rows, write_log

from .conftest import make_row, make_table

POST_URL = "https://forum.example/r/sample/comments/abc1/sample_freelancer_thread/"


def run(clippings_dir, row):
    rows = parse_evidence_table(make_table(row))
    return verify_rows(rows, load_clippings(clippings_dir))[0]


def test_post_excerpt_matches_url_date_author(clippings_dir):
    result = run(clippings_dir, make_row())
    assert result.status == PASS
    assert result.found_in == "post"
    assert result.snapshot == "sample.md"
    assert len(result.content_hash) == 64
    assert result.fields["published_at"] == PASS
    assert result.fields["author_id"] == PASS


def test_normalization_handles_spacing_quotes_and_escapes(clippings_dir):
    # the clipping holds "The   invoice ... 60 days \- every week": spacing and the escape are normalised
    result = run(clippings_dir, make_row(excerpt="The invoice stayed open for 60 days - every week the same excuse."))
    assert result.status == PASS
    # case is never altered
    result = run(clippings_dir, make_row(excerpt="the invoice stayed open for 60 days - every week the same excuse."))
    assert result.status == FAIL


def test_modified_excerpt_fails(clippings_dir):
    result = run(clippings_dir, make_row(excerpt="the client said just one more thing three times"))
    assert result.status == FAIL
    assert result.fields["verbatim_excerpt"] == FAIL


def test_wrong_url_fails_when_excerpt_exists_elsewhere(clippings_dir):
    result = run(clippings_dir, make_row(url="https://forum.example/r/other/comments/zzz9/unrelated/"))
    assert result.status == FAIL
    assert result.fields["verbatim_excerpt"] == FAIL


def test_excerpt_in_clipping_with_different_source_is_flagged(clippings_dir):
    row = make_row(url="https://forum.example/r/typo/comments/nope/", excerpt="Completely different text about gardening.")
    result = run(clippings_dir, row)
    assert result.status == FAIL
    assert result.fields["source_url"] == FAIL
    assert "different source" in result.note


def test_unknown_url_without_match_is_no_snapshot(clippings_dir):
    result = run(clippings_dir, make_row(url="https://nowhere.example/x", excerpt="text that exists nowhere"))
    assert result.status == NO_SNAPSHOT


def test_wrong_date_and_wrong_author_fail(clippings_dir):
    assert run(clippings_dir, make_row(published="2026-01-11")).fields["published_at"] == FAIL
    assert run(clippings_dir, make_row(author="someone_else")).fields["author_id"] == FAIL


def test_unknown_author_and_empty_date_are_skipped(clippings_dir):
    result = run(clippings_dir, make_row(author="unknown", published=""))
    assert result.status == PASS
    assert result.fields["author_id"] == SKIP
    assert result.fields["published_at"] == SKIP


def test_comment_excerpt_uses_comment_author_and_date(clippings_dir):
    row = make_row(excerpt="We use a change order for every extra request.", author="commenter_two", published="2026-01-11")
    result = run(clippings_dir, row)
    assert result.status == PASS
    assert result.found_in == "comment"


def test_comment_excerpt_with_post_author_fails(clippings_dir):
    row = make_row(excerpt="We use a change order for every extra request.", author="poster_one", published="2026-01-10")
    result = run(clippings_dir, row)
    assert result.status == FAIL
    assert result.fields["author_id"] == FAIL
    assert result.fields["published_at"] == FAIL


def test_nested_comment_with_curly_quotes(clippings_dir):
    row = make_row(excerpt="It's called \"scope control\" and it works.", author="third_user", published="2026-01-12")
    assert run(clippings_dir, row).status == PASS


def test_escaped_deleted_author(clippings_dir):
    row = make_row(excerpt="Hiring a designer, DM me.", author="[deleted]", published="2026-01-13")
    assert run(clippings_dir, row).status == PASS


def test_empty_excerpt_and_url_fail(clippings_dir):
    assert run(clippings_dir, make_row(excerpt="")).status == FAIL
    assert run(clippings_dir, make_row(url="")).status == FAIL


def test_summarize_counts(clippings_dir):
    rows = parse_evidence_table(make_table(make_row("E-001"), make_row("E-002", excerpt="not there at all")))
    counts = summarize(verify_rows(rows, load_clippings(clippings_dir)))
    assert counts == {PASS: 1, FAIL: 1, NO_SNAPSHOT: 0}


def test_write_log_content_and_no_other_writes(clippings_dir, tmp_path):
    evidence = tmp_path / "evidence.md"
    evidence.write_text(make_table(make_row()), encoding="utf-8")
    before = {p: p.read_bytes() for p in [evidence, *clippings_dir.glob("*.md")]}
    results = verify_rows(parse_evidence_table(evidence.read_text(encoding="utf-8")), load_clippings(clippings_dir))
    log = tmp_path / "logs" / "verify.json"
    write_log(log, evidence_path=evidence, clippings_dir=clippings_dir, results=results, clock=lambda: "2026-11-22T00:00:00+00:00")
    data = json.loads(log.read_text(encoding="utf-8"))
    assert data["verified_at"] == "2026-11-22T00:00:00+00:00"
    assert data["summary"]["PASS"] == 1
    entry = data["results"][0]
    assert entry["content_hash"] == results[0].content_hash
    assert entry["snapshot"] == "sample.md"
    assert "does not confirm the claim" in data["scope"]
    assert before == {p: p.read_bytes() for p in before}
    assert sorted(p.name for p in tmp_path.iterdir()) == ["clips", "evidence.md", "logs"]


def test_write_log_refuses_inputs_and_existing_files(clippings_dir, tmp_path):
    evidence = tmp_path / "evidence.md"
    evidence.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        write_log(evidence, evidence_path=evidence, clippings_dir=clippings_dir, results=[])
    with pytest.raises(ValueError):
        write_log(clippings_dir / "log.json", evidence_path=evidence, clippings_dir=clippings_dir, results=[])
    log = tmp_path / "log.json"
    log.write_text("old", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_log(log, evidence_path=evidence, clippings_dir=clippings_dir, results=[])
    write_log(log, evidence_path=evidence, clippings_dir=clippings_dir, results=[], overwrite=True)
    assert json.loads(log.read_text(encoding="utf-8"))["results"] == []
