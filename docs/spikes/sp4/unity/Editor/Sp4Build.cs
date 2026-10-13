// SP-4 (mote, jetable) : build Android en ligne de commande de QuestRealityCapture + sonde SP-4. Copié dans
// Assets/Sp4/Editor/ par build_sp4.ps1. Identifiant de paquet à part : s'installe à côté de l'original et de SP3.
//
//   Unity.exe -batchmode -nographics -quit -projectPath <qrc> -buildTarget Android
//             -executeMethod Sp4Build.Build -sp4Output <chemin.apk>
using System;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class Sp4Build
{
    public const string PackageId = "com.t34400.QuestRealityCapture.sp4";
    const string Plugin = "Assets/Plugins/Android/arm64-v8a/libsp4core.so";

    public static void Build()
    {
        var args = Environment.GetCommandLineArgs();
        var i = Array.IndexOf(args, "-sp4Output");
        var output = i >= 0 && i + 1 < args.Length ? args[i + 1] : "Builds/QuestRealityCapture-sp4.apk";

        // le .so du core : Android ARM64 seulement
        AssetDatabase.ImportAsset(Plugin, ImportAssetOptions.ForceUpdate);
        if (AssetImporter.GetAtPath(Plugin) is not PluginImporter imp)
        {
            Debug.LogError($"[sp4] plugin introuvable : {Plugin}");
            EditorApplication.Exit(2);
            return;
        }
        imp.SetCompatibleWithAnyPlatform(false);
        imp.SetCompatibleWithEditor(false);
        imp.SetCompatibleWithPlatform(BuildTarget.Android, true);
        imp.SetPlatformData(BuildTarget.Android, "CPU", "ARM64");
        imp.SaveAndReimport();

        PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, PackageId);
        PlayerSettings.productName = "QuestRealityCapture SP4";

        var options = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray(),
            locationPathName = output,
            target = BuildTarget.Android,
            options = BuildOptions.None,
        };
        var report = BuildPipeline.BuildPlayer(options);
        Debug.Log($"[sp4] build {report.summary.result}, {report.summary.totalErrors} erreur(s) -> {output}");
        EditorApplication.Exit(report.summary.result == BuildResult.Succeeded ? 0 : 1);
    }
}
