# SP-3 : récupère la dernière session de l'APK SP3 sur le casque et lance l'analyse (mur + rétroprojection de S1).
# Outil de spike jetable, pas du code mote. Mode d'emploi : README.md de ce dossier.
#
#   powershell -ExecutionPolicy Bypass -File docs\spikes\sp3\run_sp3.ps1                      # référence : le tracking
#   powershell -ExecutionPolicy Bypass -File docs\spikes\sp3\run_sp3.ps1 -Distances 0.52,1.01,2.0,3.03   # au mètre
[CmdletBinding()]
param(
    # Facultatif. Au mètre ruban, mur -> face avant du casque, dans l'ordre, en m avec un point décimal :
    # "0.52,1.01,2.0,3.03". Absent : la référence est le recul mesuré par le tracking du casque.
    # Une chaîne et pas un tableau : « powershell -File » passe la liste en un seul argument.
    [string]$Distances = "",
    [string]$Session = "",                                 # nom YYYYMMDD_hhmmss ; par défaut la plus récente
    [string]$Segments = "",                                # paliers forcés si la détection se trompe : "12-18.5,25-31"
    [string]$Scene = "$HOME\sp0\sessions\20261007_120820", # S1
    [string]$Work = "$HOME\sp3"
)
$ErrorActionPreference = "Continue"
function Say($m) { Write-Host "[sp3] $m" }
$here = $PSScriptRoot
$remote = "/sdcard/Android/data/com.t34400.QuestRealityCapture.sp3/files"
$dist = @($Distances -split "[,;\s]+" | Where-Object { $_ } | ForEach-Object {
    $v = 0.0
    # « 01 » vient d'une virgule décimale (1,01 coupé en 1 et 01) : refusé plutôt que lu de travers
    if ($_ -match '^0\d' -or -not [double]::TryParse($_, [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$v)) {
        Say "distance illisible : « $_ » (mètres, point décimal, séparées par des virgules : 0.52,1.01,2.0,3.03)"; exit 1
    }
    $v })
if ($Distances -and $dist.Count -lt 3) { Say "au moins trois distances (reçu : $($dist -join ' ; '))"; exit 1 }
for ($i = 1; $i -lt $dist.Count; $i++) {
    if ($dist[$i] -le $dist[$i - 1]) { Say "distances non croissantes ($($dist -join ' ; ')) : point décimal, et dans l'ordre de la capture"; exit 1 }
}
if ($Distances) { Say "distances : $($dist -join ' ; ') m" } else { Say "pas de distances au mètre : référence = recul mesuré par le tracking" }
New-Item -ItemType Directory -Force "$Work\sessions" | Out-Null

if (-not $Session) {
    $Session = (adb shell ls $remote | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^\d{8}_\d{6}$' } |
        Sort-Object | Select-Object -Last 1)
    if (-not $Session) { Say "aucune session sur le casque dans $remote (adb devices ?)"; exit 2 }
}
$local = "$Work\sessions\$Session"
if (-not (Test-Path "$local\left_depth_descriptors.csv")) {
    Say "adb pull $Session"
    adb pull "$remote/$Session" "$Work\sessions\"
    if ($LASTEXITCODE -ne 0) { Say "échec de adb pull"; exit 2 }
}
if (-not (Test-Path "$local\depth_readback_timing.csv")) { Say "attention : pas de depth_readback_timing.csv (APK non instrumenté ?)" }

$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uv) { $uv = "$HOME\.local\bin\uv.exe" }
$env:PYTHONUTF8 = "1"
$args_ = @("run", "$here\analyze.py", "--wall", $local, "--out", "$Work\out\$Session")
if ($Distances) { $args_ += @("--distances") + ($dist | ForEach-Object { $_.ToString([Globalization.CultureInfo]::InvariantCulture) }) }
if ($Segments) { $args_ += @("--segments", $Segments) }
if (Test-Path "$Scene\left_depth_descriptors.csv") { $args_ += @("--scene", $Scene) } else { Say "S1 introuvable ($Scene) : pas de rétroprojection" }
& $uv @args_
exit $LASTEXITCODE
