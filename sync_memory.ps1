$ErrorActionPreference = 'Stop'

$repoPath = 'D:\code\mynote\codex_memory'

if (-not (Test-Path $repoPath)) {
    Write-Error "记忆仓库路径 $repoPath 不存在，请先确认。"
    exit 1
}

$gitExe = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitExe) {
    Write-Error '未检测到 git，请先安装并加入 PATH。'
    exit 1
}

Set-Location $repoPath

if (-not (Test-Path (Join-Path $repoPath '.git'))) {
    Write-Error '当前记忆目录还不是 Git 仓库，请先 git init 或 git clone 并配置远程。'
    exit 1
}

function Invoke-MemoryShell {
    Write-Host "🐱 已进入记忆仓库：$repoPath"
    Write-Host '📒 编辑完成后输入 exit（或关闭窗口），我会自动帮你保存并推送。'
    powershell -NoExit -Command "Set-Location '$repoPath'; Write-Host '📝 在此窗口更新记忆，输 exit 即可触发自动推送。';"
}

Write-Host '✨ 正在拉取远端记忆...'
git pull --rebase

try {
    Invoke-MemoryShell
}
finally {
    Write-Host '💾 开始同步最新记忆...'
    git add -A

    $pending = git status --porcelain
    if ([string]::IsNullOrWhiteSpace($pending)) {
        Write-Host '✅ 没有新的修改，无需提交。'
    }
    else {
        $commitMessage = "chore(memory): sync $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git commit -m $commitMessage
        Write-Host '🚀 推送到远程...'
        git push
        Write-Host '❤️ 记忆已安全备份，去喝口水吧。'
    }
}
