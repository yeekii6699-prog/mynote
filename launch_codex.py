import argparse
import shutil
import subprocess
import sys
from pathlib import Path


STORE_DIR = Path(r"D:\code\store_system_source")
MEMORY_AGENT = Path(r"D:\code\mynote\codex_memory\AGENTS.md")


def ensure_paths():
    missing = [p for p in (STORE_DIR, MEMORY_AGENT) if not p.exists()]
    if missing:
        print("以下路径不存在，请先确认：")
        for path in missing:
            print(f"- {path}")
        sys.exit(1)


def build_cmd_script(codex_command: str) -> str:
    workspace = STORE_DIR
    agent = MEMORY_AGENT
    return (
        f'chcp 65001 >nul && cd /d "{workspace}" && cls && '
        f'echo ================= 记忆索引（AGENTS.md） ================= && '
        f'type "{agent}" && echo. && '
        f'echo 🧠 记忆已唤醒，正在启动 {codex_command} ... && {codex_command}'
    )


def open_terminal(script: str):
    wt = shutil.which("wt")
    if wt:
        subprocess.Popen([wt, "new-tab", "cmd", "/K", script])
    else:
        # 兜底使用 PowerShell
        subprocess.Popen(
            ["powershell", "-NoExit", "-Command", script],
            creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
        )


def main():
    parser = argparse.ArgumentParser(description="唤醒记忆并启动 Codex。")
    parser.add_argument(
        "--search",
        action="store_true",
        help="使用 codex --search 模式启动。",
    )
    args = parser.parse_args()

    ensure_paths()
    codex_cmd = "codex --search" if args.search else "codex"
    script = build_cmd_script(codex_cmd)
    open_terminal(script)
    print("已开启新终端，记忆索引展示完毕后会自动执行 Codex。")


if __name__ == "__main__":
    main()
