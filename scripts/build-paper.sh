#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

quarto_bin="${QUARTO_BIN:-quarto}"
python_bin="${PYTHON_BIN:-$repo_root/.venv/bin/python}"
if [[ ! -x "$python_bin" ]]; then
  python_bin="${PYTHON_BIN:-python3}"
fi
version="$($quarto_bin --version)"
if [[ "$version" != "1.10.18" ]]; then
  echo "warning: reproducibility baseline is Quarto 1.10.18; found $version" >&2
fi

mkdir -p docs paper
"$quarto_bin" render paper/manuscript.qmd --to html --output-dir docs --output index.html
test -d docs/paper/manuscript_files
mkdir -p docs/manuscript_files
cp -R docs/paper/manuscript_files/. docs/manuscript_files/
cp paper/paper.css docs/paper.css
"$quarto_bin" render paper/manuscript.qmd --to typst --output-dir paper --output main.pdf
"$quarto_bin" render paper/manuscript.qmd --to gfm --output-dir docs --output paper.md
cp paper/main.pdf docs/paper.pdf
"$python_bin" scripts/finalize-publication.py

echo "Built docs/index.html, paper/main.pdf, docs/paper.pdf, and docs/paper.md."
