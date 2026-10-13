# SP-4 : QuestRealityCapture v1.5.0 + sonde SP-4 + libsp4core.so, en une commande : clone, injection, build Android en
# batchmode, installation sur le casque. Outil de spike jetable, pas du code mote. Mode d'emploi : README.md.
#
#   powershell -ExecutionPolicy Bypass -File docs\spikes\sp4\build_sp4.ps1
#
# L'APK a son propre identifiant (com.t34400.QuestRealityCapture.sp4) : il s'installe à côté de l'original et de SP3.
[CmdletBinding()]
param(
    [string]$Work = "$HOME\sp4",
    [string]$UnityVersion = "6000.4.5f1",            # ProjectVersion.txt de QRC v1.5.0
    [string]$Unity = "",                             # chemin de Unity.exe ; par défaut celui de Unity Hub
    [switch]$SkipInstall
)
$ErrorActionPreference = "Continue"   # git et adb écrivent sur stderr sans échouer : on lit les codes de retour
function Say($m) { Write-Host "[sp4] $m" }
$here = $PSScriptRoot
$pkg = "com.t34400.QuestRealityCapture.sp4"
$qrc = "$Work\qrc"
$apk = "$Work\QuestRealityCapture-sp4.apk"
New-Item -ItemType Directory -Force $Work | Out-Null

# 0. Le .so versionné, vérifié
$so = "$here\prebuilt\libsp4core.so"
$want = ((Get-Content "$so.sha256") -split "\s+")[0]
$got = (Get-FileHash $so).Hash.ToLower()
if ($got -ne $want) { Say "libsp4core.so ne correspond pas à son empreinte ($got au lieu de $want)"; exit 3 }

# 1. Unity
if (-not $Unity) { $Unity = "C:\Program Files\Unity\Hub\Editor\$UnityVersion\Editor\Unity.exe" }
if (-not (Test-Path $Unity)) {
    Say "Unity $UnityVersion introuvable ($Unity)."
    Say "Éditeurs installés : $((Get-ChildItem 'C:\Program Files\Unity\Hub\Editor' -ErrorAction SilentlyContinue).Name -join ', ')"
    Say "Installer $UnityVersion avec le module Android Build Support (Unity Hub), ou passer -Unity <chemin de Unity.exe>."
    exit 2
}

# 2. Sources, commit vérifié (un clone à part de celui de SP-3 : pas de mélange des patchs)
if (-not (Test-Path "$qrc\.git")) {
    Say "clone de QuestRealityCapture v1.5.0"
    git -c core.longpaths=true clone --depth 1 --branch v1.5.0 https://github.com/t-34400/QuestRealityCapture $qrc
    if ($LASTEXITCODE -ne 0) { Say "échec du clone"; exit 3 }
}
$commit = git -C $qrc rev-parse HEAD
if ($commit -ne "649c012a3d95363101aa7f9fe53d67c59cbecbec") { Say "commit inattendu $commit (attendu 649c012, v1.5.0)"; exit 3 }

# 3. Injection : le .so, la sonde (asmdef avec code unsafe), le script de build
New-Item -ItemType Directory -Force "$qrc\Assets\Plugins\Android\arm64-v8a", "$qrc\Assets\Sp4\Editor" | Out-Null
Copy-Item $so "$qrc\Assets\Plugins\Android\arm64-v8a\libsp4core.so" -Force
Copy-Item "$here\unity\Sp4Probe.cs", "$here\unity\Sp4.asmdef" "$qrc\Assets\Sp4\" -Force
Copy-Item "$here\unity\Editor\Sp4Build.cs", "$here\unity\Editor\Sp4.Editor.asmdef" "$qrc\Assets\Sp4\Editor\" -Force
Say "injecté ($((git -C $qrc status --short) -join ' ; '))"

# 4. Build Android (premier build : 10 à 20 min, import des packages compris)
$newest = (Get-ChildItem "$here\unity", "$here\prebuilt" -Recurse -File | Measure-Object LastWriteTime -Maximum).Maximum
if (-not (Test-Path $apk) -or (Get-Item $apk).LastWriteTime -lt $newest) {
    # L'import des packages échoue parfois sous Windows (EPERM au renommage dans Library\PackageCache, fichier tenu
    # par l'antivirus ou l'indexeur) : on relance, le cache déjà rempli est réutilisé.
    for ($try = 1; $try -le 3; $try++) {
        Say "build Android (essai $try/3), journal : $Work\build.log"
        Get-ChildItem "$qrc\Library\PackageCache" -Filter ".tmp-*" -Directory -ErrorAction SilentlyContinue |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        $p = Start-Process -FilePath $Unity -Wait -PassThru -NoNewWindow -ArgumentList @(
            "-batchmode", "-nographics", "-quit", "-projectPath", "`"$qrc`"", "-buildTarget", "Android",
            "-executeMethod", "Sp4Build.Build", "-sp4Output", "`"$apk`"", "-logFile", "`"$Work\build.log`"")
        if ($p.ExitCode -eq 0 -and (Test-Path $apk)) { break }
        $transient = Select-String -Path "$Work\build.log" -Pattern "EPERM|EBUSY|could not be added to the local file system" -Quiet
        # premier import d'un projet neuf en batchmode : des packages (ShaderGraph...) compilés avant d'être complets
        # échouent (error CS dans Library\PackageCache) ; au lancement suivant, le cache est complet
        $cs = @(Select-String -Path "$Work\build.log" -Pattern "error CS\d+" | ForEach-Object { $_.Line })
        if ($cs.Count -gt 0 -and @($cs | Where-Object { $_ -notmatch 'Library[\\/]PackageCache' }).Count -eq 0) { $transient = $true }
        if (-not $transient -or $try -eq 3) {
            Say "ÉCHEC du build (code $($p.ExitCode)). Erreurs de compilation et dernières lignes du journal :"
            Select-String -Path "$Work\build.log" -Pattern "error CS|\[sp4\]" | Select-Object -First 20 | ForEach-Object { $_.Line }
            Get-Content "$Work\build.log" -Tail 15
            if ($transient) { Say "erreur d'accès répétée dans PackageCache : exclure $Work de l'analyse en temps réel de Windows Defender, fermer Unity Hub et l'éditeur, puis relancer" }
            exit 4
        }
        Say "erreur transitoire (accès à PackageCache ou premier import des packages), nouvel essai dans 10 s"
        Start-Sleep -Seconds 10
    }
}
Say "APK : $apk ($([math]::Round((Get-Item $apk).Length / 1MB)) Mo)"
if ($SkipInstall) { exit 0 }

# 5. Installation et durées des phases
$dev = adb devices | Select-String "\tdevice$"
if (-not $dev) { Say "aucun casque vu par adb (adb devices) : brancher le casque, autoriser le débogage USB"; exit 5 }
adb install -r $apk
if ($LASTEXITCODE -ne 0) { Say "échec de adb install"; exit 5 }
# Le dossier files/ de l'app n'existe qu'après son premier lancement, et adb ne peut pas le créer (Android 11+) :
# avant ce lancement, la copie échoue sans conséquence, la sonde ayant les mêmes valeurs par défaut que le fichier.
adb push "$here\sp4_config.json" "/sdcard/Android/data/$pkg/files/sp4_config.json" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Say "sp4_config.json non copié (l'app n'a jamais été lancée) : sans effet, la sonde a les mêmes valeurs par défaut."
    Say "Pour changer les durées : lancer l'app une fois, puis relancer ce script."
}
Say "installé : « QuestRealityCapture SP4 » dans la bibliothèque du casque (Sources inconnues). Suivre README.md §2."
