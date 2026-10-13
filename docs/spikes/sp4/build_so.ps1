# SP-4 : reconstruit prebuilt/libsp4core.so (arm64-v8a) depuis sp4core/. Inutile pour la mesure : le .so est versionné.
# Prérequis : rustup target add aarch64-linux-android ; cargo install cargo-ndk ; NDK r27c ; cmake ; ninja.
#
#   powershell -ExecutionPolicy Bypass -File docs\spikes\sp4\build_so.ps1 -Ndk C:\chemin\court\android-ndk-r27c
#
# Windows : garder le NDK et le dossier target sur des chemins courts (le clang du NDK échoue au-delà de 260
# caractères, « unspecified system_category error »).
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Ndk,
    [string]$Target = "$env:TEMP\sp4t"
)
$ErrorActionPreference = "Continue"
$env:ANDROID_NDK_HOME = $Ndk
$env:CMAKE_GENERATOR = "Ninja"
$env:CMAKE_MAKE_PROGRAM = (Get-Command ninja).Source
$env:CMAKE_TOOLCHAIN_FILE_aarch64_linux_android = "$Ndk\build\cmake\android.toolchain.cmake"
$env:ANDROID_ABI = "arm64-v8a"
$env:ANDROID_PLATFORM = "android-32"
$env:CARGO_TARGET_DIR = $Target
Push-Location "$PSScriptRoot\sp4core"
cargo ndk -t arm64-v8a -P 32 build --release
$rc = $LASTEXITCODE
Pop-Location
if ($rc -ne 0) { exit $rc }
$so = "$Target\aarch64-linux-android\release\libsp4core.so"
New-Item -ItemType Directory -Force "$PSScriptRoot\prebuilt" | Out-Null
Copy-Item $so "$PSScriptRoot\prebuilt\libsp4core.so" -Force
$h = (Get-FileHash "$PSScriptRoot\prebuilt\libsp4core.so").Hash.ToLower()
Set-Content "$PSScriptRoot\prebuilt\libsp4core.so.sha256" "$h  libsp4core.so"
Write-Host "[sp4] prebuilt\libsp4core.so ($h)"
