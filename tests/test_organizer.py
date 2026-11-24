import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.scanner import scan_files
from core.organizer import build_organization_plan, execute_organization, undo_last, category_for


def make(tmp_path):
    for n in ["a.jpg", "b.PNG", "c.mp4", "d.pdf", "e.mp3", "f.xyz"]:
        (tmp_path / n).write_text(n)
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "keep.jpg").write_text("x")


def test_scan_ignores_folders(tmp_path):
    make(tmp_path)
    assert len(scan_files(tmp_path)) == 6
    assert scan_files(tmp_path / "missing") == []


def test_plan_moves_nothing(tmp_path):
    make(tmp_path)
    plan = build_organization_plan(scan_files(tmp_path), tmp_path)
    assert {p.name for p in plan} == {"Images", "Videos", "Documents", "Audio", "Other"}
    assert (tmp_path / "a.jpg").exists()


def test_execute_and_undo(tmp_path):
    make(tmp_path)
    plan = build_organization_plan(scan_files(tmp_path), str(tmp_path))
    assert execute_organization(plan, tmp_path) == 6
    assert (tmp_path / "Images" / "a.jpg").exists() and (tmp_path / "Images" / "b.PNG").exists()
    assert not (tmp_path / "a.jpg").exists()
    assert (tmp_path / "sub" / "keep.jpg").exists()
    assert undo_last(tmp_path) == 6
    assert (tmp_path / "a.jpg").read_text() == "a.jpg"
    assert not (tmp_path / "Images").exists()
    assert undo_last(tmp_path) == 0


def test_no_overwrite(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "a.jpg").write_text("old")
    (tmp_path / "a.jpg").write_text("new")
    execute_organization(build_organization_plan(scan_files(tmp_path), tmp_path), tmp_path)
    assert (tmp_path / "Images" / "a.jpg").read_text() == "old"
    assert (tmp_path / "Images" / "a_1.jpg").read_text() == "new"


def test_category():
    assert category_for("X.JPG") == "Images" and category_for("x") == "Other"
