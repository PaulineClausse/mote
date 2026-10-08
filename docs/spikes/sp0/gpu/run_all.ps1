# SP-0 : SfM REF COLMAP sur le PC NVIDIA, toutes les sessions, en une commande.
# Outil de spike jetable, pas du code mote. Mode d'emploi : README.md de ce dossier.
#
#   powershell -ExecutionPolicy Bypass -File run_all.ps1
#
# Installe ce qui manque (uv, Python 3.11, COLMAP 4.2.1 CUDA, SRC-3), puis lance pipeline.py
# sur chaque session de -Data. Relancer la même commande reprend là où ça s'est arrêté.
[CmdletBinding()]
param(
    [string]$Data = "$HOME\sp0\sessions",   # sessions copiées du casque (adb pull) ou exports SRC-3
    [string]$Work = "$HOME\sp0\work",       # sorties, un dossier par session
    [string]$Tools = "$HOME\sp0\tools",     # outils téléchargés (COLMAP, SRC-3, venv)
    [int]$Interval = 2,                     # sous-échantillonnage de l'export SRC-3 (S0, S1 : 2)
    [ValidateSet("exhaustive", "sequential")][string]$Matcher = "exhaustive",
    [string[]]$Only,                        # ne traiter que ces sessions (noms de dossier)
    [switch]$AllowCpu,                      # accepter un COLMAP sans CUDA
    [switch]$DryRun                         # afficher les commandes sans rien exécuter
)
$ErrorActionPreference = "Continue"   # codes de sortie verifies a la main : PS 5.1 transforme le stderr natif en erreurs
function Say($m) { Write-Host "[sp0-gpu] $m" }

# 1. uv (gestionnaire Python), dans le profil utilisateur, sans droits administrateur
$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uv -and (Test-Path "$HOME\.local\bin\uv.exe")) { $uv = "$HOME\.local\bin\uv.exe" }
if (-not $uv) {
    Say "installation de uv"
    powershell -NoProfile -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $uv = "$HOME\.local\bin\uv.exe"
    if (-not (Test-Path $uv)) { throw "uv introuvable apres installation ($uv)" }
}

# 2. venv Python 3.11 dédié (uv télécharge Python s'il manque), avec numpy
$py = "$Tools\venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Say "creation du venv Python 3.11 dans $Tools\venv"
    New-Item -ItemType Directory -Force $Tools | Out-Null
    & $uv venv --python 3.11 "$Tools\venv"
    if ($LASTEXITCODE -ne 0) { throw "uv venv a echoue" }
}
& $py -c "import numpy" 2>$null
if ($LASTEXITCODE -ne 0) {
    & $uv pip install --python $py numpy
    if ($LASTEXITCODE -ne 0) { throw "installation de numpy echouee" }
}

# 3. le reste (COLMAP, SRC-3, export, SfM, alignement, résumé) : pipeline.py
$a = @("$PSScriptRoot\pipeline.py", "--data", $Data, "--work", $Work, "--tools", $Tools,
       "--interval", "$Interval", "--matcher", $Matcher)
if ($Only) { $a += @("--only") + $Only }
if ($AllowCpu) { $a += "--allow-cpu" }
if ($DryRun) { $a += "--dry-run" }
$env:UV = $uv
& $py @a
exit $LASTEXITCODE
