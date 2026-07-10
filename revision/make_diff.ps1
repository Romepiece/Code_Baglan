# Builds the marked-up diff PDF: original submission vs revised manuscript.
# Output: revision/diff/sn-article-diff.pdf
#   - deleted text: red, struck through
#   - added text:   blue, underlined
# Run from anywhere:  powershell -File revision\make_diff.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot   # repo root (revision/..)

$orig = Join-Path $root "journal_submission_package\sn-article-eng.tex"
$new  = Join-Path $root "revision\manuscript\sn-article-eng.tex"
$diffDir = Join-Path $root "revision\diff"
$diffTex = Join-Path $diffDir "sn-article-diff.tex"

$perl      = "C:\Strawberry\perl\bin\perl.exe"
$latexdiff = "$env:LOCALAPPDATA\Programs\MiKTeX\scripts\latexdiff\latexdiff"

New-Item -ItemType Directory -Force $diffDir | Out-Null

# 1. latexdiff (MiKTeX wrapper picks the wrong perl, so call the script directly)
& $perl $latexdiff --encoding=utf8 $orig $new | Out-File -Encoding utf8 $diffTex
if ($LASTEXITCODE -ne 0) { throw "latexdiff failed" }

# 2. Class/style/bib/figures needed for compilation
Copy-Item (Join-Path $root "revision\manuscript\sn-jnl.cls")          $diffDir -Force
Copy-Item (Join-Path $root "revision\manuscript\sn-mathphys-ay.bst")  $diffDir -Force
Copy-Item (Join-Path $root "revision\manuscript\sn-bibliography.bib") $diffDir -Force
Copy-Item (Join-Path $root "revision\manuscript\figures")             $diffDir -Recurse -Force

# 3. Full LaTeX cycle
Push-Location $diffDir
try {
    pdflatex -interaction=nonstopmode sn-article-diff.tex | Out-Null
    bibtex   sn-article-diff | Out-Null
    pdflatex -interaction=nonstopmode sn-article-diff.tex | Out-Null
    pdflatex -interaction=nonstopmode sn-article-diff.tex | Out-Null
} finally { Pop-Location }

if (Test-Path (Join-Path $diffDir "sn-article-diff.pdf")) {
    Write-Host "OK: $((Join-Path $diffDir 'sn-article-diff.pdf'))"
} else {
    throw "diff PDF was not produced - check logs in revision\diff\"
}
