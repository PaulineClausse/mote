// SP-4 (mote, jetable) : sonde injectée dans QuestRealityCapture v1.5.0 par build_sp4.ps1. Elle démarre seule au
// lancement, active les deux PassthroughCameraAccess du projet (1280x1280) et enchaîne ses phases :
//
//   warmup    caméras activées, attente du flux
//   bench     encodage JPEG pur dans le core, images synthétiques (sp4_bench_encode)
//   baseline  caméras actives, rien de lu : référence de la fréquence d'affichage et de la charge CPU
//   getcolors GetColors gauche + droite à 10 paires/s sur le thread principal, rien de poussé
//   nominal   GetColors + push au core (copie, JPEG q90 sur 2 threads, MCAP) à 10 paires/s
//   async     relecture GPU asynchrone (AsyncGPUReadback, RGBA32) + push au core, à 10 paires/s : le remède prévu par la
//             règle de SP-4.md si GetColors fait décrocher l'affichage (ajouté après le premier passage)
//
// Sorties dans <persistentDataPath>/sp4/ : sp4_seconds.csv (une ligne par seconde), sp4_phases.jsonl (une ligne par
// phase et des événements de diagnostic), un sp4_<unix>.mcap par phase qui écrit (nominal, async). Durées et réglages :
// sp4_config.json au même endroit. Ne pas démarrer l'enregistrement de QRC pendant la sonde : il désactiverait les
// caméras en s'arrêtant.

#nullable enable
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using Meta.XR;
using Unity.Collections;
using Unity.Collections.LowLevel.Unsafe;
using UnityEngine;
using UnityEngine.Rendering;
using Debug = UnityEngine.Debug;

namespace Sp4
{
    [Serializable]
    public class Sp4Config
    {
        public float warmupS = 20, baselineS = 60, getColorsS = 60, nominalS = 120, asyncS = 180;
        public float pairsPerSecond = 10;
        public int jpegQuality = 90, threads = 2, queuePairs = 8, benchImages = 40, maxFramerate = 10;
        public int asyncMaxInflightPairs = 3;
    }

    static class Native
    {
        const string Lib = "sp4core";
        [DllImport(Lib)] public static extern IntPtr sp4_open(string dir, uint quality, uint threads, uint queuePairs);
        [DllImport(Lib)] public static extern int sp4_push_pair(IntPtr ctx, long tNs, IntPtr left, IntPtr right,
                                                                uint width, uint height, uint stride);
        [DllImport(Lib)] public static extern int sp4_stats_json(IntPtr ctx, byte[] buf, uint cap);
        [DllImport(Lib)] public static extern int sp4_close(IntPtr ctx, byte[] buf, uint cap);
        [DllImport(Lib)] public static extern int sp4_bench_encode(uint w, uint h, uint n, uint q, byte[] buf, uint cap);
        [DllImport(Lib)] public static extern double sp4_process_cpu_s();

        public static string Str(byte[] b) { var n = Array.IndexOf(b, (byte)0); return Encoding.UTF8.GetString(b, 0, n < 0 ? b.Length : n); }
    }

    public class Sp4Probe : MonoBehaviour
    {
        enum Phase { Warmup, Bench, Baseline, GetColors, Nominal, Async, Done }

        static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
        Sp4Config cfg = new Sp4Config();
        string dir = "";
        Phase phase = Phase.Warmup;
        float phaseStart, secondStart, lastSample = -1;
        PassthroughCameraAccess? left, right;
        DateTime lastLeftTs, lastRightTs;
        IntPtr core = IntPtr.Zero;
        StreamWriter? seconds, phases;
        TextMesh? label;

        // fenêtre d'une seconde
        readonly List<float> dts = new List<float>();
        readonly List<double> readMs = new List<double>(), pushMs = new List<double>();
        int pairs, busy;
        double cpuAtSecond;
        // phase entière
        readonly List<float> phaseDts = new List<float>();
        readonly List<double> phaseRead = new List<double>();
        readonly List<int> phaseLatencyFrames = new List<int>();
        int phasePairs, phaseBusy, phaseMissed, phaseFrames, phaseSkipped, phaseNotCreated, phaseBadSize, phaseErrors;
        double cpuAtPhase;
        float wallAtPhase;
        bool sizeLogged;

        // relecture asynchrone
        NativeArray<byte> leftBuf;
        int asyncId, leftId = -1, leftW, leftH, inflight;
        long leftTns;
        readonly Dictionary<int, double> mainMsById = new Dictionary<int, double>();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Boot()
        {
            var go = new GameObject("Sp4Probe");
            DontDestroyOnLoad(go);
            go.AddComponent<Sp4Probe>();
        }

        void Start()
        {
            dir = Path.Combine(Application.persistentDataPath, "sp4");
            Directory.CreateDirectory(dir);
            var cfgPath = Path.Combine(Application.persistentDataPath, "sp4_config.json");
            if (File.Exists(cfgPath)) JsonUtility.FromJsonOverwrite(File.ReadAllText(cfgPath), cfg);
            seconds = new StreamWriter(Path.Combine(dir, "sp4_seconds.csv"), false) { AutoFlush = true };
            seconds.WriteLine("phase,t_s,frames,refresh_hz,dt_p50_ms,dt_max_ms,missed,process_cpu_pct,cores," +
                              "getcolors_ms_avg,getcolors_ms_max,pairs,push_ms_avg,busy,thermal_status");
            phases = new StreamWriter(Path.Combine(dir, "sp4_phases.jsonl"), false) { AutoFlush = true };
            MakeLabel();
            foreach (var a in FindObjectsByType<PassthroughCameraAccess>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                if (a.CameraPosition == PassthroughCameraAccess.CameraPositionType.Left) left = a; else right = a;
            }
            if (left == null || right == null) { Log("ERREUR : PassthroughCameraAccess gauche/droite introuvables"); phase = Phase.Done; return; }
            foreach (var a in new[] { left, right })
            {
                if (!a.gameObject.activeInHierarchy) a.gameObject.SetActive(true);
                SetMaxFramerate(a, cfg.maxFramerate);
                a.enabled = true;
            }
            BeginPhase(Phase.Warmup);
        }

        static void SetMaxFramerate(PassthroughCameraAccess a, int fps)
        {
            // L'API exacte n'est pas lue (MRUK 203 n'est pas dans le dépôt de QRC) : par réflexion, sans échouer.
            try
            {
                var p = a.GetType().GetProperty("MaxFramerate");
                if (p != null && p.CanWrite) { p.SetValue(a, fps); return; }
                var f = a.GetType().GetField("_maxFramerate", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                f?.SetValue(a, fps);
            }
            catch (Exception e) { Debug.LogWarning($"[sp4] MaxFramerate non réglé : {e.Message}"); }
        }

        void MakeLabel()
        {
            var cam = Camera.main;
            if (cam == null) return;
            var go = new GameObject("Sp4Label");
            go.transform.SetParent(cam.transform, false);
            go.transform.localPosition = new Vector3(0, -0.25f, 1.5f);
            label = go.AddComponent<TextMesh>();
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            go.GetComponent<MeshRenderer>().material = label.font.material;
            label.characterSize = 0.012f; label.fontSize = 48; label.anchor = TextAnchor.MiddleCenter;
        }

        void Log(string m) { Debug.Log("[sp4] " + m); if (label != null) label.text = m; }

        void LogEvent(string json) { Debug.Log("[sp4] " + json); phases?.WriteLine(json); }

        void BeginPhase(Phase p)
        {
            phase = p;
            phaseStart = secondStart = Time.realtimeSinceStartup;
            wallAtPhase = phaseStart;
            cpuAtPhase = cpuAtSecond = Native.sp4_process_cpu_s();
            phaseDts.Clear(); phaseRead.Clear(); phaseLatencyFrames.Clear(); mainMsById.Clear();
            phasePairs = phaseBusy = phaseMissed = phaseFrames = phaseSkipped = phaseNotCreated = phaseBadSize = phaseErrors = 0;
            dts.Clear(); readMs.Clear(); pushMs.Clear(); pairs = busy = 0;
            sizeLogged = false;
            if (p is Phase.Nominal or Phase.Async)
            {
                core = Native.sp4_open(dir, (uint)cfg.jpegQuality, (uint)cfg.threads, (uint)cfg.queuePairs);
                if (core == IntPtr.Zero) { Log("ERREUR : sp4_open"); Finish(); return; }
            }
            Log($"SP-4 : phase {p}");
        }

        float Duration(Phase p) => p switch
        {
            Phase.Warmup => cfg.warmupS, Phase.Baseline => cfg.baselineS, Phase.GetColors => cfg.getColorsS,
            Phase.Nominal => cfg.nominalS, Phase.Async => cfg.asyncS, _ => 0
        };

        static float RefreshHz()
        {
            try { return OVRPlugin.systemDisplayFrequency; } catch { return 0; }
        }

        static int ThermalStatus()
        {
            try
            {
                using var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
                using var act = player.GetStatic<AndroidJavaObject>("currentActivity");
                using var pm = act.Call<AndroidJavaObject>("getSystemService", "power");
                return pm.Call<int>("getCurrentThermalStatus");
            }
            catch { return -1; }
        }

        void Update()
        {
            if (phase == Phase.Done) return;
            var now = Time.realtimeSinceStartup;
            var dt = Time.unscaledDeltaTime;
            dts.Add(dt); phaseDts.Add(dt); phaseFrames++;
            var hz = RefreshHz();
            if (hz > 0 && dt > 1.5f / hz) phaseMissed++;

            switch (phase)
            {
                case Phase.Warmup:
                    if (now - phaseStart >= cfg.warmupS && left!.IsPlaying && right!.IsPlaying) { EndPhase(); RunBench(); BeginPhase(Phase.Baseline); }
                    else if (now - phaseStart > cfg.warmupS + 60) { Log("ERREUR : les caméras ne démarrent pas (permissions ?)"); Finish(); return; }
                    break;
                case Phase.GetColors:
                case Phase.Nominal:
                    SampleSync(now);
                    break;
                case Phase.Async:
                    SampleAsync(now);
                    break;
            }

            if (now - secondStart >= 1f) WriteSecond(now, hz);
            if ((phase is Phase.Baseline or Phase.GetColors or Phase.Nominal or Phase.Async) && now - phaseStart >= Duration(phase))
            {
                EndPhase();
                if (phase == Phase.Baseline) BeginPhase(Phase.GetColors);
                else if (phase == Phase.GetColors) BeginPhase(Phase.Nominal);
                else if (phase == Phase.Nominal) BeginPhase(Phase.Async);
                else Finish();
            }
        }

        bool NewPair(float now)
        {
            // 10 % de marge : les caméras livrent elles-mêmes ~10 images/s, avec de la gigue ; sans marge on en raterait
            if (now - lastSample < 0.9f / cfg.pairsPerSecond) return false;
            if (!left!.IsPlaying || !right!.IsPlaying) return false;
            if (left.Timestamp == lastLeftTs || right.Timestamp == lastRightTs) return false;   // pas d'image neuve
            lastSample = now; lastLeftTs = left.Timestamp; lastRightTs = right.Timestamp;
            return true;
        }

        static long UnixNs(DateTime t) => (t.Ticks - DateTime.UnixEpoch.Ticks) * 100;

        void LogSize(string mode, int lenL, int lenR, int w, int h)
        {
            if (sizeLogged) return;
            sizeLogged = true;
            var tex = left!.GetTexture();
            var res = left.CurrentResolution;
            LogEvent($"{{\"event\":\"size\",\"phase\":\"{phase}\",\"mode\":\"{mode}\",\"len_left\":{lenL},\"len_right\":{lenR}," +
                  $"\"width\":{w},\"height\":{h},\"texture\":[{(tex != null ? tex.width : 0)},{(tex != null ? tex.height : 0)}]," +
                  $"\"current_resolution\":[{res.x},{res.y}]}}");
        }

        void SampleSync(float now)
        {
            if (!NewPair(now)) return;
            var sw = Stopwatch.StartNew();
            var l = left!.GetColors();
            var r = right!.GetColors();
            var ms = sw.Elapsed.TotalMilliseconds;
            readMs.Add(ms); phaseRead.Add(ms);
            if (phase != Phase.Nominal) return;
            if (!l.IsCreated || !r.IsCreated) { phaseNotCreated++; return; }

            // taille prise sur la texture, et contrôlée contre le tableau (CurrentResolution peut différer)
            var tex = left.GetTexture();
            int w = tex != null ? tex.width : left.CurrentResolution.x;
            int h = l.Length / Math.Max(1, w);
            LogSize("sync", l.Length, r.Length, w, h);
            if (w <= 0 || h <= 0 || l.Length != w * h || r.Length != l.Length) { phaseBadSize++; return; }
            IntPtr lp, rp;
            unsafe
            {
                lp = (IntPtr)NativeArrayUnsafeUtility.GetUnsafeReadOnlyPtr(l);
                rp = (IntPtr)NativeArrayUnsafeUtility.GetUnsafeReadOnlyPtr(r);
            }
            sw.Restart();
            var st = Native.sp4_push_pair(core, UnixNs(left.Timestamp), lp, rp, (uint)w, (uint)h, 0);
            pushMs.Add(sw.Elapsed.TotalMilliseconds);
            pairs++; phasePairs++;
            if (st == 3) { busy++; phaseBusy++; }
            else if (st != 0) phaseErrors++;
        }

        void SampleAsync(float now)
        {
            if (!NewPair(now)) return;
            if (inflight >= 2 * cfg.asyncMaxInflightPairs) { phaseSkipped++; return; }
            var lt = left!.GetTexture();
            var rt = right!.GetTexture();
            if (lt == null || rt == null) { phaseNotCreated++; return; }
            var sw = Stopwatch.StartNew();
            int id = ++asyncId;
            long tNs = UnixNs(left.Timestamp);
            int frame = Time.frameCount;
            var ph = phase;
            inflight += 2;
            AsyncGPUReadback.Request(lt, 0, TextureFormat.RGBA32, req => OnLeft(req, id, tNs, frame, ph));
            AsyncGPUReadback.Request(rt, 0, TextureFormat.RGBA32, req => OnRight(req, id, frame, ph));
            AddMain(id, sw.Elapsed.TotalMilliseconds);
        }

        void AddMain(int id, double ms) { mainMsById.TryGetValue(id, out var v); mainMsById[id] = v + ms; }

        void OnLeft(AsyncGPUReadbackRequest req, int id, long tNs, int frame, Phase ph)
        {
            inflight--;
            if (ph != phase || core == IntPtr.Zero) return;                // arrivée après la fin de la phase
            var sw = Stopwatch.StartNew();
            phaseLatencyFrames.Add(Time.frameCount - frame);
            if (req.hasError) { phaseErrors++; return; }
            var data = req.GetData<byte>();
            if (!leftBuf.IsCreated || leftBuf.Length != data.Length)
            {
                if (leftBuf.IsCreated) leftBuf.Dispose();
                leftBuf = new NativeArray<byte>(data.Length, Allocator.Persistent, NativeArrayOptions.UninitializedMemory);
            }
            NativeArray<byte>.Copy(data, leftBuf, data.Length);            // valide seulement pendant le callback
            leftId = id; leftW = req.width; leftH = req.height; leftTns = tNs;
            AddMain(id, sw.Elapsed.TotalMilliseconds);
        }

        void OnRight(AsyncGPUReadbackRequest req, int id, int frame, Phase ph)
        {
            inflight--;
            if (ph != phase || core == IntPtr.Zero) return;
            var sw = Stopwatch.StartNew();
            phaseLatencyFrames.Add(Time.frameCount - frame);
            if (req.hasError) { phaseErrors++; return; }
            if (leftId != id) { phaseSkipped++; return; }                  // gauche manquante ou d'une autre paire
            var data = req.GetData<byte>();
            LogSize("async", leftBuf.Length / 4, data.Length / 4, req.width, req.height);
            if (req.width != leftW || req.height != leftH || data.Length != leftW * leftH * 4) { phaseBadSize++; return; }
            IntPtr lp, rp;
            unsafe
            {
                lp = (IntPtr)NativeArrayUnsafeUtility.GetUnsafeReadOnlyPtr(leftBuf);
                rp = (IntPtr)NativeArrayUnsafeUtility.GetUnsafeReadOnlyPtr(data);
            }
            var sp = Stopwatch.StartNew();
            var st = Native.sp4_push_pair(core, leftTns, lp, rp, (uint)leftW, (uint)leftH, 0);
            pushMs.Add(sp.Elapsed.TotalMilliseconds);
            pairs++; phasePairs++;
            if (st == 3) { busy++; phaseBusy++; }
            else if (st != 0) phaseErrors++;
            AddMain(id, sw.Elapsed.TotalMilliseconds);
            mainMsById.TryGetValue(id, out var total);
            readMs.Add(total); phaseRead.Add(total);                       // coût total du thread principal par paire
        }

        void WriteSecond(float now, float hz)
        {
            var cpu = Native.sp4_process_cpu_s();
            var cpuPct = 100.0 * (cpu - cpuAtSecond) / Math.Max(1e-3, now - secondStart);
            var sorted = new List<float>(dts); sorted.Sort();
            seconds!.WriteLine(string.Join(",", phase, (now - phaseStart).ToString("F1", Inv), dts.Count,
                hz.ToString("F0", Inv), (1000 * Pct(sorted, 0.5)).ToString("F2", Inv),
                (1000 * (sorted.Count > 0 ? sorted[^1] : 0)).ToString("F2", Inv),
                dts.FindAll(x => hz > 0 && x > 1.5f / hz).Count, cpuPct.ToString("F1", Inv), SystemInfo.processorCount,
                Avg(readMs).ToString("F2", Inv), Max(readMs).ToString("F2", Inv), pairs,
                Avg(pushMs).ToString("F2", Inv), busy, ThermalStatus()));
            secondStart = now; cpuAtSecond = cpu;
            dts.Clear(); readMs.Clear(); pushMs.Clear(); pairs = busy = 0;
            if (label != null) label.text = $"SP-4 : {phase} {now - phaseStart:F0}/{Duration(phase):F0} s";
        }

        void EndPhase()
        {
            var now = Time.realtimeSinceStartup;
            var wall = now - wallAtPhase;
            var sorted = new List<float>(phaseDts); sorted.Sort();
            var gc = new List<double>(phaseRead); gc.Sort();
            var lat = new List<int>(phaseLatencyFrames); lat.Sort();
            var sb = new StringBuilder();
            sb.Append("{\"phase\":\"").Append(phase).Append("\",\"wall_s\":").Append(wall.ToString("F2", Inv))
              .Append(",\"read_mode\":\"").Append(phase == Phase.Async ? "async" : "sync").Append('"')
              .Append(",\"frames\":").Append(phaseFrames)
              .Append(",\"fps\":").Append((phaseFrames / Math.Max(1e-3f, wall)).ToString("F2", Inv))
              .Append(",\"refresh_hz\":").Append(RefreshHz().ToString("F0", Inv))
              .Append(",\"dt_p50_ms\":").Append((1000 * Pct(sorted, 0.5)).ToString("F2", Inv))
              .Append(",\"dt_p99_ms\":").Append((1000 * Pct(sorted, 0.99)).ToString("F2", Inv))
              .Append(",\"missed\":").Append(phaseMissed)
              .Append(",\"process_cpu_pct\":").Append((100.0 * (Native.sp4_process_cpu_s() - cpuAtPhase) / Math.Max(1e-3, wall)).ToString("F1", Inv))
              .Append(",\"cores\":").Append(SystemInfo.processorCount)
              .Append(",\"getcolors_pairs\":").Append(gc.Count)
              .Append(",\"getcolors_ms_p50\":").Append(PctD(gc, 0.5).ToString("F2", Inv))
              .Append(",\"getcolors_ms_p95\":").Append(PctD(gc, 0.95).ToString("F2", Inv))
              .Append(",\"getcolors_ms_max\":").Append((gc.Count > 0 ? gc[^1] : 0).ToString("F2", Inv))
              .Append(",\"latency_frames_p50\":").Append(lat.Count > 0 ? lat[lat.Count / 2] : 0)
              .Append(",\"latency_frames_max\":").Append(lat.Count > 0 ? lat[^1] : 0)
              .Append(",\"pairs_pushed\":").Append(phasePairs).Append(",\"pairs_busy\":").Append(phaseBusy)
              .Append(",\"skipped\":").Append(phaseSkipped).Append(",\"not_created\":").Append(phaseNotCreated)
              .Append(",\"bad_size\":").Append(phaseBadSize).Append(",\"errors\":").Append(phaseErrors)
              .Append(",\"thermal_status\":").Append(ThermalStatus());
            if (core != IntPtr.Zero)
            {
                var buf = new byte[4096];
                var st = Native.sp4_close(core, buf, (uint)buf.Length);   // un MCAP par phase, statistiques finales
                core = IntPtr.Zero;
                sb.Append(",\"close_status\":").Append(st).Append(",\"core\":").Append(Native.Str(buf));
            }
            sb.Append("}");
            phases!.WriteLine(sb.ToString());
        }

        void RunBench()
        {
            var buf = new byte[1024];
            Native.sp4_bench_encode(1280, 1280, (uint)cfg.benchImages, (uint)cfg.jpegQuality, buf, (uint)buf.Length);
            phases!.WriteLine("{\"phase\":\"Bench\",\"bench\":" + Native.Str(buf) + "}");
        }

        void Finish()
        {
            phase = Phase.Done;
            if (core != IntPtr.Zero)
            {
                var buf = new byte[4096];
                var st = Native.sp4_close(core, buf, (uint)buf.Length);
                core = IntPtr.Zero;
                phases?.WriteLine("{\"phase\":\"Close\",\"status\":" + st + ",\"core\":" + Native.Str(buf) + "}");
            }
            foreach (var a in new[] { left, right }) if (a != null) a.enabled = false;
            File.WriteAllText(Path.Combine(dir, "sp4_done.txt"), DateTime.UtcNow.ToString("o"));
            Log("SP-4 terminé : retirer le casque, lancer run_sp4.ps1");
            seconds?.Dispose(); phases?.Dispose();
        }

        void OnDestroy() { if (leftBuf.IsCreated) leftBuf.Dispose(); }

        void OnApplicationPause(bool paused) { if (paused && phase != Phase.Done) phases?.WriteLine("{\"event\":\"pause\"}"); }

        static float Pct(List<float> s, double q) => s.Count == 0 ? 0 : s[(int)Math.Round((s.Count - 1) * q)];
        static double PctD(List<double> s, double q) => s.Count == 0 ? 0 : s[(int)Math.Round((s.Count - 1) * q)];
        static double Avg(List<double> x) { double t = 0; foreach (var v in x) t += v; return x.Count == 0 ? 0 : t / x.Count; }
        static double Max(List<double> x) { double m = 0; foreach (var v in x) m = Math.Max(m, v); return m; }
    }
}
