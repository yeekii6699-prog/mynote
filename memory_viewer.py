import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import webbrowser


BASE_DIR = Path(__file__).resolve().parent
MEMORY_DIR = BASE_DIR / "codex_memory"
MODULES_DIR = MEMORY_DIR / "modules"


def ensure_paths():
    if not MEMORY_DIR.exists():
        messagebox.showerror("路径不存在", f"未找到记忆目录：{MEMORY_DIR}")
        sys.exit(1)
    if not MODULES_DIR.exists():
        messagebox.showerror("路径不存在", f"未找到模块目录：{MODULES_DIR}")
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


def list_memory_files():
    files = [("索引 / 说明", MEMORY_DIR / "NOTES.md")]
    files += [
        (f"模块 · {path.stem}", path)
        for path in sorted(MODULES_DIR.glob("*.md"))
    ]
    return files


class MemoryViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codex 记忆浏览器")
        self.geometry("960x600")
        self.files = list_memory_files()
        self.create_widgets()
        self.status_var.set("正在拉取远端记忆...")
        self.after(100, self.refresh_from_git)

    def create_widgets(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="ns")

        ttk.Label(left_frame, text="记忆模块").pack(padx=10, pady=(10, 4))
        self.listbox = tk.Listbox(left_frame, width=28, height=25)
        self.listbox.pack(padx=10, pady=4, fill="y", expand=False)
        for idx, (label, _) in enumerate(self.files):
            self.listbox.insert(idx, label)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(padx=10, pady=10, fill="x")
        ttk.Button(btn_frame, text="打开文件", command=self.open_current_file).pack(fill="x")
        ttk.Button(btn_frame, text="刷新列表", command=self.reload_files).pack(fill="x", pady=(6, 0))

        self.text = ScrolledText(self, wrap="word", font=("Consolas", 11))
        self.text.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.text.insert("1.0", "请选择左侧模块以查看内容。")
        self.text.configure(state="disabled")

        status_frame = ttk.Frame(self)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, anchor="w").grid(
            row=0, column=0, sticky="ew", padx=10, pady=6
        )
        ttk.Button(status_frame, text="查看索引说明", command=self.open_architecture).grid(
            row=0, column=1, padx=10
        )

    def refresh_from_git(self):
        msg = git_pull()
        self.status_var.set(msg)

    def on_select(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        _, path = self.files[idx]
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as exc:
            messagebox.showerror("读取失败", f"无法读取 {path}：{exc}")
            return
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.configure(state="disabled")
        self.status_var.set(f"已加载：{path.name}")

    def open_current_file(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个模块。")
            return
        path = self.files[selection[0]][1]
        try:
            webbrowser.open(path.as_uri())
            self.status_var.set(f"已在默认程序中打开：{path.name}")
        except Exception as exc:
            messagebox.showerror("打开失败", str(exc))

    def reload_files(self):
        self.files = list_memory_files()
        self.listbox.delete(0, "end")
        for idx, (label, _) in enumerate(self.files):
            self.listbox.insert(idx, label)
        self.status_var.set("已刷新文件列表。")

    def open_architecture(self):
        arch_path = MEMORY_DIR / "ARCHITECTURE.md"
        if not arch_path.exists():
            messagebox.showinfo("提示", "尚未创建 ARCHITECTURE.md。")
            return
        webbrowser.open(arch_path.as_uri())


if __name__ == "__main__":
    ensure_paths()
    app = MemoryViewer()
    app.mainloop()
