import json
import shutil
from datetime import datetime
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"},
    "Videos": {".mp4", ".avi", ".mkv", ".mov", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
}
CATEGORY_FOLDERS = tuple(CATEGORIES) + ("Other",)
HISTORY = ".organizer_history.json"
MAX_HISTORY = 20  # keeps the history file small: the last 20 runs can be undone


def category_for(path):
    ext = Path(path).suffix.lower()
    for name, exts in CATEGORIES.items():
        if ext in exts:
            return name
    return "Other"


def build_organization_plan(files, base, by_date=False):
    """Map target folder -> list of files. Nothing is moved here.

    by_date=True adds a YYYY-MM sub-folder (from the file's modified time): Images/2026-11.
    """
    base = Path(base)
    plan = {}
    for f in files:
        f = Path(f)
        folder = base / category_for(f)
        if by_date:
            try:
                folder = folder / datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m")
            except OSError:
                pass
        if f.parent == folder:  # already where it belongs
            continue
        plan.setdefault(folder, []).append(f)
    return plan


def summarize_plan(plan, base):
    """List of (folder relative to base, file count, total bytes), biggest first."""
    base = Path(base)
    rows = []
    for folder, items in plan.items():
        size = 0
        for i in items:
            try:
                size += i.stat().st_size
            except OSError:
                pass
        rows.append((str(folder.relative_to(base)), len(items), size))
    return sorted(rows, key=lambda r: (-r[1], r[0]))


def human_size(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{int(n)} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def _free_name(dest):
    if not dest.exists():
        return dest
    i = 1
    while True:
        c = dest.with_name(f"{dest.stem}_{i}{dest.suffix}")
        if not c.exists():
            return c
        i += 1


def _load(base):
    h = Path(base) / HISTORY
    try:
        data = json.loads(h.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def _save(base, hist):
    (Path(base) / HISTORY).write_text(json.dumps(hist[-MAX_HISTORY:], indent=2), encoding="utf-8")


def history_count(base):
    """How many runs can still be undone."""
    return len(_load(base))


def execute_organization(plan, base, progress=None, errors=None):
    """Move files into their folders, never overwrite, record the batch for undo.

    progress(done, total) is called after each file. A file that cannot be moved (locked,
    no permission) is skipped and its message is appended to `errors` if a list is given;
    the rest still move. Returns the number of files moved.
    """
    base = Path(base)
    total = sum(len(v) for v in plan.values())
    moves, done = [], 0
    for folder, items in plan.items():
        for src in items:
            done += 1
            dest = None
            try:
                if src.exists() and not src.is_symlink():
                    folder.mkdir(parents=True, exist_ok=True)
                    dest = _free_name(folder / src.name)
                    shutil.move(str(src), str(dest))
                    moves.append({"from": str(src), "to": str(dest)})
            except OSError as e:
                # a move across folders is copy + delete: if the delete failed, drop our copy
                # so the file is not left twice
                if dest is not None and src.exists() and dest.exists():
                    try:
                        dest.unlink()
                    except OSError:
                        pass
                if errors is not None:
                    errors.append(f"{src.name}: {e.strerror or e}")
            if progress:
                progress(done, total)
    if moves:
        hist = _load(base)
        hist.append({"at": datetime.now().isoformat(timespec="seconds"), "moves": moves})
        _save(base, hist)
    return len(moves)


def undo_last(base):
    """Move the files of the last run back. Returns how many were restored."""
    base = Path(base)
    hist = _load(base)
    if not hist:
        return 0
    batch = hist.pop()
    restored = 0
    for m in reversed(batch["moves"]):
        to, frm = Path(m["to"]), Path(m["from"])
        if to.exists() and not frm.exists():
            frm.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(to), str(frm))
            restored += 1
    for d in sorted({Path(m["to"]).parent for m in batch["moves"]}, key=lambda p: -len(p.parts)):
        for cur in (d, d.parent):  # remove the emptied date folder, then its category folder
            try:
                if cur != base:
                    cur.rmdir()
            except OSError:
                pass
    _save(base, hist)
    return restored
