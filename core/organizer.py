import json
import shutil
from pathlib import Path

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"},
    "Videos": {".mp4", ".avi", ".mkv", ".mov", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
}
HISTORY = ".organizer_history.json"


def category_for(path):
    ext = Path(path).suffix.lower()
    for name, exts in CATEGORIES.items():
        if ext in exts:
            return name
    return "Other"


def build_organization_plan(files, base):
    """Map target folder -> list of files. Nothing is moved here."""
    base = Path(base)
    plan = {}
    for f in files:
        plan.setdefault(base / category_for(f), []).append(Path(f))
    return plan


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
        return json.loads(h.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def execute_organization(plan, base):
    """Move files into their folders, never overwrite, record the batch for undo."""
    base = Path(base)
    moves = []
    for folder, items in plan.items():
        for src in items:
            if not src.exists():
                continue
            folder.mkdir(parents=True, exist_ok=True)
            dest = _free_name(folder / src.name)
            shutil.move(str(src), str(dest))
            moves.append({"from": str(src), "to": str(dest)})
    if moves:
        hist = _load(base)
        hist.append({"moves": moves})
        (base / HISTORY).write_text(json.dumps(hist, indent=2), encoding="utf-8")
    return len(moves)


def undo_last(base):
    """Move the files of the last batch back. Returns how many were restored."""
    base = Path(base)
    hist = _load(base)
    if not hist:
        return 0
    batch = hist.pop()
    restored = 0
    for m in reversed(batch["moves"]):
        to, frm = Path(m["to"]), Path(m["from"])
        if to.exists() and not frm.exists():
            shutil.move(str(to), str(frm))
            restored += 1
    for d in {Path(m["to"]).parent for m in batch["moves"]}:
        try:
            d.rmdir()
        except OSError:
            pass
    (base / HISTORY).write_text(json.dumps(hist, indent=2), encoding="utf-8")
    return restored
