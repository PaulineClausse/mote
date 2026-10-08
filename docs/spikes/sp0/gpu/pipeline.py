#!/usr/bin/env python3
"""SfM REF de SP-0 sur un PC NVIDIA, de bout en bout, pour toutes les sessions d'un dossier.

Outil de spike jetable, pas du code mote. Appelé par run_all.ps1, qui prépare Python ; lancé seul :

  python pipeline.py --data <sessions> --work <sorties> --tools <outils> [--dry-run]

Pour chaque session trouvée sous --data, dans --work/<session>/ (PROTOCOL.md §5 et §6, GPU_RUN.md annexe) :
  1. export      mq3drecon export-colmap, poses du casque (option A), sans --use-optimized-color-dataset
                 (session brute seulement ; un export déjà fait, images/ + distorted/sparse/0, est repris tel quel)
  2. est_txt     modèle du casque converti en texte
  3. by_eye      images_by_eye/left|right en liens physiques, pour une caméra par œil
  4. SfM REF     feature_extractor, matcher, mapper, chronométrés, SIFT sur GPU
  5. post_ref    modèle REF qui recale le plus d'images, Sim(3) casque contre REF (deux yeux, gauche, droite),
                 erreurs en mètres, temps du SfM, ref_flat/ pour l'entraînement « A sur poses REF »
Chaque étape réussie laisse un marqueur dans <session>/.steps/ : relancer reprend où ça s'est arrêté.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC3_REPO = "t-34400/metaquest-3d-reconstruction"
SRC3_COMMIT = "97d15f77ce24a4b6121b1e9d2b71513bcf3318e0"     # celui de l'export S0/S1 (SP-0.md §4)
COLMAP_TAG = "4.2.1"                                         # celui du REF S0/S1 sur le Mac (SP-0.md §4)
COLMAP_URL = "https://github.com/colmap/colmap/releases/download/{tag}/colmap-x64-windows-cuda.zip"
IMG_EXTS = {".png", ".jpg", ".jpeg"}

DRY = False


def say(msg: str) -> None:
    print(f"[sp0-gpu {datetime.datetime.now():%H:%M:%S}] {msg}", flush=True)


class StepError(RuntimeError):
    pass


# ----------------------------------------------------------------- exécution

def run_logged(cmd: list, log: Path, timings: Path | None = None, label: str | None = None) -> None:
    """Exécute cmd, recopie sa sortie (stdout + stderr) à l'écran et dans log, chronomètre si label.
    Le journal des temps a le format de run_timed.py : label, argv, wall_s, exit_code, start, host."""
    cmd = [str(c) for c in cmd]
    say(("DRY-RUN " if DRY else "") + (f"{label} : " if label else "") + subprocess.list2cmdline(cmd))
    if DRY:
        return
    log.parent.mkdir(parents=True, exist_ok=True)
    start = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    t0 = time.perf_counter()
    with open(log, "ab") as f:
        f.write(f"\n===== {start} {subprocess.list2cmdline(cmd)}\n".encode())
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            raise StepError(f"commande introuvable : {cmd[0]}")
        for chunk in iter(lambda: p.stdout.read1(65536), b""):
            sys.stdout.buffer.write(chunk)
            sys.stdout.flush()
            f.write(chunk)
        code = p.wait()
    wall = time.perf_counter() - t0
    if timings and label:
        rows = json.loads(timings.read_text()) if timings.exists() else []
        rows.append({"label": label, "argv": cmd, "wall_s": round(wall, 2), "exit_code": code,
                     "start": start, "host": platform.node()})
        timings.write_text(json.dumps(rows, indent=1))
    say(f"{label or Path(cmd[0]).name} : {wall:.1f} s, code {code}")
    if code != 0:
        raise StepError(f"{label or cmd[0]} a échoué (code {code}), journal : {log}")


def capture(cmd: list) -> tuple[int, str]:
    try:
        p = subprocess.run([str(c) for c in cmd], capture_output=True, timeout=120)
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as e:
        return 127, str(e)
    return p.returncode, (p.stdout + p.stderr).decode(errors="replace")


def download(url: str, dest: Path) -> None:
    say(f"téléchargement {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "mote-sp0"})
    with urllib.request.urlopen(req) as r, open(tmp, "wb") as f:
        total, done, last = int(r.headers.get("Content-Length") or 0), 0, 0.0
        while chunk := r.read(1 << 20):
            f.write(chunk)
            done += len(chunk)
            if total and time.time() - last > 5:
                say(f"  {done / 1e6:.0f} / {total / 1e6:.0f} Mo")
                last = time.time()
    tmp.replace(dest)


# ----------------------------------------------------------------- outils

class Colmap:
    def __init__(self, cmd: list[str]):
        self.cmd = cmd
        self.version = ""
        self.cuda = False
        self.gpu_extract = "FeatureExtraction.use_gpu"
        self.gpu_match = "FeatureMatching.use_gpu"

    def probe(self) -> bool:
        code, out = capture(self.cmd + ["-h"])
        m = re.search(r"COLMAP[^\n]*", out)
        if not m or code == 127:
            return False
        self.version = m.group(0).strip()
        self.cuda = "with CUDA" in out
        # avant COLMAP 3.11 : SiftExtraction / SiftMatching (PROTOCOL.md §6)
        _, ex = capture(self.cmd + ["feature_extractor", "-h"])
        if "FeatureExtraction.use_gpu" not in ex and "SiftExtraction.use_gpu" in ex:
            self.gpu_extract, self.gpu_match = "SiftExtraction.use_gpu", "SiftMatching.use_gpu"
        return True


def colmap_candidates(root: Path) -> list[list[str]]:
    out = []
    exe = next(iter(root.rglob("colmap.exe")), None)
    if exe:
        os.environ["PATH"] = str(exe.parent) + os.pathsep + os.environ["PATH"]   # DLL à côté de l'exe
        out.append([str(exe)])
    bat = next(iter(root.rglob("COLMAP.bat")), None)
    if bat:
        out.append([str(bat)])
    return out


def ensure_colmap(tools: Path, tag: str, allow_cpu: bool) -> Colmap:
    cands = []
    if os.environ.get("COLMAP"):
        cands.append([os.environ["COLMAP"]])
    cands += colmap_candidates(tools / "colmap" / tag) if (tools / "colmap" / tag).exists() else []
    if shutil.which("colmap"):
        cands.append([shutil.which("colmap")])
    for c in cands:
        cm = Colmap(c)
        if cm.probe() and (cm.cuda or allow_cpu):
            return cm
    if platform.system() != "Windows":
        raise StepError("COLMAP avec CUDA introuvable : l'installer (paquet ou build CUDA) et le mettre dans le PATH, "
                        "ou passer son chemin dans la variable COLMAP")
    if DRY:
        say(f"DRY-RUN téléchargement et extraction de COLMAP {tag} CUDA dans {tools / 'colmap' / tag}")
        return Colmap(["colmap"])
    z = tools / "downloads" / f"colmap-{tag}-windows-cuda.zip"
    if not z.exists():
        download(COLMAP_URL.format(tag=tag), z)
    dest = tools / "colmap" / tag
    say(f"extraction de COLMAP dans {dest}")
    with zipfile.ZipFile(z) as zf:
        members = [m for m in zf.namelist() if not m.endswith((".pdb", "_test.exe"))]
        zf.extractall(dest, members)
    for c in colmap_candidates(dest):
        cm = Colmap(c)
        if cm.probe():
            if not cm.cuda and not allow_cpu:
                raise StepError(f"{c[0]} n'annonce pas CUDA : {cm.version}")
            return cm
    raise StepError(f"COLMAP extrait dans {dest} ne démarre pas (essayer {dest}\\COLMAP.bat -h à la main)")


def ensure_src3(tools: Path) -> str:
    """mq3drecon dans le venv qui exécute ce script, installé depuis le commit de S0/S1."""
    scripts = Path(sys.executable).parent
    for name in ("mq3drecon.exe", "mq3drecon"):
        if (scripts / name).exists():
            return str(scripts / name)
    if DRY:
        say(f"DRY-RUN installation de SRC-3 {SRC3_COMMIT[:7]} dans le venv")
        return "mq3drecon"
    src = tools / "src" / f"metaquest-3d-reconstruction-{SRC3_COMMIT}"
    if not src.exists():
        z = tools / "downloads" / f"src3-{SRC3_COMMIT[:7]}.zip"
        if not z.exists():
            download(f"https://github.com/{SRC3_REPO}/archive/{SRC3_COMMIT}.zip", z)
        with zipfile.ZipFile(z) as zf:
            zf.extractall(tools / "src")
    uv = os.environ.get("UV") or shutil.which("uv")
    pip = [uv, "pip", "install", "--python", sys.executable] if uv else [sys.executable, "-m", "pip", "install"]
    run_logged(pip + ["-e", f"{src}[io,convert]"], tools / "install.log")
    for name in ("mq3drecon.exe", "mq3drecon"):
        if (scripts / name).exists():
            return str(scripts / name)
    raise StepError(f"mq3drecon absent de {scripts} après installation, journal : {tools / 'install.log'}")


def gpu_name() -> str:
    code, out = capture(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
    return out.strip() if code == 0 else ""


# ----------------------------------------------------------------- sessions

def is_raw(d: Path) -> bool:
    return (d / "hmd_poses.csv").is_file()


def est_model_dir(d: Path) -> Path | None:
    """Modèle du casque dans un export SRC-3 : distorted/sparse/0 (S0, S1), sinon le premier sparse/N trouvé."""
    for c in [d / "distorted" / "sparse" / "0", d / "sparse" / "0"]:
        if (c / "images.bin").exists() or (c / "images.txt").exists():
            return c
    for c in sorted(d.rglob("images.bin")) + sorted(d.rglob("images.txt")):
        if "ref" not in c.parts and "est_txt" not in c.parts:
            return c.parent
    return None


def is_export(d: Path) -> bool:
    return (d / "images").is_dir() and est_model_dir(d) is not None


def discover(data: Path) -> list[tuple[str, Path, str]]:
    """(nom, dossier, 'raw' | 'export'), sans descendre dans une session une fois trouvée."""
    found = []

    def walk(d: Path):
        if is_raw(d):
            found.append((d.name, d, "raw"))
        elif is_export(d):
            found.append((d.name, d, "export"))
        else:
            for c in sorted(p for p in d.iterdir() if p.is_dir()):
                walk(c)
    walk(data)
    names = [n for n, _, _ in found]
    return [(n if names.count(n) == 1 else f"{d.parent.name}_{n}", d, k) for n, d, k in found]


def list_images(images: Path) -> list[Path]:
    return sorted(p for p in images.rglob("*") if p.suffix.lower() in IMG_EXTS)


def eye_of(name: str) -> str:
    n = Path(name).name.lower()
    return "left" if n.startswith("left") else "right" if n.startswith("right") else "other"


def link_by_eye(images: Path, dest: Path) -> int:
    """images_by_eye/left|right en liens physiques (pas de droits admin, pas de copie) ; copie sinon."""
    imgs = list_images(images)
    for p in imgs:
        t = dest / eye_of(p.name) / p.name
        if t.exists():
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(p, t)
        except OSError:
            shutil.copy2(p, t)
    return len(imgs)


class Session:
    def __init__(self, name: str, src: Path, kind: str, work: Path):
        self.name, self.src, self.kind = name, src, kind
        self.dir = work / name
        self.export = self.dir / "export" if kind == "raw" else src
        self.ref = self.dir / "ref"
        self.logs = self.dir / "logs"
        self.timings = self.dir / "timings.json"

    def done(self, step: str) -> bool:
        return (self.dir / ".steps" / step).exists()

    def mark(self, step: str) -> None:
        if not DRY:
            (self.dir / ".steps").mkdir(parents=True, exist_ok=True)
            (self.dir / ".steps" / step).write_text(datetime.datetime.now().isoformat(timespec="seconds"))

    def step(self, step: str, fn) -> None:
        if self.done(step):
            say(f"{self.name} : {step} déjà fait")
            return
        say(f"{self.name} : {step}")
        fn()
        self.mark(step)


def process(s: Session, a, colmap: Colmap | None, mq3drecon: str | None, env: dict) -> dict:
    cm = colmap.cmd if colmap else ["colmap"]
    gpu = "1" if DRY or (colmap and colmap.cuda) else "0"
    s.dir.mkdir(parents=True, exist_ok=True)

    if s.kind == "raw":
        def export():
            if s.export.exists() and not DRY:
                shutil.rmtree(s.export)                       # export partiel d'un essai interrompu
            run_logged([mq3drecon, "export-colmap", "--project-dir", s.src, "--output-dir", s.export,
                        "--interval", a.interval], s.logs / "export.log", s.timings, "src3_export_colmap")
            if not DRY and not is_export(s.export):
                raise StepError(f"export SRC-3 sans images/ ni modèle dans {s.export}")
        s.step("export", export)

    def est_txt():
        m = est_model_dir(s.export)
        if m is None and DRY:
            m = s.export / "distorted" / "sparse" / "0"
        if (m / "images.txt").exists():
            (s.dir / "est_txt").mkdir(parents=True, exist_ok=True)
            for f in ("cameras.txt", "images.txt", "points3D.txt"):
                shutil.copy2(m / f, s.dir / "est_txt" / f)
            return
        (s.dir / "est_txt").mkdir(parents=True, exist_ok=True)
        run_logged(cm + ["model_converter", "--input_path", m, "--output_path", s.dir / "est_txt",
                         "--output_type", "TXT"], s.logs / "colmap.log")
    s.step("est_txt", est_txt)

    by_eye = s.ref / "images_by_eye"
    s.step("by_eye", lambda: say(f"  {0 if DRY else link_by_eye(s.export / 'images', by_eye)} images liées"))

    db = s.ref / "database.db"

    def extract():
        if db.exists() and not DRY:
            db.unlink()                                       # base partielle d'un essai interrompu
        s.ref.mkdir(parents=True, exist_ok=True)
        run_logged(cm + ["feature_extractor", "--database_path", db, "--image_path", by_eye,
                         "--ImageReader.camera_model", "OPENCV", "--ImageReader.single_camera_per_folder", "1",
                         f"--{colmap.gpu_extract if colmap else 'FeatureExtraction.use_gpu'}", gpu],
                   s.logs / "colmap.log", s.timings, "colmap_feature_extractor")
    s.step("feature_extractor", extract)

    def match():
        started = s.ref / ".matcher_started"
        if started.exists() and not DRY:
            # un appariement repris ne ferait que les paires restantes : temps partiel, faux pour SC-03
            say(f"{s.name} : appariement interrompu, extraction et appariement refaits pour un temps complet")
            extract()
        if not DRY:
            started.write_text("")
        flag = f"--{colmap.gpu_match if colmap else 'FeatureMatching.use_gpu'}"
        if a.matcher == "exhaustive":
            cmd = cm + ["exhaustive_matcher", "--database_path", db, flag, gpu]
        else:
            cmd = cm + ["sequential_matcher", "--database_path", db, flag, gpu,
                        "--SequentialMatching.overlap", "20"]
        run_logged(cmd, s.logs / "colmap.log", s.timings, "colmap_matcher")
        if not DRY:
            started.unlink()
    s.step("matcher", match)

    def mapper():
        sparse = s.ref / "sparse"
        if sparse.exists() and not DRY:
            shutil.rmtree(sparse)
        sparse.mkdir(parents=True, exist_ok=True)
        run_logged(cm + ["mapper", "--database_path", db, "--image_path", by_eye, "--output_path", sparse],
                   s.logs / "colmap.log", s.timings, "colmap_mapper")
    s.step("mapper", mapper)

    def to_txt():
        models = sorted(p for p in (s.ref / "sparse").iterdir() if p.is_dir()) if not DRY else [s.ref / "sparse" / "0"]
        for m in models:
            run_logged(cm + ["model_converter", "--input_path", m, "--output_path", m, "--output_type", "TXT"],
                       s.logs / "colmap.log")
    s.step("ref_txt", to_txt)

    if DRY:
        say(f"DRY-RUN post_ref : {s.dir / 'summary.json'}")
        return {"session": s.name, "dry_run": True}
    import post_ref
    return post_ref.summarize(s.dir, s.dir / "est_txt" / "images.txt", s.ref / "sparse", s.timings,
                              extra={"session": s.name, "source": str(s.src), "kind": s.kind,
                                     "interval": a.interval if s.kind == "raw" else None,
                                     "matcher": a.matcher, "sift_gpu": gpu == "1", "env": env})


# ----------------------------------------------------------------- main

def main(argv=None) -> int:
    global DRY
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, type=Path, help="dossier des sessions (brutes ou déjà exportées)")
    ap.add_argument("--work", required=True, type=Path, help="dossier des sorties, une sous-dossier par session")
    ap.add_argument("--tools", required=True, type=Path, help="dossier des outils téléchargés (COLMAP, SRC-3)")
    ap.add_argument("--interval", default="2", help="sous-échantillonnage de l'export SRC-3 (S0, S1 : 2)")
    ap.add_argument("--matcher", choices=["exhaustive", "sequential"], default="exhaustive",
                    help="exhaustive par défaut : le seul comparable aux temps S0 et S1 (SC-03)")
    ap.add_argument("--colmap-tag", default=COLMAP_TAG)
    ap.add_argument("--allow-cpu", action="store_true", help="accepter un COLMAP sans CUDA (temps non comparables)")
    ap.add_argument("--only", nargs="*", default=None, help="ne traiter que ces sessions (noms)")
    ap.add_argument("--dry-run", action="store_true", help="affiche les commandes sans rien exécuter")
    a = ap.parse_args(argv)
    DRY = a.dry_run
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")       # accents dans un journal ou un tube
    a.data, a.work, a.tools = a.data.resolve(), a.work.resolve(), a.tools.resolve()
    if platform.system() == "Windows" and not DRY:
        import ctypes                                   # pas de mise en veille pendant le calcul (temps SC-03)
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)   # CONTINUOUS | SYSTEM_REQUIRED
    sys.path.insert(0, str(HERE))

    if not a.data.is_dir():
        say(f"dossier de sessions introuvable : {a.data}. Y copier les sessions du casque (adb pull), puis relancer.")
        return 2
    sessions = [x for x in discover(a.data) if a.only is None or x[0] in a.only]
    if not sessions:
        say(f"aucune session sous {a.data} : il faut des dossiers contenant hmd_poses.csv (session brute) "
            f"ou images/ et distorted/sparse/0 (export SRC-3)")
        return 2
    for n, d, k in sessions:
        say(f"session {n} ({'brute' if k == 'raw' else 'export SRC-3'}) : {d}")

    gpu = gpu_name()
    say(f"GPU : {gpu or 'aucun GPU NVIDIA visible (nvidia-smi)'}")
    if not gpu and not a.allow_cpu and not DRY:
        say("arrêt : pas de GPU NVIDIA. Vérifier le pilote (nvidia-smi), ou --allow-cpu pour un REF sur CPU.")
        return 3
    try:
        colmap = ensure_colmap(a.tools, a.colmap_tag, a.allow_cpu)
        say(f"COLMAP : {colmap.version or colmap.cmd[0]} ({' '.join(colmap.cmd)})")
        mq3drecon = ensure_src3(a.tools) if any(k == "raw" for _, _, k in sessions) else None
    except StepError as e:
        say(f"arrêt pendant l'installation : {e}")
        return 4
    env = {"gpu": gpu, "colmap": colmap.version, "colmap_cmd": colmap.cmd, "python": platform.python_version(),
           "src3_commit": SRC3_COMMIT, "host": platform.node(), "os": platform.platform()}

    a.work.mkdir(parents=True, exist_ok=True)
    results, failed = [], []
    for n, d, k in sessions:
        s = Session(n, d, k, a.work)
        try:
            results.append(process(s, a, colmap, mq3drecon, env))
        except StepError as e:
            say(f"ÉCHEC {n} : {e}")
            failed.append(n)
    if not DRY:
        (a.work / "summary_all.json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
        import post_ref
        print(post_ref.table(results))
        say(f"résumé : {a.work / 'summary_all.json'}")
    if failed:
        say(f"sessions en échec : {', '.join(failed)}. Relancer la même commande reprend à l'étape en échec.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
