#nullable enable
// SP-3 (mote) : copie instrumentée de Assets/RealityLog/Scripts/Runtime/IO/DepthRenderTextureExporter.cs,
// QuestRealityCapture v1.5.0 (commit 649c012), licence MIT. Remplace le fichier d'origine via build_qrc.ps1.
//
// Deux changements, rien d'autre :
//  1. Chronométrage, écrit dans <session>/depth_readback_timing.csv (une ligne par œil et par carte) :
//     export_cpu_ms   temps du thread principal dans Export (dispatch du compute shader + deux requêtes)
//     latency_ms      de la requête AsyncGPUReadback à l'appel du callback
//     latency_frames  même chose en frames Unity
//     callback_ms     temps du thread principal dans le callback : GetData + copie vers un tableau managé
//  2. La copie vers un tableau managé se fait dans le callback, pas dans le Task : le NativeArray de la requête
//     n'est garanti valide que pendant le callback. C'est aussi ce que fera l'hôte mote avant de pousser au core.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Threading.Tasks;
using Unity.Collections;
using UnityEngine;
using UnityEngine.Rendering;
using Debug = UnityEngine.Debug;

namespace RealityLog
{
    public class DepthRenderTextureExporter : IDisposable
    {
        private readonly ComputeShader computeShader;
        private readonly int kernel;

        private readonly Queue<GraphicsBuffer> bufferPool = new();
        private bool isDisposed = false;

        private readonly object bufferPoolLock = new();

        // ---- SP-3 : chronométrage ----
        private static readonly object timingLock = new();
        private static StreamWriter? timingWriter;
        private static string? timingPath;

        private static void WriteTiming(string depthPath, string eye, int width, int height, double exportCpuMs,
                                        double latencyMs, int latencyFrames, double callbackMs)
        {
            // <session>/left_depth/<t>.raw -> <session>/depth_readback_timing.csv
            var session = Path.GetDirectoryName(Path.GetDirectoryName(depthPath));
            if (session == null) return;
            var path = Path.Combine(session, "depth_readback_timing.csv");
            var inv = CultureInfo.InvariantCulture;
            lock (timingLock)
            {
                if (timingPath != path)
                {
                    timingWriter?.Dispose();
                    var isNew = !File.Exists(path);
                    timingWriter = new StreamWriter(path, append: true) { AutoFlush = true };
                    timingPath = path;
                    if (isNew)
                        timingWriter.WriteLine("file,eye,width,height,export_cpu_ms,latency_ms,latency_frames,callback_ms");
                }
                timingWriter!.WriteLine(string.Join(",", Path.GetFileName(depthPath), eye,
                    width.ToString(inv), height.ToString(inv), exportCpuMs.ToString("F3", inv),
                    latencyMs.ToString("F3", inv), latencyFrames.ToString(inv), callbackMs.ToString("F3", inv)));
            }
        }
        // ---- fin SP-3 ----

        public DepthRenderTextureExporter(ComputeShader computeShader)
        {
            this.computeShader = computeShader ?? throw new ArgumentNullException(nameof(computeShader));
            kernel = this.computeShader.FindKernel("CopyRT");
        }

        public void Export(RenderTexture sourceRT, string leftDepthOutputPath, string rightDepthOutputPath)
        {
            var exportWatch = Stopwatch.StartNew();   // SP-3
            if (isDisposed)
            {
                Debug.LogError("RenderTextureExporter has been disposed.");
                return;
            }

            if (sourceRT == null || !sourceRT.IsCreated())
            {
                Debug.LogError("RenderTexture is not created or null.");
                return;
            }

            var width = sourceRT.width;
            var height = sourceRT.height;
            var pixelCount = width * height;

            GraphicsBuffer leftEyeBuffer = GetOrCreateBuffer(pixelCount);
            GraphicsBuffer rightEyeBuffer = GetOrCreateBuffer(pixelCount);

            computeShader.SetTexture(kernel, "InputTex", sourceRT);
            computeShader.SetBuffer(kernel, "LeftEyeDepth", leftEyeBuffer);
            computeShader.SetBuffer(kernel, "RightEyeDepth", rightEyeBuffer);
            computeShader.SetInt("_Width", width);
            computeShader.SetInt("_Height", height);

            int groupsX = Mathf.CeilToInt(width / 8f);
            int groupsY = Mathf.CeilToInt(height / 8f);
            computeShader.Dispatch(kernel, groupsX, groupsY, 1);

            var exportCpu = new double[1];            // SP-3 : connu après les deux requêtes, lu dans les callbacks
            RequestGPUReadbackAndSave(leftEyeBuffer, leftDepthOutputPath, "left", width, height, exportCpu);
            RequestGPUReadbackAndSave(rightEyeBuffer, rightDepthOutputPath, "right", width, height, exportCpu);
            exportCpu[0] = exportWatch.Elapsed.TotalMilliseconds;
        }

        public void Dispose()
        {
            isDisposed = true;
            ClearAllBuffers();
            lock (timingLock) { timingWriter?.Dispose(); timingWriter = null; timingPath = null; }   // SP-3
        }

        private GraphicsBuffer GetOrCreateBuffer(int pixelCount)
        {
            lock (bufferPoolLock)
            {
                if (bufferPool.Count > 0)
                {
                    var pooledBuffer = bufferPool.Dequeue();

                    if (pooledBuffer.count == pixelCount)
                    {
                        return pooledBuffer;
                    }
                    else
                    {
                        pooledBuffer.Dispose();
                    }
                }
            }

            return new GraphicsBuffer(GraphicsBuffer.Target.Structured, pixelCount, sizeof(float));
        }

        private void ReturnBuffer(GraphicsBuffer buffer)
        {
            lock (bufferPoolLock)
            {
                if (isDisposed)
                {
                    buffer.Dispose();
                }
                else
                {
                    bufferPool.Enqueue(buffer);
                }
            }
        }

        private void ClearAllBuffers()
        {
            lock (bufferPoolLock)
            {
                while (bufferPool.Count > 0)
                {
                    var b = bufferPool.Dequeue();
                    b.Dispose();
                }
            }
        }

        private void RequestGPUReadbackAndSave(GraphicsBuffer buffer, string outputPath, string eye, int width,
                                               int height, double[] exportCpu)
        {
            var latencyWatch = Stopwatch.StartNew();  // SP-3
            var requestFrame = Time.frameCount;       // SP-3
            AsyncGPUReadback.Request(buffer, request =>
            {
                var latencyMs = latencyWatch.Elapsed.TotalMilliseconds;   // SP-3
                var latencyFrames = Time.frameCount - requestFrame;     // SP-3
                var callbackWatch = Stopwatch.StartNew();               // SP-3
                if (request.hasError)
                {
                    Debug.LogError("AsyncGPUReadback failed.");
                    ReturnBuffer(buffer);
                    return;
                }

                var data = request.GetData<float>().ToArray();   // SP-3 : copie dans le callback (voir l'en-tête)
                var callbackMs = callbackWatch.Elapsed.TotalMilliseconds;
                WriteTiming(outputPath, eye, width, height, exportCpu[0], latencyMs, latencyFrames, callbackMs);

                SaveAsRaw(data, outputPath, () => ReturnBuffer(buffer));
            });
        }

        private void SaveAsRaw(float[] data, string path, Action onComplete)
        {
            Task.Run(() =>
            {
                try
                {
                    int byteLength = data.Length * sizeof(float);
                    byte[] rawBytes = new byte[byteLength];
                    Buffer.BlockCopy(data, 0, rawBytes, 0, byteLength);
                    File.WriteAllBytes(path, rawBytes);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Failed to save raw data: {ex}");
                }
                finally
                {
                    onComplete?.Invoke();
                }
            });
        }
    }
}
