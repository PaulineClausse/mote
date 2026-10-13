// SP-3 (mote) : build Android en ligne de commande de QuestRealityCapture instrumenté. Copié dans Assets/Sp3/Editor/
// par build_qrc.ps1. Identifiant de paquet à part : l'APK s'installe à côté de l'original sans le remplacer, donc sans
// désinstaller l'original ni perdre les sessions qu'il garde sur le casque.
//
//   Unity.exe -batchmode -nographics -quit -projectPath <qrc> -buildTarget Android
//             -executeMethod Sp3Build.Build -sp3Output <chemin.apk>
using System;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class Sp3Build
{
    public const string PackageId = "com.t34400.QuestRealityCapture.sp3";

    public static void Build()
    {
        var args = Environment.GetCommandLineArgs();
        var i = Array.IndexOf(args, "-sp3Output");
        var output = i >= 0 && i + 1 < args.Length ? args[i + 1] : "Builds/QuestRealityCapture-sp3.apk";

        PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, PackageId);
        PlayerSettings.productName = "QuestRealityCapture SP3";

        var options = new BuildPlayerOptions
        {
            scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray(),
            locationPathName = output,
            target = BuildTarget.Android,
            options = BuildOptions.None,
        };
        var report = BuildPipeline.BuildPlayer(options);
        Debug.Log($"[sp3] build {report.summary.result}, {report.summary.totalErrors} erreur(s) -> {output}");
        EditorApplication.Exit(report.summary.result == BuildResult.Succeeded ? 0 : 1);
    }
}
