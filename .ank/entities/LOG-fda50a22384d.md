---
id: LOG-fda50a22384d
type: log
title: "Kit écrit dans docs/spikes/sp3/ : QRC v1.5.0 (649c012, Unity 6000.4.5f1) instrumenté par un seul"
created: 2026-10-13T08:05:59Z
author: claude-agent@mote-session
scope:
  - docs/spikes/**
about: TASK-eea12a7997da
seq: 1
schema: 4
version: 1
---

 fichier (chrono Export, latence AsyncGPUReadback en ms et frames, callback avec copie), paquet à part com.t34400.QuestRealityCapture.sp3 ; build batchmode + adb install (build_qrc.ps1) ; capture devant un mur texturé à 0,5/1/2/3 m mesurés au mètre ; run_sp3.ps1 : adb pull + analyze.py (résolution/cadence depuis les descripteurs à pleine cadence, plan ajusté au centre, erreur après décalage constant, rétroprojection de S1 en PLY). Règle fixée dans SP-3.md §2 avant mesure. Tests synthétiques : 7/7 + bout en bout.
