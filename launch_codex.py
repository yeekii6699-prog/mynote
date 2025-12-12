import subprocess
import sys
from pathlib import Path


STORE_DIR = Path(r"D:\code\store_system_source")
MEMORY_DIR = Path(r"D:\code\mynote\codex_memory")
NOTES_FILE = MEMORY_DIR / "NOTES.md"
MODULES_DIR = MEMORY_DIR / "modules"


def ensure_paths():
    missing = []
    for path in [STORE_DIR, MEMORY_DIR, NOTES_FILE, MODULES_DIR]:
        if not path.exists():
            missing.append(str(path))
    if missing:
        print("以下路径不存在，请先确认：")
        for item in missing:
            print(f"- {item}")
        sys.exit(1)


def build_powershell_script() -> str:
    notes = NOTES_FILE.as_posix()
    modules = MODULES_DIR.as_posix()
    workspace = STORE_DIR.as_posix()
    ps_script = f"""
$ErrorActionPreference = 'Stop'
Set-Location -Path "{workspace}"
Write-Host "================ 记忆索引（NOTES.md） ================" -ForegroundColor Cyan
Get-Content -Path "{notes}"
Write-Host "`n---------------- 模块列表 ----------------" -ForegroundColor Yellow
Get-ChildItem -Path "{modules}" -Filter "*.md" | ForEach-Object {{ Write-Host ("- " + $_.Name) }}
Write-Host "`n🧠 记忆已唤醒，正在启动 Codex CLI..." -ForegroundColor Green
codex
"""
    return ps_script


def open_new_terminal(script: str):
    creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    subprocess.Popen(
        [
            "powershell",
            "-NoExit",
            "-Command",
            script,
        ],
        creationflags=creation_flags,
    )


def main():
    ensure_paths()
    ps_script = build_powershell_script()
    open_new_terminal(ps_script)
    print("已开启新终端并唤醒记忆，窗口中会自动显示 NOTES 和模块列表后启动 codex。")


if __name__ == "__main__":
    main()
