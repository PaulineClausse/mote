import math

from mote import geometry as g


def col(m, j):
    return [m[i][j] for i in range(3)]


def apply_rot(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]


def close(a, b, tol=1e-12):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def test_quat_roundtrip():
    for q in [(0, 0, 0, 1), (0.5, -0.5, 0.5, -0.5), (0.1, 0.2, 0.3, 0.9), (0.9, 0.1, -0.3, 0.05)]:
        qn = g.quat_normalize(q)
        qn = qn if qn[3] >= 0 else tuple(-c for c in qn)
        assert close(g.matrix_quat(g.pose_matrix((0, 0, 0), q)), qn, 1e-12)


def test_unity_camera_axes_map_to_opencv():
    # caméra Unity tournée de 30° autour de y, à (1, 2, 3)
    a = math.radians(30)
    q = (0.0, math.sin(a / 2), 0.0, math.cos(a / 2))
    t = g.pose_matrix((1.0, 2.0, 3.0), q)
    cv = g.unity_to_canonical(t)
    flip = lambda v: [v[0], v[1], -v[2]]  # noqa: E731  monde Unity -> monde main droite
    # l'avant de la caméra Unity (+Z) est l'avant OpenCV (+z) ; le haut Unity (+Y) est -y OpenCV ; la droite reste
    assert close(col(cv, 2), flip(apply_rot(t, [0, 0, 1])))
    assert close([-c for c in col(cv, 1)], flip(apply_rot(t, [0, 1, 0])))
    assert close(col(cv, 0), flip(apply_rot(t, [1, 0, 0])))
    assert close(col(cv, 3), [1.0, 2.0, -3.0])
    # rotation propre (det = +1) : le repère canonique est bien main droite
    r = [row[:3] for row in cv[:3]]
    det = (r[0][0] * (r[1][1] * r[2][2] - r[1][2] * r[2][1]) - r[0][1] * (r[1][0] * r[2][2] - r[1][2] * r[2][0])
           + r[0][2] * (r[1][0] * r[2][1] - r[1][1] * r[2][0]))
    assert abs(det - 1) < 1e-12


def test_same_as_src3_formula():
    # SRC-3 (metaquest-3d-reconstruction, transforms.py) : R = Rc R_u Rc^T diag(1,-1,-1), p = Rc p, Rc = diag(1,1,-1)
    q = g.quat_normalize((0.1, 0.7, -0.2, 0.6))
    t = g.pose_matrix((0.3, 1.5, -2.0), q)
    rc = [[1, 0, 0], [0, 1, 0], [0, 0, -1]]
    ru = [row[:3] for row in t[:3]]
    mm = lambda a, b: [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]  # noqa: E731
    want = mm(mm(mm(rc, ru), rc), [[1, 0, 0], [0, -1, 0], [0, 0, -1]])
    cv = g.unity_to_canonical(t)
    assert all(close(cv[i][:3], want[i]) for i in range(3))
    assert close(col(cv, 3), [0.3, 1.5, 2.0])


def test_openxr_and_opengl_export():
    t = g.pose_matrix((1.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0))
    cv = g.openxr_to_canonical(t)                      # OpenXR regarde -Z ; OpenCV regarde +z
    assert close(col(cv, 2), [0, 0, -1]) and close(col(cv, 1), [0, -1, 0])
    assert g.canonical_to_opengl(cv) == t              # aller-retour exact


def test_invert_rigid_and_slerp():
    t = g.pose_matrix((1.0, -2.0, 0.5), g.quat_normalize((0.2, 0.1, 0.3, 0.9)))
    i = g.matmul(t, g.invert_rigid(t))
    assert all(close(i[r], g.IDENTITY[r], 1e-12) for r in range(4))
    q0, q1 = (0.0, 0.0, 0.0, 1.0), (0.0, math.sin(0.5), 0.0, math.cos(0.5))     # 1 rad autour de y
    mid = g.slerp(q0, q1, 0.5)
    assert close(mid, (0.0, math.sin(0.25), 0.0, math.cos(0.25)))
