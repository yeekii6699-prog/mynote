$ErrorActionPreference = 'Stop'

$repoPath = 'D:\code\mynote\codex_memory'
$snapshotRoot = Join-Path $repoPath 'snapshots'

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

function New-MemorySnapshot {
    param(
        [string]$SourcePath,
        [string]$SnapshotRoot
    )

    if (-not (Test-Path $SnapshotRoot)) {
        New-Item -ItemType Directory -Path $SnapshotRoot | Out-Null
    }

    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $zipPath = Join-Path $SnapshotRoot "snapshot_$timestamp.zip"
    $items = Get-ChildItem -LiteralPath $SourcePath -Force |
        Where-Object { $_.Name -notin @('.git', 'snapshots') }

    if (-not $items) {
        Write-Host '⚠️ 没有可快照的文件，跳过压缩。'
        return
    }

    Compress-Archive -Path ($items | ForEach-Object { $_.FullName }) `
        -DestinationPath $zipPath -Force
    Write-Host "🧳 已生成快照：$zipPath"
}

function Invoke-MemoryShell {
    param([string]$Path)

    Write-Host "🐱 已进入记忆仓库：$Path"
    Write-Host '📒 编辑完成后输入 exit（或关闭窗口），我会自动帮你保存并推送。'
    powershell -NoExit -Command "Set-Location '$Path'; Write-Host '📝 在此窗口更新记忆，输 exit 即可触发自动推送。';"
}

Write-Host '✨ 正在拉取远端记忆...'
git pull --rebase

New-MemorySnapshot -SourcePath $repoPath -SnapshotRoot $snapshotRoot

try {
    Invoke-MemoryShell -Path $repoPath
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
