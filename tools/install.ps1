<#
.SYNOPSIS
  Sfumato installer for Windows (Windows PowerShell 5.1+ / PowerShell 7).

.DESCRIPTION
  Installs skill/sfumato into the skill directories of supported agents:
    claude -> ~\.claude\skills\sfumato  (+ ~\.claude\commands\sfm.md)
    agy    -> ~\.gemini\config\skills\sfumato
    codex  -> ~\.codex\skills\sfumato
  -Target auto (default) installs for every agent whose config dir exists,
  falling back to claude. Uses the local checkout when skill\sfumato sits next
  to this script (or one level up); otherwise downloads the GitHub zip.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\install.ps1 -Target all
.EXAMPLE
  irm https://raw.githubusercontent.com/Excelsus4/sfumato/main/tools/install.ps1 | iex
.EXAMPLE
  & ([scriptblock]::Create((irm https://raw.githubusercontent.com/Excelsus4/sfumato/main/tools/install.ps1))) -Target all -DryRun
#>
[CmdletBinding()]
param(
    [ValidateSet('claude', 'agy', 'codex', 'all', 'auto')]
    [string]$Target = 'auto',
    [switch]$DryRun,
    [string]$HomeDir = '',
    [string]$Source = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoZip = 'https://github.com/Excelsus4/sfumato/archive/refs/heads/main.zip'

if (-not $HomeDir) {
    $HomeDir = $env:USERPROFILE
    if (-not $HomeDir) { $HomeDir = $HOME }
}
if (-not $HomeDir) { throw 'Cannot determine home directory; pass -HomeDir.' }

function Write-Step([string]$Message) { Write-Host $Message }

function Test-SkillRoot([string]$Dir) {
    if (-not $Dir) { return $false }
    return (Test-Path -LiteralPath (Join-Path $Dir 'skill\sfumato\SKILL.md') -PathType Leaf)
}

$tmpDir = $null
try {
    # --- locate source ---------------------------------------------------------
    if (-not $Source) {
        $scriptDir = $null
        if ($PSCommandPath) { $scriptDir = Split-Path -Parent $PSCommandPath }
        elseif ($MyInvocation.MyCommand.Path) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
        if ($scriptDir) {
            foreach ($cand in @($scriptDir, (Split-Path -Parent $scriptDir))) {
                if ($cand -and (Test-SkillRoot $cand)) { $Source = (Resolve-Path -LiteralPath $cand).Path; break }
            }
        }
    }
    elseif (-not (Test-SkillRoot $Source)) {
        throw "skill\sfumato\SKILL.md not found under '$Source'."
    }

    $downloaded = $false
    if (-not $Source) {
        Write-Step "Local checkout not found; downloading $RepoZip"
        if ($DryRun) {
            Write-Step "[dry-run] would download and extract $RepoZip"
            $Source = '<downloaded-archive>'
            $downloaded = $true
        }
        else {
            try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch { }
            $tmpDir = Join-Path ([IO.Path]::GetTempPath()) ('sfumato-' + [Guid]::NewGuid().ToString('N'))
            New-Item -ItemType Directory -Path $tmpDir | Out-Null
            $zipPath = Join-Path $tmpDir 'src.zip'
            Invoke-WebRequest -Uri $RepoZip -OutFile $zipPath -UseBasicParsing
            Expand-Archive -LiteralPath $zipPath -DestinationPath $tmpDir -Force
            foreach ($d in @(Get-ChildItem -LiteralPath $tmpDir -Directory)) {
                if (Test-SkillRoot $d.FullName) { $Source = $d.FullName; break }
            }
            if (-not $Source) { throw 'skill\sfumato not found in downloaded archive.' }
            $downloaded = $true
        }
    }
    Write-Step "Source: $Source"

    # --- resolve targets -------------------------------------------------------
    $targets = @()
    switch ($Target) {
        'all' { $targets = @('claude', 'agy', 'codex') }
        'auto' {
            if (Test-Path -LiteralPath (Join-Path $HomeDir '.claude') -PathType Container) { $targets += 'claude' }
            if (Test-Path -LiteralPath (Join-Path $HomeDir '.gemini') -PathType Container) { $targets += 'agy' }
            if (Test-Path -LiteralPath (Join-Path $HomeDir '.codex') -PathType Container) { $targets += 'codex' }
            if ($targets.Count -eq 0) {
                Write-Step 'No agent config dirs detected; defaulting to claude'
                $targets = @('claude')
            }
        }
        default { $targets = @($Target) }
    }

    $destMap = @{
        'claude' = Join-Path $HomeDir '.claude\skills\sfumato'
        'agy'    = Join-Path $HomeDir '.gemini\config\skills\sfumato'
        'codex'  = Join-Path $HomeDir '.codex\skills\sfumato'
    }

    foreach ($t in $targets) {
        $dest = $destMap[$t]
        Write-Step "[$t] skill -> $dest"
        if ($DryRun) {
            if (Test-Path -LiteralPath $dest) { Write-Step "[dry-run] would replace existing $dest" }
            Write-Step "[dry-run] would copy $Source\skill\sfumato\* -> $dest"
        }
        else {
            if (Test-Path -LiteralPath $dest) {
                $item = Get-Item -LiteralPath $dest -Force
                if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                    # Junction/symlink: remove the link only, never the link target's contents.
                    [IO.Directory]::Delete($dest)
                }
                else {
                    Remove-Item -LiteralPath $dest -Recurse -Force
                }
            }
            New-Item -ItemType Directory -Path $dest -Force | Out-Null
            Copy-Item -Path (Join-Path $Source 'skill\sfumato\*') -Destination $dest -Recurse -Force
        }

        if ($t -eq 'claude') {
            $cmdSrc = Join-Path $Source 'commands\sfm.md'
            $cmdDir = Join-Path $HomeDir '.claude\commands'
            $cmdDest = Join-Path $cmdDir 'sfm.md'
            if ($downloaded -or (Test-Path -LiteralPath $cmdSrc -PathType Leaf)) {
                Write-Step "[claude] command -> $cmdDest"
                if ($DryRun) { Write-Step "[dry-run] would copy $cmdSrc -> $cmdDest" }
                else {
                    New-Item -ItemType Directory -Path $cmdDir -Force | Out-Null
                    Copy-Item -LiteralPath $cmdSrc -Destination $cmdDest -Force
                }
            }
            else {
                Write-Step "[claude] warning: $cmdSrc not found; skipping /sfm command"
            }
        }
    }

    if ($DryRun) { Write-Step 'Dry run complete. No files were changed.' }
    else { Write-Step ('Sfumato installed for: ' + ($targets -join ', ')) }
}
finally {
    if ($tmpDir -and (Test-Path -LiteralPath $tmpDir)) { Remove-Item -LiteralPath $tmpDir -Recurse -Force -ErrorAction SilentlyContinue }
}
