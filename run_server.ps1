<#
.SYNOPSIS
    Starts the AI CLI MCP Server on Windows.

.DESCRIPTION
    Launches the production-ready Model Context Protocol (MCP) server for OpenAI Codex
    and Google Antigravity CLIs. Detects local virtual environments (.venv, venv, env)
    or system Python 3.10+, and ensures unbuffered stdio transport.

.PARAMETER Status
    Performs a health check and prints host CLI binary versions, paths, and statuses.

.PARAMETER Yolo
    Enables YOLO mode (dangerously bypass approvals/permissions). Defaults to true if not set.

.EXAMPLE
    .\run_server.ps1
    Starts the MCP server on stdio transport (used by Claude Desktop, Cursor, Antigravity).

.EXAMPLE
    .\run_server.ps1 -Status
    Prints the health status of Codex and Antigravity CLIs.

.EXAMPLE
    .\run_server.ps1 -Yolo:$false
    Starts the server with autonomous YOLO mode disabled.
#>

[CmdletBinding()]
param(
    [switch]$Status,
    [switch]$Yolo,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

# Set YOLO mode if explicitly specified
if ($PSBoundParameters.ContainsKey('Yolo')) {
    if ($Yolo) {
        $env:CLI_YOLO_MODE = "true"
    } else {
        $env:CLI_YOLO_MODE = "false"
    }
}

# 1. Search for virtual environments first
$candidatePythons = @(
    (Join-Path $ScriptDir ".venv\Scripts\python.exe"),
    (Join-Path $ScriptDir "venv\Scripts\python.exe"),
    (Join-Path $ScriptDir "env\Scripts\python.exe")
)

$pythonExe = $null

foreach ($candidate in $candidatePythons) {
    if (Test-Path -Path $candidate -PathType Leaf) {
        $pythonExe = $candidate
        break
    }
}

# 2. Search for Python on PATH (excluding WindowsApps redirector)
if (-not $pythonExe) {
    $pyCommands = Get-Command python -All -ErrorAction SilentlyContinue
    foreach ($cmd in $pyCommands) {
        if ($cmd.Source -notlike "*WindowsApps*") {
            $pythonExe = $cmd.Source
            break
        }
    }
    # Fallback to any python found if none outside WindowsApps
    if (-not $pythonExe -and $pyCommands) {
        $pythonExe = $pyCommands[0].Source
    }
}

# 3. Search for Python Launcher (py.exe)
if (-not $pythonExe) {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $pythonExe = $pyLauncher.Source
    }
}

if (-not $pythonExe) {
    [Console]::Error.WriteLine("[ERROR] Python 3.10+ was not found on PATH or in a virtual environment (.venv / venv).")
    [Console]::Error.WriteLine("[ERROR] Please install Python 3.10+ from https://www.python.org/ or add it to PATH.")
    exit 1
}

# If -Status switch was passed, run health check
if ($Status) {
    & $pythonExe -c "import asyncio, server; print(asyncio.run(server.cli_status()))"
    exit $LASTEXITCODE
}

# Run MCP server in unbuffered mode (-u)
$serverScript = Join-Path $ScriptDir "server.py"

if ($RemainingArgs) {
    & $pythonExe -u $serverScript @RemainingArgs
} else {
    & $pythonExe -u $serverScript
}

exit $LASTEXITCODE
