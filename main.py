import argparse
import sys
from pathlib import Path

from core.scanner import scan_files
from core.organizer import (CATEGORY_FOLDERS, build_organization_plan, execute_organization,
                            history_count, human_size, summarize_plan, undo_last)


def print_plan(plan, base):
    rows = summarize_plan(plan, base)
    for name, count, size in rows:
        print(f"  {name:<22} {count:>4} files  {human_size(size):>9}")
    print(f"  Total: {sum(r[1] for r in rows)} files")


def run(folder, recursive=False, by_date=False, dry_run=False, assume_yes=False, undo=False, ask=input):
    base = Path(folder)
    if not base.is_dir():
        print(f"Folder not found: {folder}")
        return 2
    if undo:
        n = undo_last(base)
        print(f"Restored {n} files." if n else "Nothing to undo.")
        return 0
    files = scan_files(base, recursive=recursive, skip_dirs=CATEGORY_FOLDERS)
    plan = build_organization_plan(files, base, by_date=by_date)
    if not plan:
        print("Nothing to organize.")
        return 0
    print("Preview:")
    print_plan(plan, base)
    if dry_run:
        print("Dry run: nothing was moved.")
        return 0
    if not assume_yes and ask("\nMove these files? (y/n): ").strip().lower() != "y":
        print("Cancelled. Nothing was moved.")
        return 0
    errors = []
    moved = execute_organization(plan, base, errors=errors)
    print(f"Moved {moved} files. You can undo this run ({history_count(base)} run(s) saved).")
    for e in errors:
        print(f"  Skipped: {e}")
    return 1 if errors else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sort the files in a folder into Images, Videos, Audio, Documents, Archives and Other.")
    ap.add_argument("folder", nargs="?", help="folder to organize (asked interactively if omitted)")
    ap.add_argument("-r", "--recursive", action="store_true", help="also organize files inside sub-folders")
    ap.add_argument("--by-date", action="store_true", help="add a YYYY-MM folder inside each category")
    ap.add_argument("-n", "--dry-run", action="store_true", help="show the preview and move nothing")
    ap.add_argument("-y", "--yes", action="store_true", help="do not ask for confirmation")
    ap.add_argument("--undo", action="store_true", help="undo the last run in this folder")
    a = ap.parse_args(argv)
    folder = a.folder or input("Enter folder path: ").strip()
    return run(folder, a.recursive, a.by_date, a.dry_run, a.yes, a.undo)


if __name__ == "__main__":
    sys.exit(main())
