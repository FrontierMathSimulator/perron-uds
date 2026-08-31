[CmdletBinding()]
param(
    [string]$Quarto = "",
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $repoRoot
try {
    if (-not $Quarto) {
        $portable = Join-Path $repoRoot ".tools\quarto-1.10.18\bin\quarto.exe"
        if (Test-Path -LiteralPath $portable) {
            $Quarto = $portable
        } else {
            $command = Get-Command quarto -ErrorAction SilentlyContinue
            if (-not $command) {
                throw "Quarto 1.10.18 is required. Install it or pass -Quarto <path>."
            }
            $Quarto = $command.Source
        }
    }

    if (-not $Python) {
        $venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
        if (Test-Path -LiteralPath $venvPython) {
            $Python = $venvPython
        } else {
            $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
            if (-not $pythonCommand) {
                throw "Python 3.11 or newer is required to finalize the publication."
            }
            $Python = $pythonCommand.Source
        }
    }

    $version = (& $Quarto --version).Trim()
    if ($version -ne "1.10.18") {
        Write-Warning "The reproducibility baseline uses Quarto 1.10.18; found $version."
    }

    New-Item -ItemType Directory -Force -Path "docs", "paper" | Out-Null
    & $Quarto render paper/manuscript.qmd --to html --output-dir docs --output index.html
    if ($LASTEXITCODE -ne 0) { throw "HTML render failed." }

    $generatedAssets = "docs\paper\manuscript_files"
    if (-not (Test-Path -LiteralPath $generatedAssets)) {
        throw "Quarto HTML assets were not generated at $generatedAssets."
    }
    New-Item -ItemType Directory -Force -Path "docs\manuscript_files" | Out-Null
    Copy-Item -Path "$generatedAssets\*" -Destination "docs\manuscript_files" -Recurse -Force
    Copy-Item -LiteralPath "paper\paper.css" -Destination "docs\paper.css" -Force

    Remove-Item -LiteralPath "main.pdf", "paper\main.pdf" -Force -ErrorAction SilentlyContinue
    & $Quarto render paper/manuscript.qmd --to typst --output main.pdf
    if ($LASTEXITCODE -ne 0) { throw "PDF render failed." }
    if (-not (Test-Path -LiteralPath "main.pdf")) {
        throw "Typst PDF was not generated at main.pdf."
    }
    Move-Item -LiteralPath "main.pdf" -Destination "paper\main.pdf" -Force

    & $Quarto render paper/manuscript.qmd --to gfm --output-dir docs --output paper.md
    if ($LASTEXITCODE -ne 0) { throw "Markdown render failed." }

    Copy-Item -LiteralPath "paper\main.pdf" -Destination "docs\paper.pdf" -Force
    & $Python "scripts\finalize-publication.py"
    if ($LASTEXITCODE -ne 0) { throw "Publication finalization failed." }

    Write-Output "Built docs/index.html, paper/main.pdf, docs/paper.pdf, and docs/paper.md."
} finally {
    Pop-Location
}
