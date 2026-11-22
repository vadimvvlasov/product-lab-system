from pls_evidence.table import parse_evidence_table

from .conftest import TABLE_HEADER, TABLE_SEPARATOR, make_row, make_table


def test_parses_rows_and_ignores_separator_and_placeholder():
    placeholder = "| E-xxx | | | | | | | | | | | L_ | | | | | | | C-01 | | | |"
    rows = parse_evidence_table(make_table(make_row("E-001"), make_row("E-002"), placeholder))
    assert [r["id"] for r in rows] == ["E-001", "E-002"]
    assert rows[0]["author_id"] == "poster_one"
    assert rows[0]["verbatim_excerpt"].startswith("the client said")


def test_escaped_pipe_inside_cell():
    row = make_row(excerpt=r"left \| right")
    parsed = parse_evidence_table(make_table(row))
    assert parsed[0]["verbatim_excerpt"] == "left | right"


def test_no_table_returns_empty():
    assert parse_evidence_table("# Title\n\nno table\n") == []


def test_stops_after_table_block():
    text = make_table(make_row("E-001")) + "\nText\n\n| id | source_url |\n|---|---|\n| E-002 | x |\n"
    assert [r["id"] for r in parse_evidence_table(text)] == ["E-001"]


def test_template_header_constant_is_a_valid_header():
    assert TABLE_HEADER.startswith("| id | source_url")
    assert TABLE_SEPARATOR.count("---") == 22
