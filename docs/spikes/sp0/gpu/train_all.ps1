# SP-0 : bench 3DGS sur le PC NVIDIA, poses du casque (A) contre poses COLMAP (AREF), en une commande.
# Outil de spike jetable, pas du code mote. Mode d'emploi : README.md de ce dossier.
#
#   powershell -ExecutionPolicy Bypass -File train_all.ps1
#
# 1. run_all.ps1 : export et REF COLMAP de chaque session (sauté pour ce qui est déjà fait)
# 2. venv d'entraînement : Python 3.10, torch 2.1.2 CUDA 11.8, nerfstudio 1.1.5, gsplat 1.4.0 précompilé, LPIPS
# 3. train.py : jeu commun, splatfacto A et AREF sur chaque graine, rendu, métriques, bench.json
# Relancer la même commande reprend là où ça s'est arrêté.
[CmdletBinding()]
param(
    [string]$Data = "$HOME\sp0\sessions",
    [string]$Work = "$HOME\sp0\work",
    [string]$Tools = "$HOME\sp0\tools",
    [int[]]$Seeds = @(0, 1, 2),             # au moins 3 (PROTOCOL.md §7)
    [ValidateSet("A", "AREF")][string[]]$Variants = @("A", "AREF"),
    [int]$Iterations = 30000,               # figé par SP-0 (PROTOCOL.md §7)
    [string[]]$Only,
    [switch]$SkipColmap,                    # ne pas relancer run_all.ps1
    [switch]$DryRun
)
$ErrorActionPreference = "Continue"   # codes de sortie verifies a la main : PS 5.1 transforme le stderr natif en erreurs
function Say($m) { Write-Host "[sp0-gpu] $m" }

# 1. COLMAP (REF) : rien n'est refait pour une session déjà finie
if (-not $SkipColmap) {
    $ra = @{ Data = $Data; Work = $Work; Tools = $Tools }
    if ($Only) { $ra.Only = $Only }
    if ($DryRun) { $ra.DryRun = $true }
    & "$PSScriptRoot\run_all.ps1" @ra
    if ($LASTEXITCODE -gt 1) { Say "arret : run_all.ps1 a echoue (code $LASTEXITCODE)"; exit $LASTEXITCODE }
    if ($LASTEXITCODE -eq 1) { Say "des sessions sont en echec cote COLMAP ; on entraine celles qui ont un REF" }
}

# 2. venv d'entraînement, séparé de celui de SRC-3 (versions de numpy et d'OpenCV incompatibles)
$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uv) { $uv = "$HOME\.local\bin\uv.exe" }
if (-not (Test-Path $uv)) {
    Say "installation de uv"
    powershell -NoProfile -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
}
$py = "$Tools\venv-train\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Say "creation du venv d'entrainement Python 3.10 dans $Tools\venv-train"
    & $uv venv --python 3.10 "$Tools\venv-train"
    if ($LASTEXITCODE -ne 0) { throw "uv venv a echoue" }
}
& $py -c "import nerfstudio, gsplat, lpips, torch; assert torch.version.cuda" 2>$null
if ($LASTEXITCODE -ne 0) {
    Say "installation de torch 2.1.2 CUDA 11.8, nerfstudio 1.1.5, gsplat 1.4.0, LPIPS (environ 3 Go, une fois)"
    # gsplat précompilé pour torch 2.1 / CUDA 11.8 / Python 3.10 : ni CUDA Toolkit ni Visual Studio à installer
    $gsplat = "https://github.com/nerfstudio-project/gsplat/releases/download/v1.4.0/gsplat-1.4.0%2Bpt21cu118-cp310-cp310-win_amd64.whl"
    & $uv pip install --python $py --extra-index-url https://download.pytorch.org/whl/cu118 `
        --index-strategy unsafe-best-match "torch==2.1.2+cu118" "torchvision==0.16.2+cu118" `
        "nerfstudio==1.1.5" "lpips==0.1.4" "numpy<2" "gsplat @ $gsplat"
    if ($LASTEXITCODE -ne 0) { throw "installation de l'environnement d'entrainement echouee" }
}
if (-not $DryRun) {
    & $py -c "import torch,sys; ok=torch.cuda.is_available(); print('[sp0-gpu] torch', torch.__version__, 'CUDA', ok, torch.cuda.get_device_name(0) if ok else ''); sys.exit(0 if ok else 1)"
    if ($LASTEXITCODE -ne 0) { Say "arret : torch ne voit pas le GPU (pilote NVIDIA trop ancien pour CUDA 11.8 ?)"; exit 3 }
}

# 3. bench
$a = @("$PSScriptRoot\train.py", "--work", $Work, "--iterations", "$Iterations", "--seeds") + ($Seeds | ForEach-Object { "$_" })
$a += @("--variants") + $Variants
if ($Only) { $a += @("--only") + $Only }
if ($DryRun) { $a += "--dry-run" }
& $py @a
exit $LASTEXITCODE
