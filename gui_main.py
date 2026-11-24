import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.organizer import (CATEGORY_FOLDERS, build_organization_plan, execute_organization,
                            history_count, human_size, summarize_plan, undo_last)
from core.scanner import scan_files

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
NO_FOLDER = "No folder selected..."


class SmartOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart Organizer Pro - by Mahamed Yasser")
        self.geometry("760x600")
        self.minsize(700, 560)
        try:
            self.iconbitmap("icon.ico")
        except Exception:
            pass
        self.plan = None

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(pady=(18, 4), padx=24, fill="x")
        ctk.CTkLabel(head, text="Smart Organizer", font=("Segoe UI", 28, "bold")).pack(side="left")
        self.theme_menu = ctk.CTkOptionMenu(head, values=["Dark", "Light"], command=ctk.set_appearance_mode, width=90)
        self.theme_menu.pack(side="right")

        main = ctk.CTkFrame(self)
        main.pack(pady=8, padx=24, fill="both", expand=True)
        main.grid_columnconfigure(0, weight=1)

        self.path_var = ctk.StringVar(value=NO_FOLDER)
        ctk.CTkEntry(main, textvariable=self.path_var).grid(row=0, column=0, padx=(16, 8), pady=(16, 8), sticky="ew")
        ctk.CTkButton(main, text="Browse", width=90, command=self.browse_folder).grid(row=0, column=1, padx=(0, 16), pady=(16, 8))

        opts = ctk.CTkFrame(main, fg_color="transparent")
        opts.grid(row=1, column=0, columnspan=2, sticky="w", padx=16)
        self.recursive = ctk.BooleanVar(value=False)
        self.by_date = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(opts, text="Include sub-folders", variable=self.recursive, command=self.preview).pack(side="left", padx=(0, 20))
        ctk.CTkSwitch(opts, text="Group by month", variable=self.by_date, command=self.preview).pack(side="left")

        self.summary = ctk.CTkTextbox(main, height=170, font=("Consolas", 13))
        self.summary.grid(row=2, column=0, columnspan=2, padx=16, pady=10, sticky="nsew")
        main.grid_rowconfigure(2, weight=1)

        btns = ctk.CTkFrame(main, fg_color="transparent")
        btns.grid(row=3, column=0, columnspan=2, pady=4)
        ctk.CTkButton(btns, text="Preview", width=110, command=self.preview).pack(side="left", padx=6)
        self.organize_btn = ctk.CTkButton(btns, text="Organize", width=130, fg_color="#2ecc71", hover_color="#27ae60",
                                          font=("Segoe UI", 15, "bold"), command=self.run_organizer, state="disabled", text_color_disabled=("gray40", "gray65"))
        self.organize_btn.pack(side="left", padx=6)
        self.undo_btn = ctk.CTkButton(btns, text="Undo last run", width=130, fg_color="#e74c3c", hover_color="#c0392b",
                                      command=self.run_undo, state="disabled", text_color_disabled=("gray40", "gray65"))
        self.undo_btn.pack(side="left", padx=6)

        self.progress = ctk.CTkProgressBar(main)
        self.progress.set(0)
        self.progress.grid(row=4, column=0, columnspan=2, padx=16, pady=(10, 4), sticky="ew")
        self.status = ctk.CTkLabel(main, text="Choose a folder to see what would change.", text_color="gray")
        self.status.grid(row=5, column=0, columnspan=2, pady=(0, 14))

        ctk.CTkLabel(self, text="Nothing moves until you press Organize. The last 20 runs in a folder can be undone.",
                     font=("Segoe UI", 12, "italic"), text_color="gray").pack(side="bottom", pady=10)

        self.preview()  # shows the start instructions

    # ---- helpers (kept free of dialogs so they can be tested) ----
    def folder(self):
        v = self.path_var.get()
        return None if v == NO_FOLDER or not Path(v).is_dir() else Path(v)

    def set_text(self, text):
        self.summary.configure(state="normal")
        self.summary.delete("1.0", "end")
        self.summary.insert("1.0", text)
        self.summary.configure(state="disabled")

    def refresh_undo(self):
        f = self.folder()
        n = history_count(f) if f else 0
        self.undo_btn.configure(state="normal" if n else "disabled", text=f"Undo last run ({n})" if n else "Undo last run",
                                fg_color="#e74c3c" if n else ("gray75", "gray30"))

    def browse_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.path_var.set(d)
            self.preview()

    def preview(self):
        f = self.folder()
        self.refresh_undo()
        self.plan = None
        self.organize_btn.configure(state="disabled", fg_color=("gray75", "gray30"))
        if not f:
            self.set_text("\n  1. Press Browse and pick a folder.\n  2. Check the preview: nothing has moved yet.\n  3. Press Organize. Undo is available afterwards.")
            return
        files = scan_files(f, recursive=self.recursive.get(), skip_dirs=CATEGORY_FOLDERS)
        self.plan = build_organization_plan(files, f, by_date=self.by_date.get())
        if not self.plan:
            self.set_text("Nothing to organize in this folder.")
            self.status.configure(text="Already tidy.")
            return
        rows = summarize_plan(self.plan, f)
        lines = [f"{'Destination':<26}{'Files':>6}{'Size':>12}", "-" * 44]
        lines += [f"{n:<26}{c:>6}{human_size(s):>12}" for n, c, s in rows]
        lines += ["-" * 44, f"{'Total':<26}{sum(r[1] for r in rows):>6}{human_size(sum(r[2] for r in rows)):>12}"]
        self.set_text("\n".join(lines))
        self.status.configure(text="Preview ready. Press Organize to move the files.")
        self.organize_btn.configure(state="normal", fg_color="#2ecc71")

    def run_organizer(self):
        f = self.folder()
        if not f or not self.plan:
            return
        self.organize_btn.configure(state="disabled")
        errors = []
        moved_rows = summarize_plan(self.plan, f)

        state = {"done": 0, "total": 1, "n": None}

        def work():  # worker thread: never touches widgets, only plain data
            state["n"] = execute_organization(
                self.plan, f, errors=errors,
                progress=lambda d, t: state.update(done=d, total=t))

        def poll():  # main thread: update the bar, finish when the worker is done
            self.progress.set(state["done"] / max(state["total"], 1))
            if state["n"] is None:
                self.after(50, poll)
            else:
                self.finish(state["n"], errors, moved_rows)
        threading.Thread(target=work, daemon=True).start()
        poll()

    def finish(self, n, errors, moved_rows=()):
        self.preview()
        if moved_rows:
            lines = ["Moved:"] + [f"  {name:<24}{c:>5} {'file' if c == 1 else 'files'}" for name, c, _ in moved_rows]
            self.set_text("\n".join(lines))
        self.progress.set(1)
        msg = f"Moved {n} {'file' if n == 1 else 'files'}. Use Undo to bring them back."
        if errors:
            msg = f"Moved {n} files, {len(errors)} skipped."
            self.set_text("Skipped:\n" + "\n".join(errors))
        self.status.configure(text=msg)

    def run_undo(self):
        f = self.folder()
        if not f:
            return
        n = undo_last(f)
        self.progress.set(0)
        self.preview()
        self.status.configure(text=f"Restored {n} files.")


if __name__ == "__main__":
    SmartOrganizerApp().mainloop()
