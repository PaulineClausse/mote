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
    Say "build Android, journal : $Work\build.log"
    $p = Start-Process -FilePath $Unity -Wait -PassThru -NoNewWindow -ArgumentList @(
        "-batchmode", "-nographics", "-quit", "-projectPath", "`"$qrc`"", "-buildTarget", "Android",
        "-executeMethod", "Sp4Build.Build", "-sp4Output", "`"$apk`"", "-logFile", "`"$Work\build.log`"")
    if ($p.ExitCode -ne 0 -or -not (Test-Path $apk)) {
        Say "ÉCHEC du build (code $($p.ExitCode)). Erreurs de compilation et dernières lignes du journal :"
        Select-String -Path "$Work\build.log" -Pattern "error CS|\[sp4\]" | Select-Object -First 20 | ForEach-Object { $_.Line }
        Get-Content "$Work\build.log" -Tail 15
        exit 4
    }
}
Say "APK : $apk ($([math]::Round((Get-Item $apk).Length / 1MB)) Mo)"
if ($SkipInstall) { exit 0 }

# 5. Installation et durées des phases
$dev = adb devices | Select-String "\tdevice$"
if (-not $dev) { Say "aucun casque vu par adb (adb devices) : brancher le casque, autoriser le débogage USB"; exit 5 }
adb install -r $apk
if ($LASTEXITCODE -ne 0) { Say "échec de adb install"; exit 5 }
adb push "$here\sp4_config.json" "/sdcard/Android/data/$pkg/files/sp4_config.json"
Say "installé : « QuestRealityCapture SP4 » dans la bibliothèque du casque (Sources inconnues). Suivre README.md §2."
