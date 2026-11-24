from pathlib import Path


def scan_files(folder):
    """Return the files directly inside `folder` (not sub-folders, not hidden files)."""
    p = Path(folder)
    if not p.is_dir():
        return []
    return sorted(f for f in p.iterdir() if f.is_file() and not f.name.startswith("."))
