"""Poses, conversions de repère et interpolation, en Python pur (pas de numpy) : mêmes flottants sur toute machine,
d'où des sorties d'ingest identiques bit à bit (NFR-07).

Matrices 4x4 en listes de listes, ligne par ligne. Quaternions (x, y, z, w) comme dans `mote.v1.Pose3`.

Repère canonique (SPEC-64c5 §9.4) : monde main droite, métrique ; caméras OpenCV (x droite, y bas, z avant) ;
poses `world_from_camera`.
"""
from __future__ import annotations

import math

Mat = list[list[float]]

IDENTITY: Mat = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]

# Identifiant de la conversion appliquée, écrit dans le dataset. SPEC-64c5 §9.4 la donne comme hypothèse : WP-08 la
# valide (test de reprojection sur cible connue, SP-2). C'est aussi celle de SRC-3, avec laquelle SP-0 a validé H-01.
POSE_CONVERSION = "unity-flipz/v0"


def matmul(a: Mat, b: Mat) -> Mat:
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def diag(x: float, y: float, z: float) -> Mat:
    return [[x, 0.0, 0.0, 0.0], [0.0, y, 0.0, 0.0], [0.0, 0.0, z, 0.0], [0.0, 0.0, 0.0, 1.0]]


def quat_normalize(q: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    n = math.sqrt(sum(c * c for c in q))
    if n == 0.0:
        raise ValueError("quaternion nul")
    return (q[0] / n, q[1] / n, q[2] / n, q[3] / n)


def pose_matrix(p: tuple[float, float, float], q: tuple[float, float, float, float]) -> Mat:
    """Matrice 4x4 d'une position et d'un quaternion (x, y, z, w). La formule ne dépend pas de la latéralité du
    repère : un quaternion Unity tourne les vecteurs Unity par la même algèbre."""
    x, y, z, w = quat_normalize(q)
    return [
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), p[0]],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), p[1]],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), p[2]],
        [0.0, 0.0, 0.0, 1.0],
    ]


def matrix_quat(m: Mat) -> tuple[float, float, float, float]:
    """Quaternion (x, y, z, w), w ≥ 0, d'une matrice de rotation (méthode de Shepperd)."""
    t = m[0][0] + m[1][1] + m[2][2]
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        q = ((m[2][1] - m[1][2]) / s, (m[0][2] - m[2][0]) / s, (m[1][0] - m[0][1]) / s, 0.25 * s)
    elif m[0][0] > m[1][1] and m[0][0] > m[2][2]:
        s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2
        q = (0.25 * s, (m[0][1] + m[1][0]) / s, (m[0][2] + m[2][0]) / s, (m[2][1] - m[1][2]) / s)
    elif m[1][1] > m[2][2]:
        s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2
        q = ((m[0][1] + m[1][0]) / s, 0.25 * s, (m[1][2] + m[2][1]) / s, (m[0][2] - m[2][0]) / s)
    else:
        s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2
        q = ((m[0][2] + m[2][0]) / s, (m[1][2] + m[2][1]) / s, 0.25 * s, (m[1][0] - m[0][1]) / s)
    q = quat_normalize(q)
    return q if q[3] >= 0 else (-q[0], -q[1], -q[2], -q[3])


def invert_rigid(m: Mat) -> Mat:
    r = [[m[j][i] for j in range(3)] for i in range(3)]          # transposée
    t = [-sum(r[i][k] * m[k][3] for k in range(3)) for i in range(3)]
    return [r[0] + [t[0]], r[1] + [t[1]], r[2] + [t[2]], [0.0, 0.0, 0.0, 1.0]]


_FLIP_Z = diag(1.0, 1.0, -1.0)         # monde ou caméra Unity (main gauche) <-> main droite
_GL_TO_CV = diag(1.0, -1.0, -1.0)      # caméra OpenGL (y haut, regard -z) <-> OpenCV (y bas, regard +z)


def unity_to_canonical(world_from_camera: Mat) -> Mat:
    """Pose caméra Unity (monde main gauche, Y haut, caméra regardant +Z) vers le repère canonique.
    SPEC-64c5 §9.4 : T_gl = S T_unity S, S = diag(1, 1, -1, 1), puis caméra OpenGL vers OpenCV (inversion de y et z).
    La caméra Unity regarde +Z ; après S à droite, elle regarde -Z, comme une caméra OpenGL."""
    return matmul(matmul(matmul(_FLIP_Z, world_from_camera), _FLIP_Z), _GL_TO_CV)


def openxr_to_canonical(world_from_camera: Mat) -> Mat:
    """Pose caméra OpenXR (main droite, Y haut, regard -Z, comme OpenGL) vers le repère canonique."""
    return matmul(world_from_camera, _GL_TO_CV)


def canonical_to_opengl(world_from_camera_cv: Mat) -> Mat:
    """Repère canonique (caméra OpenCV) vers caméra OpenGL, pour nerfstudio (SPEC-64c5 §9.4, export)."""
    return matmul(world_from_camera_cv, _GL_TO_CV)


def lerp(a: float, b: float, s: float) -> float:
    return a + (b - a) * s


def slerp(q0: tuple, q1: tuple, s: float) -> tuple[float, float, float, float]:
    q0, q1 = quat_normalize(q0), quat_normalize(q1)
    d = sum(a * b for a, b in zip(q0, q1))
    if d < 0.0:
        q1, d = tuple(-c for c in q1), -d
    if d > 0.9995:
        return quat_normalize(tuple(lerp(a, b, s) for a, b in zip(q0, q1)))
    th = math.acos(d)
    s0, s1 = math.sin((1 - s) * th) / math.sin(th), math.sin(s * th) / math.sin(th)
    return quat_normalize(tuple(s0 * a + s1 * b for a, b in zip(q0, q1)))
