"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def _link_distance(L, q, c):
    """Smallest distance from point c to any link segment of the arm at joint angles q."""
    cum = np.cumsum(q)
    P = np.vstack([[0, 0], np.cumsum(L.LINKS[:, None] * np.stack([np.cos(cum), np.sin(cum)], axis=1), axis=0)])
    best = 1e9
    for i in range(3):
        ab = P[i + 1] - P[i]
        t = np.clip((c - P[i]) @ ab / (ab @ ab), 0, 1)
        best = min(best, float(np.linalg.norm(c - (P[i] + t * ab))))
    return best


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d = np.radians
    q = d([30, 40, -20])
    checks.append(("Jacobian at (30, 40, -20) degrees matches finite differences (error below 1e-7)",
                   np.abs(L.jacobian(q) - L.jacobian_fd(q)).max() < 1e-7))
    checks.append(("straight arm: Jacobian is [[0, 0, 0], [0.70, 0.40, 0.15]] by hand",
                   np.allclose(L.jacobian(d([0, 0, 0])), [[0, 0, 0], [0.70, 0.40, 0.15]])))
    checks.append(("straight arm: second singular value is 0 and manipulability is 0",
                   L.singular_values([0, 0, 0])[1] < 1e-12 and L.manipulability([0, 0, 0]) < 1e-12))
    q0 = np.array([0.3, 0.3, 0.3])
    qs, err, it = L.solve_ik((0.45, 0.20), q0)
    checks.append(("worked example: IK reaches (0.45, 0.20) m within 1e-9 m in 11 iterations",
                   err < 1e-9 and it == 11 and np.allclose(L.fk(qs), [0.45, 0.20], atol=1e-9)))
    e0 = np.array([0.45, 0.20]) - L.fk(q0)
    raw = L.dls_step(L.jacobian(q0), e0, 0.01)
    errs = [L.solve_ik((0.45, 0.20), q0, max_iter=k)[1] for k in (0, 1, 8, 9, 10)]
    checks.append(("worked example: start error 0.2006 m, first raw step 1.56 rad capped to 0.1 rad (error 0.1861 m)",
                   abs(np.linalg.norm(e0) - 0.2006) < 1e-4 and abs(np.abs(raw).max() - 1.56) < 0.01
                   and abs(errs[0] - 0.2006) < 1e-4 and abs(errs[1] - 0.1861) < 1e-4))
    checks.append(("worked example: errors after 8, 9, 10 iterations are 4.3e-4, 9.5e-7, 1.9e-9 m (fast final convergence)",
                   abs(errs[2] - 4.33e-4) < 1e-5 and abs(errs[3] - 9.5e-7) < 1e-7 and abs(errs[4] - 1.9e-9) < 2e-10))
    e25 = [L.solve_ik((0.45, 0.20), q0, max_iter=k)[1] for k in (2, 5)]
    checks.append(("worked example: start at (0.586, 0.347) m, raw step (-1.28, 1.56, 1.50) rad, errors 0.168 m after 2 and 0.091 m after 5 iterations",
                   np.allclose(L.fk(q0), [0.586, 0.347], atol=1e-3) and np.allclose(raw, [-1.283, 1.560, 1.495], atol=0.005)
                   and abs(e25[0] - 0.168) < 1e-3 and abs(e25[1] - 0.091) < 1e-3))
    checks.append(("worked example: final angles (-21.0, 60.7, 59.0) degrees",
                   np.allclose(np.degrees(L.solve_ik((0.45, 0.20), q0)[0]), [-21.05, 60.67, 59.02], atol=0.05)))
    checks.append(("stretched arm: largest singular value sqrt(0.70^2 + 0.40^2 + 0.15^2) = 0.82 m/rad",
                   abs(L.singular_values([0, 0, 0])[0] - np.sqrt(0.49 + 0.16 + 0.0225)) < 1e-12 and abs(L.singular_values([0, 0, 0])[0] - 0.82) < 1e-3))
    Jq = L.jacobian(q)
    checks.append(("a DLS step equals J^T (J J^T + lambda^2 I)^-1 e written out by hand",
                   np.allclose(L.dls_step(Jq, np.array([0.01, -0.02]), 0.05),
                               Jq.T @ np.linalg.inv(Jq @ Jq.T + 0.0025 * np.eye(2)) @ [0.01, -0.02])))
    speeds = []
    for eps in (0.1, 0.01, 0.001):
        qq = [0.0, eps, 0.0]
        speeds.append((L.singular_values(qq)[1], np.linalg.norm(L.joint_speeds(qq, [0.1, 0.0])),
                       np.linalg.norm(L.joint_speeds(qq, [0.1, 0.0], lam=0.05))))
    checks.append(("smallest singular value is 0.0156, 0.00156, 0.00016 for bends of 0.1, 0.01, 0.001 rad",
                   np.allclose([s[0] for s in speeds], [0.01562, 0.001562, 0.0001562], rtol=0.01)))
    checks.append(("pseudoinverse speeds for 0.1 m/s along the arm: 6.4, 64, 640 rad/s; damped (0.05): 0.57, 0.06, 0.01 rad/s",
                   np.allclose([s[1] for s in speeds], [6.39, 63.99, 639.87], rtol=0.01)
                   and np.allclose([s[2] for s in speeds], [0.57, 0.06, 0.01], atol=0.006)))
    checks.append(("pseudoinverse speed is about 0.1 / smallest singular value",
                   all(abs(s[1] * s[0] - 0.1) < 0.002 for s in speeds)))
    checks.append(("manipulability equals sqrt(det(J J^T))",
                   abs(L.manipulability(q) - np.sqrt(np.linalg.det(Jq @ Jq.T))) < 1e-12))
    grid = d(np.arange(0, 181, 15))
    best = max(L.manipulability([a, b, c]) for a in grid for b in grid for c in grid)
    checks.append(("largest manipulability on a 15 degree grid is about 0.133 m^2, the straight arm has 0", abs(best - 0.133) < 0.003))
    checks.append(("quintic timing: 0 at start, 1 at end, 0.5 in the middle, flat at both ends",
                   abs(L.quintic(0.0)) < 1e-15 and abs(L.quintic(1.0) - 1) < 1e-12 and abs(L.quintic(0.5) - 0.5) < 1e-12
                   and abs(L.quintic(1e-3)) < 1e-7 and abs(1 - L.quintic(1 - 1e-3)) < 1e-7))
    n = 401
    a_, b_ = np.array([0.25, -0.30]), np.array([0.25, 0.30])
    peak_q = np.linalg.norm(np.diff(L.line_path(a_, b_, n), axis=0), axis=1).max() / (2.0 / (n - 1))
    peak_c = np.linalg.norm(np.diff(L.line_path(a_, b_, n, L.cubic), axis=0), axis=1).max() / (2.0 / (n - 1))
    checks.append(("2 s move of 0.60 m: peak gripper speed 0.5625 m/s (quintic, 1.875 x mean) and 0.45 m/s (cubic, 1.5 x mean)",
                   abs(peak_q - 0.5625) < 1e-3 and abs(peak_c - 0.45) < 1e-3))
    pts = L.line_path(a_, b_, 41)
    qa = L.solve_ik(pts[0], [0.3, -0.3, 0.3])[0]
    plain = L.track_path(pts, qa)
    nul = L.track_path(pts, qa, null_gain=0.1)
    checks.append(("path validated: gripper error below 1e-6 m with and without null-space motion",
                   L.path_error(pts, plain) < 1e-6 and L.path_error(pts, nul) < 1e-6))
    checks.append(("joint limits: plain tracking swings a joint to 150.7 degrees, null-space motion keeps it to 102.8 degrees",
                   abs(np.degrees(np.abs(plain).max()) - 150.7) < 0.1 and abs(np.degrees(np.abs(nul).max()) - 102.8) < 0.1))
    checks.append(("the 2 s plain path peaks at 2.42 rad/s in one joint",
                   abs(np.abs(np.diff(plain, axis=0)).max() / (2.0 / 40) - 2.42) < 0.02))
    other = L.track_path(pts, L.solve_ik(pts[0], [0.3, 0.3, 0.3])[0])
    checks.append(("another elbow choice at the start (from q = 0.3, 0.3, 0.3) keeps plain tracking below 99.5 degrees",
                   abs(np.degrees(np.abs(other).max()) - 99.5) < 0.1 and L.path_error(pts, other) < 1e-6))
    warm = np.degrees(np.abs(np.diff(plain, axis=0)).max())
    alt = np.array([L.solve_ik(p, [0.3, -0.3, 0.3] if i % 2 else [0.3, 0.3, 0.3])[0] for i, p in enumerate(pts)])
    checks.append(("elbow flip: warm starts change a joint at most 6.9 degrees per step, alternating cold starts jump 249 degrees",
                   abs(warm - 6.93) < 0.1 and abs(np.degrees(np.abs(np.diff(alt, axis=0)).max()) - 249.0) < 1.0
                   and L.path_error(pts, alt) < 1e-6))
    qf, errf, _ = L.solve_ik((0.9, 0.0), q0)
    checks.append(("unreachable target (0.9, 0): the gripper stops within 2 mm of the boundary point (0.70, 0), error 0.2007 m",
                   abs(np.linalg.norm(L.fk(qf)) - 0.70) < 0.002 and abs(errf - 0.2007) < 0.001))
    q_lim, e_lim = L.multi_start((-0.50, 0.0), limit=d(120))
    q_free, e_free = L.multi_start((-0.50, 0.0))
    checks.append(("target (-0.50, 0) is reachable without limits but misses by 5.6 cm with +-120 degree limits",
                   e_free < 1e-9 and abs(e_lim - 0.0557) < 0.002 and np.abs(q_lim).max() <= d(120) + 1e-12))
    xs, _, mask = L.numeric_reach_map(d(120))
    inside = np.hypot(*np.meshgrid(xs, xs)) <= 0.70
    checks.append(("numerical reach map at +-120 degrees: 156 cells inside the disk, 0.859 of them reached",
                   inside.sum() == 156 and abs(mask[inside].mean() - 0.859) < 0.002))
    qq = L.solve_ik((0.45, 0.20), q0)[0]
    e1 = [L.link_error_effect(qq, np.eye(3)[i] * 0.001) * 1000 for i in range(3)]
    checks.append(("1 mm error in any single link moves the gripper by 1.000 mm", np.allclose(e1, 1.0, atol=1e-6)))
    checks.append(("1 mm error in all three links: 3.000 mm when stretched, 2.005 mm at the pose for (0.45, 0.20)",
                   abs(L.link_error_effect(np.zeros(3), [0.001] * 3) * 1000 - 3.0) < 1e-6
                   and abs(L.link_error_effect(qq, [0.001] * 3) * 1000 - 2.005) < 0.001))
    A, B, C, R = np.array([0.40, -0.20]), np.array([0.40, 0.20]), np.array([0.40, 0.0]), 0.06
    pv = C + np.array([0.07, 0.0])
    route = np.vstack([L.line_path(A, pv, 41)[:-1], L.line_path(pv, B, 41)])
    qr = L.track_path(route, L.solve_ik(A, q0, limit=d(120))[0], limit=d(120), null_gain=0.1)
    dense = np.vstack([A + (pv - A) * t for t in np.linspace(0, 1, 200)] + [pv + (B - pv) * t for t in np.linspace(0, 1, 200)])
    checks.append(("no-go zone (centre (0.40, 0), radius 0.06): the straight route hits the centre, a 0.07 m detour clears it and tracks within 1e-6 m",
                   min(np.linalg.norm(p - C) for p in L.line_path(A, B, 401)) < 1e-9
                   and min(np.linalg.norm(p - C) for p in dense) > R and L.path_error(route, qr) < 1e-6
                   and np.abs(qr).max() <= d(120) + 1e-9))
    checks.append(("a clearance margin of 0.03 m is not kept for the links on this route",
                   min(_link_distance(L, qv, C) for qv in qr) < R + 0.03))
    checks.append(("the route checks the gripper only: at some pose a link passes within 0.06 m of the zone centre",
                   min(_link_distance(L, qv, C) for qv in qr) < R))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
