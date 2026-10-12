# SP-6 : entraînement 3DGS incrémental sur les poses du casque, en une commande, sur le PC NVIDIA de SP-0.
# Outil de spike jetable, pas du code mote. Mode d'emploi : README.md de ce dossier.
#
#   powershell -ExecutionPolicy Bypass -File docs\spikes\sp6\run_sp6.ps1
#
# Réutilise le venv d'entraînement et le jeu commun (nsdata) préparés par le bench de SP-0 (train_all.ps1).
# Relancer la même commande saute les runs déjà faits (un JSON par run dans -Out).
[CmdletBinding()]
param(
    [string]$NsData = "$HOME\sp0\work\20261007_120820\nsdata",   # S1
    [string]$Out = "$HOME\sp0\sp6\runs",
    [string]$Python = "$HOME\sp0\tools\venv-train\Scripts\python.exe",
    [int[]]$Seeds = @(0, 1, 2),
    [string[]]$Strategies = @("uniform", "recent", "window"),
    [int]$OfflineSteps = 7000,
    [switch]$SkipOffline,
    [switch]$SkipDownscale,
    [switch]$WithNoReset                  # en plus : la meilleure piste sans remise des opacités
)
$ErrorActionPreference = "Continue"
function Say($m) { Write-Host "[sp6] $m" }
$here = $PSScriptRoot
if (-not (Test-Path $Python)) { Say "pas de venv d'entrainement ($Python) : lancer d'abord docs\spikes\sp0\gpu\train_all.ps1"; exit 2 }
if (-not (Test-Path "$NsData\train_list.txt")) { Say "pas de jeu commun dans $NsData : lancer d'abord le bench de SP-0"; exit 2 }
New-Item -ItemType Directory -Force $Out | Out-Null
$env:PYTHONUTF8 = "1"

function Run($name, [string[]]$extra) {
    $json = "$Out\$name.json"
    if (Test-Path $json) { Say "$name deja fait"; return }
    Say "$name"
    & $Python "$here\incremental.py" --nsdata $NsData --out $json @extra 2>&1 | Tee-Object -FilePath "$Out\$name.log"
    if ($LASTEXITCODE -ne 0) { Say "ECHEC $name (code $LASTEXITCODE), voir $Out\$name.log"; Remove-Item -ErrorAction SilentlyContinue $json }
}

& $Python -c "import gsplat, torchmetrics, torch; assert torch.cuda.is_available()"
if ($LASTEXITCODE -ne 0) { Say "le venv ne voit pas gsplat, torchmetrics ou le GPU"; exit 3 }

foreach ($seed in $Seeds) {
    # 1. latence d'aperçu pure : toutes les vues dès t = 0, évaluation toutes les 200 itérations
    if (-not $SkipOffline) { Run "offline_s$seed" @("--offline", "--max-steps", "$OfflineSteps", "--eval-every-it", "200", "--seed", "$seed") }
    # 2. rejeu de S1 à sa cadence réelle, une stratégie à la fois, 60 s d'entraînement après la fin du flux
    foreach ($st in $Strategies) { Run "${st}_s$seed" @("--strategy", $st, "--seed", "$seed") }
    # 3. mitigation de RISK-09 : demi-résolution
    if (-not $SkipDownscale) { Run "recent_half_s$seed" @("--strategy", "recent", "--downscale", "2", "--seed", "$seed") }
    if ($WithNoReset) { Run "recent_noreset_s$seed" @("--strategy", "recent", "--reset-every", "0", "--seed", "$seed") }
}

& $Python "$here\summarize.py" --runs $Out
exit $LASTEXITCODE
