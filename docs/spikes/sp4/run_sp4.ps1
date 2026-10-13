# SP-4 : récupère les journaux et le MCAP de la sonde, vérifie le MCAP sur PC, affiche les tableaux de SP-4.md.
# Outil de spike jetable, pas du code mote. Mode d'emploi : README.md de ce dossier.
#
#   powershell -ExecutionPolicy Bypass -File docs\spikes\sp4\run_sp4.ps1
[CmdletBinding()]
param([string]$Work = "$HOME\sp4")
$ErrorActionPreference = "Continue"
function Say($m) { Write-Host "[sp4] $m" }
$here = $PSScriptRoot
$remote = "/sdcard/Android/data/com.t34400.QuestRealityCapture.sp4/files/sp4"
$run = "$Work\runs\$(Get-Date -Format yyyyMMdd_HHmmss)"
New-Item -ItemType Directory -Force "$Work\runs" | Out-Null

adb pull $remote $run
if ($LASTEXITCODE -ne 0) { Say "échec de adb pull ($remote) : la sonde a-t-elle tourné ?"; exit 2 }
if (-not (Test-Path "$run\sp4_done.txt")) { Say "attention : pas de sp4_done.txt, la sonde n'est pas allée au bout" }

$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uv) { $uv = "$HOME\.local\bin\uv.exe" }
$env:PYTHONUTF8 = "1"
& $uv run --no-project "$here\analyze_sp4.py" $run
# Un MCAP par phase qui écrit (Nominal, Async) : leurs noms sont dans sp4_phases.jsonl ; d'anciens passages peuvent
# en avoir laissé d'autres dans le dossier.
$names = @(Get-Content "$run\sp4_phases.jsonl" | ForEach-Object {
    try { $j = $_ | ConvertFrom-Json } catch { return }
    if ($j.core -and $j.core.mcap) { [pscustomobject]@{ Phase = $j.phase; File = Split-Path $j.core.mcap -Leaf } }
})
if (-not $names) { Say "aucun MCAP annoncé dans sp4_phases.jsonl"; exit 3 }
foreach ($n in $names) {
    $file = "$run\$($n.File)"
    ""
    "### MCAP de la phase $($n.Phase), écrit sur le casque, relu sur PC"
    ""
    if (-not (Test-Path $file)) { Say "$($n.File) absent de $run"; continue }
    & $uv run "$here\verify_mcap.py" $file --out "$run\first_pair_$($n.Phase)"
}
Say "journaux, MCAP et première paire (JPEG) de chaque phase dans $run"
