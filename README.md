# Smart File Organizer

Small Python tool that sorts the files in one folder into Images, Videos, Audio, Documents, Archives and Other, with undo for the last run.

![App Interface](screenshot.png)

_The screenshot is the desktop window (CustomTkinter) in its empty start state._

## What works (tested)

- Scans one folder (not sub-folders) and groups files by extension.
- Moves files into category folders. Never overwrites: a name clash becomes `name_1.ext`.
- Preview of how many files go to each folder before anything moves (command line).
- Undo of the last run, saved in `.organizer_history.json` inside the organized folder.
- 5 automated tests (`python -m pytest tests`) cover scan, plan, move, undo and name clashes.

## Run

```bash
pip install -r requirements.txt
python main.py        # command line: asks for a folder, shows a preview, asks to confirm
python gui_main.py    # desktop window: Browse, Start Organizing, Undo Cleanup
```

## Limits

- Sorts by file type only, not by date and not by content.
- The window has a Dark/Light switch. There is no config file, history viewer or keyboard shortcuts.
- The window has no preview step: Start Organizing moves files right away (Undo reverses it).
- The command line and the core logic are tested. The window was not run in the test environment (no display).
- `gui_main.exe` in the repo is an old prebuilt binary that was not rebuilt or verified. Build your own with PyInstaller from `gui_main.py`.

Python 3.9+. No license file is included yet.
