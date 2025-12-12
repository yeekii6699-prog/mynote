import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText


BASE_DIR = Path(__file__).resolve().parent
MEMORY_DIR = BASE_DIR / "codex_memory"
AGENT_PATH = MEMORY_DIR / "AGENTS.md"


def ensure_paths():
    missing = [p for p in (MEMORY_DIR, AGENT_PATH) if not p.exists()]
    if missing:
        messagebox.showerror(
            "路径不存在",
            "请先确认以下路径已创建：\n" + "\n".join(str(p) for p in missing),
        )
        sys.exit(1)


def git_pull():
    try:
        result = subprocess.run(
            ["git", "-C", str(MEMORY_DIR), "pull", "--rebase"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or "已是最新。"
    except FileNotFoundError:
        return "未检测到 git，可先安装或跳过拉取。"
    except subprocess.CalledProcessError as exc:
        return f"git pull 失败：{exc.stderr.strip() or exc.stdout.strip()}"


def load_sections():
    text = AGENT_PATH.read_text(encoding="utf-8")
    sections = [("全文（AGENTS.md）", text)]
    current_title = None
    buffer: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title:
                sections.append((current_title, "\n".join(buffer).strip()))
            current_title = line[3:].strip()
            buffer = []
        else:
            if current_title:
                buffer.append(line)

    if current_title:
        sections.append((current_title, "\n".join(buffer).strip()))

    return sections


class MemoryViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codex 记忆浏览器")
        self.geometry("960x600")
        self.sections = load_sections()
        self.create_widgets()
        self.status_var.set("正在拉取远端记忆…")
        self.after(100, self.refresh_from_git)

    def create_widgets(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self)
        sidebar.grid(row=0, column=0, sticky="ns")
        ttk.Label(sidebar, text="记忆章节").pack(padx=10, pady=(10, 4))

        self.listbox = tk.Listbox(sidebar, width=32, height=25)
        self.listbox.pack(padx=10, pady=4, fill="y")
        for idx, (label, _) in enumerate(self.sections):
            self.listbox.insert(idx, label)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        ttk.Button(sidebar, text="用记事本打开", command=self.open_agent).pack(
            padx=10, pady=(6, 0), fill="x"
        )
        ttk.Button(sidebar, text="重新载入章节", command=self.reload_sections).pack(
            padx=10, pady=(6, 0), fill="x"
        )

        self.text = ScrolledText(self, wrap="word", font=("Consolas", 11))
        self.text.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.text.insert("1.0", "请选择左侧章节以阅读内容。")
        self.text.configure(state="disabled")

        status_frame = ttk.Frame(self)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, anchor="w").grid(
            row=0, column=0, sticky="ew", padx=10, pady=6
        )

    def refresh_from_git(self):
        msg = git_pull()
        self.status_var.set(msg)

    def on_select(self, _event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        label, content = self.sections[idx]
        if not content:
            content = "(本章节暂无详细内容)"
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", f"# {label}\n\n{content}")
        self.text.configure(state="disabled")
        self.status_var.set(f"已加载：{label}")

    def open_agent(self):
        try:
            os.startfile(AGENT_PATH)  # type: ignore[attr-defined]
        except Exception:
            messagebox.showinfo("提醒", f"请使用编辑器打开：{AGENT_PATH}")
        else:
            self.status_var.set("已调用系统默认程序打开 AGENTS.md。")

    def reload_sections(self):
        self.sections = load_sections()
        self.listbox.delete(0, "end")
        for idx, (label, _) in enumerate(self.sections):
            self.listbox.insert(idx, label)
        self.status_var.set("章节列表已刷新。")


if __name__ == "__main__":
    ensure_paths()
    app = MemoryViewer()
    app.mainloop()
