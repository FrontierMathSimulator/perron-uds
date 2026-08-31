[CmdletBinding()]
param(
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $Python) {
    $venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        $Python = $venvPython
    } else {
        $command = Get-Command python -ErrorAction SilentlyContinue
        if (-not $command) { throw "Python 3.11 or newer is required." }
        $Python = $command.Source
    }
}

& $Python (Join-Path $repoRoot "reproducibility\reproduce.py")
if ($LASTEXITCODE -ne 0) { throw "Reproduction failed." }

