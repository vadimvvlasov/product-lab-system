import json

from pls_evidence.cli import main
from pls_evidence.clipping import load_clippings
from pls_evidence.report import build_report, render_csv, render_markdown

from .conftest import make_row, make_table


def test_report_flags_and_columns(clippings_dir):
    rows = {r.file: r for r in build_report(load_clippings(clippings_dir))}
    sample = rows["sample.md"]
    assert sample.source_name == "forum.example"
    assert sample.author == "poster_one"
    assert sample.comments == 3
    assert "builder_post" in sample.flags
    assert any(f.startswith("external_link:") for f in sample.flags)
    assert rows["other.md"].flags == []


def test_report_renderers(clippings_dir):
    rows = build_report(load_clippings(clippings_dir))
    markdown = render_markdown(rows)
    assert markdown.splitlines()[0].startswith("| file | source_name")
    assert "sample.md" in markdown
    csv_text = render_csv(rows)
    assert csv_text.splitlines()[0] == "file,source_name,published,author,title,comments,flags"


def test_cli_verify_exit_codes_and_log(clippings_dir, tmp_path, capsys):
    evidence = tmp_path / "evidence.md"
    evidence.write_text(make_table(make_row("E-001")), encoding="utf-8")
    log = tmp_path / "v.json"
    code = main(["verify", "--evidence", str(evidence), "--clippings", str(clippings_dir), "--log", str(log)])
    assert code == 0
    assert json.loads(log.read_text(encoding="utf-8"))["summary"]["PASS"] == 1
    assert "PASS=1 FAIL=0" in capsys.readouterr().out

    evidence.write_text(make_table(make_row("E-001", excerpt="fabricated quote")), encoding="utf-8")
    code = main(["verify", "--evidence", str(evidence), "--clippings", str(clippings_dir), "--log", str(log), "--overwrite"])
    assert code == 1
    assert "FAIL E-001" in capsys.readouterr().out


def test_cli_verify_errors(clippings_dir, tmp_path, capsys):
    missing = tmp_path / "missing.md"
    assert main(["verify", "--evidence", str(missing), "--clippings", str(clippings_dir), "--log", str(tmp_path / "l.json")]) == 2
    empty = tmp_path / "empty.md"
    empty.write_text("# nothing\n", encoding="utf-8")
    assert main(["verify", "--evidence", str(empty), "--clippings", str(clippings_dir), "--log", str(tmp_path / "l.json")]) == 2
    capsys.readouterr()


def test_cli_report_stdout_and_file(clippings_dir, tmp_path, capsys):
    assert main(["report", "--clippings", str(clippings_dir)]) == 0
    assert "sample.md" in capsys.readouterr().out
    out = tmp_path / "report.csv"
    assert main(["report", "--clippings", str(clippings_dir), "--format", "csv", "--out", str(out)]) == 0
    assert out.read_text(encoding="utf-8").startswith("file,source_name")
    assert main(["report", "--clippings", str(clippings_dir), "--out", str(out)]) == 2
    assert main(["report", "--clippings", str(clippings_dir), "--out", str(clippings_dir / "r.md")]) == 2
    capsys.readouterr()
