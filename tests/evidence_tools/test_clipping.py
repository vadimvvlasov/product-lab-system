import hashlib

from pls_evidence.clipping import (
    load_clipping,
    load_clippings,
    normalize,
    normalize_name,
    normalize_url,
)


def test_normalize_rules():
    assert normalize("It’s  “fine”") == 'It\'s "fine"'
    assert normalize(r"snake\_case and \$5") == "snake_case and $5"
    assert normalize("see [**tool.example**](http://tool.example/) now") == "see tool.example now"
    assert normalize("a\n\n b\t c") == "a b c"
    assert normalize("Case Stays") == "Case Stays"


def test_normalize_name_and_url():
    assert normalize_name(r"Commenter\_Two") == "commenter_two"
    assert normalize_url("https://x.example/a/ ") == "https://x.example/a"


def test_parse_frontmatter_post_and_comments(clippings_dir):
    clipping = load_clipping(clippings_dir / "sample.md")
    assert clipping.title == "Sample freelancer thread"
    assert clipping.source.endswith("sample_freelancer_thread/")
    assert clipping.author == "poster_one"
    assert clipping.published == "2026-01-10"
    assert "one more thing" in clipping.post_text
    assert "Comments" not in clipping.post_text
    authors = [(c.author, c.date) for c in clipping.comments]
    assert authors == [
        (r"commenter\_two", "2026-01-11"),
        (r"third\_user", "2026-01-12"),
        (r"\[deleted\]", "2026-01-13"),
    ]
    assert "change order" in clipping.comments[0].text
    assert "scope control" in clipping.comments[1].text


def test_content_hash_is_sha256_of_bytes_and_stable(clippings_dir):
    path = clippings_dir / "sample.md"
    first = load_clipping(path)
    second = load_clipping(path)
    assert first.content_hash == second.content_hash
    assert first.content_hash == hashlib.sha256(path.read_bytes()).hexdigest()


def test_load_clippings_skips_files_without_frontmatter(clippings_dir):
    (clippings_dir / "notes.md").write_text("no frontmatter here", encoding="utf-8")
    names = sorted(c.path.name for c in load_clippings(clippings_dir))
    assert names == ["other.md", "sample.md"]
