param([Parameter(Mandatory=$true)][ValidateSet('setup','test','check','seed','run','evaluate','real-eval','security','benchmark')][string]$Target)
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$runner = Join-Path $PSScriptRoot 'scripts/tasks.py'
if (Test-Path -LiteralPath $python) {
    & $python $runner $Target
} else {
    & py -3.11 $runner $Target
}
exit $LASTEXITCODE
