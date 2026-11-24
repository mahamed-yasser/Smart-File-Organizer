from pathlib import Path


def scan_files(folder, recursive=False, skip_dirs=()):
    """Return the files in `folder`, sorted. Hidden files are skipped.

    recursive=False looks only at the top level. recursive=True also walks sub-folders,
    except top-level folders named in `skip_dirs` (used to leave already-sorted folders alone).
    """
    p = Path(folder)  # symbolic links are never followed or moved
    if not p.is_dir():
        return []
    if not recursive:
        return sorted(f for f in p.iterdir() if f.is_file() and not f.is_symlink() and not f.name.startswith("."))
    found = []
    skip = {s.lower() for s in skip_dirs}
    for f in p.rglob("*"):
        rel = f.relative_to(p)
        if not f.is_file() or f.is_symlink() or any(part.startswith(".") for part in rel.parts):
            continue
        if len(rel.parts) > 1 and rel.parts[0].lower() in skip:
            continue
        found.append(f)
    return sorted(found)
