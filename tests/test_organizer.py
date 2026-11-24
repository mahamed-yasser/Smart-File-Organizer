import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.scanner import scan_files
from core.organizer import (build_organization_plan, execute_organization, undo_last, category_for,
                            CATEGORY_FOLDERS, history_count)


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


def test_recursive_scan_skips_hidden_and_sorted_folders(tmp_path):
    from core.organizer import CATEGORY_FOLDERS
    make(tmp_path)
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "done.jpg").write_text("x")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "obj.jpg").write_text("x")
    names = {f.name for f in scan_files(tmp_path, recursive=True, skip_dirs=CATEGORY_FOLDERS)}
    assert "keep.jpg" in names and "done.jpg" not in names and "obj.jpg" not in names


def test_recursive_organize_and_undo_restores_subfolder(tmp_path):
    make(tmp_path)
    files = scan_files(tmp_path, recursive=True)
    plan = build_organization_plan(files, tmp_path)
    assert execute_organization(plan, tmp_path) == 7
    assert (tmp_path / "Images" / "keep.jpg").exists()
    assert undo_last(tmp_path) == 7
    assert (tmp_path / "sub" / "keep.jpg").exists()


def test_by_date_folder(tmp_path):
    import os
    f = tmp_path / "a.jpg"
    f.write_text("x")
    os.utime(f, (1700000000, 1700000000))  # Nov 2023
    plan = build_organization_plan([f], tmp_path, by_date=True)
    assert [p.relative_to(tmp_path).as_posix() for p in plan] == ["Images/2023-11"]
    execute_organization(plan, tmp_path)
    assert (tmp_path / "Images" / "2023-11" / "a.jpg").exists()
    undo_last(tmp_path)
    assert f.exists() and not (tmp_path / "Images").exists()


def test_name_collision_never_overwrites(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "a.jpg").write_text("old")
    (tmp_path / "a.jpg").write_text("new")
    execute_organization(build_organization_plan(scan_files(tmp_path), tmp_path), tmp_path)
    assert (tmp_path / "Images" / "a.jpg").read_text() == "old"
    assert (tmp_path / "Images" / "a_1.jpg").read_text() == "new"


def test_multi_level_undo(tmp_path):
    from core.organizer import history_count
    (tmp_path / "a.jpg").write_text("1")
    execute_organization(build_organization_plan(scan_files(tmp_path), tmp_path), tmp_path)
    (tmp_path / "b.mp3").write_text("2")
    execute_organization(build_organization_plan(scan_files(tmp_path), tmp_path), tmp_path)
    assert history_count(tmp_path) == 2
    assert undo_last(tmp_path) == 1 and (tmp_path / "b.mp3").exists()
    assert (tmp_path / "Images" / "a.jpg").exists()
    assert undo_last(tmp_path) == 1 and (tmp_path / "a.jpg").exists()


def test_summary_and_human_size(tmp_path):
    from core.organizer import summarize_plan, human_size
    make(tmp_path)
    rows = summarize_plan(build_organization_plan(scan_files(tmp_path), tmp_path), tmp_path)
    assert sum(r[1] for r in rows) == 6
    assert human_size(512) == "512 B" and human_size(2048) == "2.0 KB"


def test_cli_dry_run_yes_undo(tmp_path, capsys):
    import main as cli
    make(tmp_path)
    assert cli.main([str(tmp_path), "--dry-run"]) == 0
    assert (tmp_path / "a.jpg").exists()
    assert cli.main([str(tmp_path), "-y"]) == 0
    assert (tmp_path / "Images" / "a.jpg").exists()
    assert cli.main([str(tmp_path), "--undo"]) == 0
    assert (tmp_path / "a.jpg").exists()
    assert cli.main([str(tmp_path / "nope")]) == 2
    assert "Total" in capsys.readouterr().out


def test_cli_cancel_moves_nothing(tmp_path):
    import main as cli
    make(tmp_path)
    assert cli.run(str(tmp_path), ask=lambda _: "n") == 0
    assert (tmp_path / "a.jpg").exists()


# ---- safety ----
def test_undo_never_overwrites_a_new_file_at_the_old_path(tmp_path):
    (tmp_path / "a.jpg").write_text("original")
    execute_organization(build_organization_plan(scan_files(tmp_path), tmp_path), tmp_path)
    (tmp_path / "a.jpg").write_text("NEW file made after organizing")
    assert undo_last(tmp_path) == 0
    assert (tmp_path / "a.jpg").read_text() == "NEW file made after organizing"
    assert (tmp_path / "Images" / "a.jpg").read_text() == "original"  # not lost


def test_undo_keeps_edits_made_after_the_move(tmp_path):
    (tmp_path / "a.txt").write_text("v1")
    execute_organization(build_organization_plan(scan_files(tmp_path), tmp_path), tmp_path)
    (tmp_path / "Documents" / "a.txt").write_text("v2 edited")
    assert undo_last(tmp_path) == 1
    assert (tmp_path / "a.txt").read_text() == "v2 edited"


def test_undo_skips_files_the_user_deleted_and_survives_bad_history(tmp_path):
    (tmp_path / "a.jpg").write_text("1")
    (tmp_path / "b.jpg").write_text("2")
    execute_organization(build_organization_plan(scan_files(tmp_path), tmp_path), tmp_path)
    (tmp_path / "Images" / "a.jpg").unlink()
    assert undo_last(tmp_path) == 1
    (tmp_path / ".organizer_history.json").write_text("{not json")
    assert undo_last(tmp_path) == 0  # corrupt history: nothing happens, no crash


def test_symlinks_are_never_followed_or_moved(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.jpg").write_text("x")
    base = tmp_path / "base"
    base.mkdir()
    (base / "real.jpg").write_text("r")
    (base / "link.jpg").symlink_to(outside / "secret.jpg")
    (base / "linkdir").symlink_to(outside, target_is_directory=True)
    for rec in (False, True):
        names = {f.name for f in scan_files(base, recursive=rec)}
        assert names == {"real.jpg"}
    execute_organization(build_organization_plan(scan_files(base, recursive=True), base), base)
    assert (outside / "secret.jpg").exists() and (base / "link.jpg").is_symlink()


def test_repeat_run_is_idempotent(tmp_path):
    make(tmp_path)
    p = build_organization_plan(scan_files(tmp_path, recursive=True, skip_dirs=CATEGORY_FOLDERS), tmp_path, by_date=False)
    assert execute_organization(p, tmp_path) == 7
    again = build_organization_plan(scan_files(tmp_path, recursive=True, skip_dirs=CATEGORY_FOLDERS), tmp_path)
    assert again == {} and execute_organization(again, tmp_path) == 0
    assert history_count(tmp_path) == 1  # an empty run is not recorded


def test_partial_failure_keeps_going_and_leaves_no_duplicate(tmp_path):
    import os
    (tmp_path / "ok.mp3").write_text("fine")
    locked = tmp_path / "locked"
    locked.mkdir()
    (locked / "stuck.jpg").write_text("stuck")
    os.chmod(locked, 0o555)  # cannot remove files from it
    try:
        if os.access(locked, os.W_OK):
            import pytest; pytest.skip("account ignores permissions")
        errors = []
        plan = build_organization_plan(scan_files(tmp_path, recursive=True), tmp_path)
        assert execute_organization(plan, tmp_path, errors=errors) == 1
        assert len(errors) == 1 and "stuck.jpg" in errors[0]
        assert (locked / "stuck.jpg").read_text() == "stuck"          # original untouched
        assert not (tmp_path / "Images" / "stuck.jpg").exists()       # no stray copy
        assert (tmp_path / "Audio" / "ok.mp3").exists()
        assert undo_last(tmp_path) == 1                               # undo only covers what moved
    finally:
        os.chmod(locked, 0o755)
