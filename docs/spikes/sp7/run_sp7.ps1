# SP-7 : initialisation par la profondeur du casque, sur le PC NVIDIA, en une commande. Pas de casque.
# Outil de spike jetable, pas du code mote. Mode d'emploi : README.md de ce dossier.
#
#   powershell -ExecutionPolicy Bypass -File docs\spikes\sp7\run_sp7.ps1            # flux puis hors ligne
#   powershell -ExecutionPolicy Bypass -File docs\spikes\sp7\run_sp7.ps1 -SkipOffline   # flux seul (~30 min)
#
# Relancer la même commande saute ce qui est déjà fait (un JSON par run).
[CmdletBinding()]
param(
    [string]$Session = "$HOME\sp0\sessions\20261007_120820",        # S1 brute, avec left_depth/
    [string]$NsData = "$HOME\sp0\work\20261007_120820\nsdata",       # jeu commun de S1 (bench de SP-0)
    [string]$Out = "$HOME\sp0\sp7",
    [string]$Python = "$HOME\sp0\tools\venv-train\Scripts\python.exe",
    [int[]]$Seeds = @(0, 1, 2),
    [int]$OfflineSteps = 30000,
    [switch]$SkipOffline,
    [switch]$SkipStream
)
$ErrorActionPreference = "Continue"
function Say($m) { Write-Host "[sp7] $m" }
$here = $PSScriptRoot
$sp6 = "$here\..\sp6"
if (-not (Test-Path $Python)) { Say "pas de venv d'entrainement ($Python) : lancer d'abord docs\spikes\sp0\gpu\train_all.ps1"; exit 2 }
if (-not (Test-Path "$NsData\train_list.txt")) { Say "pas de jeu commun dans $NsData"; exit 2 }
if (-not (Test-Path "$Session\left_depth_descriptors.csv")) { Say "pas de profondeur dans $Session (session brute de S1)"; exit 2 }
New-Item -ItemType Directory -Force "$Out\init", "$Out\runs" | Out-Null
$env:PYTHONUTF8 = "1"

# 1. nuage d'initialisation
if (-not (Test-Path "$Out\init\init.npz")) {
    Say "nuage d'initialisation (rétroprojection de la profondeur de S1)"
    & $Python "$here\depth_init.py" --session $Session --nsdata $NsData --out "$Out\init"
    if ($LASTEXITCODE -ne 0) { Say "ÉCHEC de depth_init.py"; exit 3 }
}
Get-Content "$Out\init\init.json" -Raw | Write-Host
$npz = "$Out\init\init.npz"

function Run($name, [string[]]$extra) {
    $json = "$Out\runs\$name.json"
    if (Test-Path $json) { Say "$name déjà fait"; return }
    Say "$name"
    & $Python "$sp6\incremental.py" --nsdata $NsData --out $json @extra 2>&1 | Tee-Object -FilePath "$Out\runs\$name.log"
    if ($LASTEXITCODE -ne 0) { Say "ÉCHEC $name (code $LASTEXITCODE), voir $Out\runs\$name.log"; Remove-Item -ErrorAction SilentlyContinue $json }
}

# 2. le live d'abord : la meilleure configuration de SP-6 (uniform, demi-résolution), aléatoire contre profondeur
if (-not $SkipStream) {
    foreach ($seed in $Seeds) {
        $f = @("--strategy", "uniform", "--downscale", "2", "--seed", "$seed")
        Run "flux_aleatoire_s$seed" $f
        Run "flux_profondeur_s$seed" ($f + @("--init-npz", $npz))
    }
}

# 3. hors ligne, pleine résolution, 30 000 itérations, évaluation toutes les 200 (environ 45 min par run)
if (-not $SkipOffline) {
    Say "hors ligne : $($Seeds.Count * 2) runs de $OfflineSteps itérations, compter 4 à 5 h"
    foreach ($seed in $Seeds) {
        $f = @("--offline", "--max-steps", "$OfflineSteps", "--eval-every-it", "200", "--seed", "$seed")
        Run "horsligne_aleatoire_s$seed" $f
        Run "horsligne_profondeur_s$seed" ($f + @("--init-npz", $npz))
    }
}

& $Python "$here\compare.py" --runs "$Out\runs"
& $Python "$sp6\curves.py" --runs "$Out\runs"
Say "nuage : $Out\init\init.ply, vues : $Out\init\init_views.png"
exit 0
