#Requires -Version 5.1
<#
.SYNOPSIS
  If SyncRoot/PUSH_ME.txt exists, pull, commit ledger+audit+原稿, push, delete marker.
.PARAMETER SyncRoot
  帝王龙虾勘录同步目录（含 PUSH_ME.txt、ledger、audit、原稿）。
.PARAMETER RepoRoot
  carbon-silicon-canonical 克隆路径。
.PARAMETER Branch
  推送分支，默认 main。
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$SyncRoot,
    [string]$RepoRoot = $(if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { "E:\carbon-silicon-canonical" }),
    [string]$Branch = "main",
    [string]$CommitMsg = ""
)

$ErrorActionPreference = "Stop"
$Marker = Join-Path $SyncRoot "PUSH_ME.txt"
if (-not (Test-Path $Marker)) {
    Write-Host "No PUSH_ME.txt under $SyncRoot — skip push (勘录未就绪)."
    exit 0
}

$msgFile = @(
    (Join-Path $SyncRoot "COMMIT_MSG.txt"),
    (Join-Path $SyncRoot "HB-COMMIT-MSG.txt")
) | Where-Object { Test-Path $_ } | Select-Object -First 1

$commitMsg = if ($CommitMsg.Trim()) {
    $CommitMsg
} elseif ($msgFile) {
    Get-Content $msgFile -Raw -Encoding UTF8
} else {
    Get-Content $Marker -Raw -Encoding UTF8
}
if (-not $commitMsg.Trim()) {
    $commitMsg = "HB compass-pedal survey batch (see PUSH_ME.txt)"
}

Set-Location $RepoRoot
git fetch origin $Branch
git checkout $Branch
git pull origin $Branch

# Copy/sync: adjust globs to match 帝王龙虾 layout
$auditSrc = Join-Path $SyncRoot "audit"
if (-not (Test-Path $auditSrc)) {
    $auditSrc = Join-Path $SyncRoot "logs"
}
$copyPairs = @(
    @{ Src = Join-Path $SyncRoot "ledger"; Dst = Join-Path $RepoRoot "compass-pedal-ledger" },
    @{ Src = $auditSrc; Dst = Join-Path $RepoRoot "compass-pedal-audit" },
    @{ Src = Join-Path $SyncRoot "原稿"; Dst = Join-Path $RepoRoot "compass-pedal-manuscripts" }
)
foreach ($p in $copyPairs) {
    if (-not (Test-Path $p.Src)) { continue }
    New-Item -ItemType Directory -Force -Path $p.Dst | Out-Null
    robocopy $p.Src $p.Dst /MIR /XD __pycache__ /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed $($p.Src) -> $($p.Dst) exit $LASTEXITCODE" }
}

$addPaths = @("compass-pedal-ledger", "compass-pedal-audit", "compass-pedal-manuscripts") | Where-Object {
    Test-Path (Join-Path $RepoRoot $_)
}
if ($addPaths.Count -gt 0) {
    git add @addPaths
}
$pending = git status --porcelain
if (-not $pending) {
    Write-Warning "Nothing to commit after sync; check SyncRoot layout."
    exit 1
}

$env:GIT_AUTHOR_NAME = "黄清佳 | 碳硅道统"
$env:GIT_AUTHOR_EMAIL = "73703285+liu-hui-ming@users.noreply.github.com"
$env:GIT_COMMITTER_NAME = $env:GIT_AUTHOR_NAME
$env:GIT_COMMITTER_EMAIL = $env:GIT_AUTHOR_EMAIL

git commit -m $commitMsg.Trim()
git push origin $Branch
Remove-Item $Marker -Force
Write-Host "Pushed and removed PUSH_ME.txt"
