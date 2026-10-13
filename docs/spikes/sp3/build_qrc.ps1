# SP-3 : QuestRealityCapture v1.5.0 instrumenté (chronométrage de la relecture de profondeur), en une commande :
# clone, patch, build Android en batchmode, installation sur le casque, configuration.
# Outil de spike jetable, pas du code mote. Mode d'emploi : README.md de ce dossier.
#
#   powershell -ExecutionPolicy Bypass -File docs\spikes\sp3\build_qrc.ps1
#
# L'APK a son propre identifiant (com.t34400.QuestRealityCapture.sp3) : il s'installe à côté de l'original.
[CmdletBinding()]
param(
    [string]$Work = "$HOME\sp3",
    [string]$UnityVersion = "6000.4.5f1",            # ProjectVersion.txt de QRC v1.5.0
    [string]$Unity = "",                             # chemin de Unity.exe ; par défaut celui de Unity Hub
    [switch]$SkipInstall
)
$ErrorActionPreference = "Continue"   # git et adb écrivent sur stderr sans échouer : on lit les codes de retour
function Say($m) { Write-Host "[sp3] $m" }
$here = $PSScriptRoot
$pkg = "com.t34400.QuestRealityCapture.sp3"
$qrc = "$Work\qrc"
$apk = "$Work\QuestRealityCapture-sp3.apk"
New-Item -ItemType Directory -Force $Work | Out-Null

# 1. Unity
if (-not $Unity) { $Unity = "C:\Program Files\Unity\Hub\Editor\$UnityVersion\Editor\Unity.exe" }
if (-not (Test-Path $Unity)) {
    Say "Unity $UnityVersion introuvable ($Unity)."
    Say "Éditeurs installés : $((Get-ChildItem 'C:\Program Files\Unity\Hub\Editor' -ErrorAction SilentlyContinue).Name -join ', ')"
    Say "Installer $UnityVersion avec le module Android Build Support (Unity Hub), ou passer -Unity <chemin de Unity.exe>."
    exit 2
}

# 2. Sources, commit vérifié
if (-not (Test-Path "$qrc\.git")) {
    Say "clone de QuestRealityCapture v1.5.0"
    git -c core.longpaths=true clone --depth 1 --branch v1.5.0 https://github.com/t-34400/QuestRealityCapture $qrc
    if ($LASTEXITCODE -ne 0) { Say "échec du clone"; exit 3 }
}
$commit = git -C $qrc rev-parse HEAD
if ($commit -ne "649c012a3d95363101aa7f9fe53d67c59cbecbec") { Say "commit inattendu $commit (attendu 649c012, v1.5.0)"; exit 3 }

# 3. Patch : l'exporteur instrumenté remplace l'original, le script de build est ajouté
$target = "$qrc\Assets\RealityLog\Scripts\Runtime\IO\DepthRenderTextureExporter.cs"
Copy-Item "$here\qrc_patch\DepthRenderTextureExporter.cs" $target -Force
New-Item -ItemType Directory -Force "$qrc\Assets\Sp3\Editor" | Out-Null
Copy-Item "$here\qrc_patch\Sp3Build.cs" "$qrc\Assets\Sp3\Editor\Sp3Build.cs" -Force
Say "patch appliqué ($((git -C $qrc status --short) -join ' ; '))"

# 4. Build Android (premier build : 10 à 20 min, import des packages compris)
if (-not (Test-Path $apk) -or (Get-Item $apk).LastWriteTime -lt (Get-Item "$here\qrc_patch\DepthRenderTextureExporter.cs").LastWriteTime) {
    # L'import des packages échoue parfois sous Windows (EPERM au renommage dans Library\PackageCache, fichier tenu
    # par l'antivirus ou l'indexeur) : on relance, le cache déjà rempli est réutilisé.
    for ($try = 1; $try -le 3; $try++) {
        Say "build Android (essai $try/3), journal : $Work\build.log"
        Get-ChildItem "$qrc\Library\PackageCache" -Filter ".tmp-*" -Directory -ErrorAction SilentlyContinue |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        $p = Start-Process -FilePath $Unity -Wait -PassThru -NoNewWindow -ArgumentList @(
            "-batchmode", "-nographics", "-quit", "-projectPath", "`"$qrc`"", "-buildTarget", "Android",
            "-executeMethod", "Sp3Build.Build", "-sp3Output", "`"$apk`"", "-logFile", "`"$Work\build.log`"")
        if ($p.ExitCode -eq 0 -and (Test-Path $apk)) { break }
        $transient = Select-String -Path "$Work\build.log" -Pattern "EPERM|EBUSY|could not be added to the local file system" -Quiet
        # premier import d'un projet neuf en batchmode : des packages (ShaderGraph...) compilés avant d'être complets
        # échouent (error CS dans Library\PackageCache) ; au lancement suivant, le cache est complet
        $cs = @(Select-String -Path "$Work\build.log" -Pattern "error CS\d+" | ForEach-Object { $_.Line })
        if ($cs.Count -gt 0 -and @($cs | Where-Object { $_ -notmatch 'Library[\\/]PackageCache' }).Count -eq 0) { $transient = $true }
        if (-not $transient -or $try -eq 3) {
            Say "ÉCHEC du build (code $($p.ExitCode)). Dernières lignes du journal :"
            Get-Content "$Work\build.log" -Tail 30
            if ($transient) { Say "erreur d'accès répétée dans PackageCache : exclure $Work de l'analyse en temps réel de Windows Defender, fermer Unity Hub et l'éditeur, puis relancer" }
            exit 4
        }
        Say "erreur transitoire (accès à PackageCache ou premier import des packages), nouvel essai dans 10 s"
        Start-Sleep -Seconds 10
    }
}
Say "APK : $apk ($([math]::Round((Get-Item $apk).Length / 1MB)) Mo)"
if ($SkipInstall) { exit 0 }

# 5. Installation et configuration (profondeur à pleine cadence, targetSaveFps 0)
$dev = adb devices | Select-String "\tdevice$"
if (-not $dev) { Say "aucun casque vu par adb (adb devices) : brancher le casque, autoriser le débogage USB"; exit 5 }
adb install -r $apk
if ($LASTEXITCODE -ne 0) { Say "échec de adb install"; exit 5 }
adb push "$here\recording_config_sp3.json" "/sdcard/Android/data/$pkg/files/recording_config.json"
Say "installé : « QuestRealityCapture SP3 » dans la bibliothèque du casque (Sources inconnues). Suivre README.md §2."
