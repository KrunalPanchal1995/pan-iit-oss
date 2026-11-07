"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    H = L.FLAME["H"]
    zm = (np.arange(12) + 0.5) * H / 12
    checks.append(("worked example: exact volume pi x 15 x 10 x 60 / 2 mm^3 = 14.137 cm^3",
                   abs(L.true_volume() * 1e6 - np.pi * 15 * 10 * 60 / 2 / 1000) < 1e-9 and abs(L.true_volume() * 1e6 - 14.137) < 1e-3))
    checks.append(("12 slices of the exact area (midpoint rule) add up to the exact volume",
                   abs(L.volume_from_areas(L.true_area(zm), H / 12) / L.true_volume() - 1) < 1e-9))
    checks.append(("shoelace: unit square has area 1 and a 2000-gon circle of radius 1 has area pi",
                   abs(L.shoelace([0, 1, 1, 0], [0, 0, 1, 1]) - 1) < 1e-12
                   and abs(L.shoelace(np.cos(np.linspace(0, 2 * np.pi, 2000, endpoint=False)),
                                      np.sin(np.linspace(0, 2 * np.pi, 2000, endpoint=False))) - np.pi) < 1e-5))
    R_ok = True
    for phi in (0, 90, 137, 270):
        cl, cr, R = L.stereo_pair(phi)
        R_ok &= bool(np.allclose(R @ R.T, np.eye(3))
                     and abs(np.linalg.norm(cr - cl) - L.BASE) < 1e-12)
        mid = 0.5 * (cl + cr)
        R_ok &= bool(np.allclose(np.hypot(mid[0], mid[1]), L.DIST))
    checks.append(("camera pairs: rotation is orthonormal, baseline is 3 cm, distance to the axis is 30 cm", R_ok))
    # round trip: take real surface points seen by a camera, project into both cameras, triangulate back
    cl, cr, R = L.stereo_pair(40.0)
    hits = L.ray_hits(cl, R)
    ok = np.isfinite(hits[..., 0])
    idx = np.argwhere(ok)[::97]
    f, (rows, cols) = L.F_PX, L.SHAPE
    cy, cx = (rows - 1) / 2, (cols - 1) / 2
    ms, P = [], []
    for r, c in idx:
        p = hits[r, c]
        xc = R @ (p - cl)
        xr = R @ (p - cr)
        ms.append((cy - f * xc[1] / xc[2] + 0 * r, cx + f * xc[0] / xc[2], f * (xc[0] / xc[2] - xr[0] / xr[2]), 1.0))
        P.append(p)
    back = L.triangulate_world(np.array(ms), cl, R)
    checks.append((f"round trip: {len(P)} surface points projected into both cameras triangulate back within 0.01 mm",
                   len(P) > 20 and np.max(np.abs(back - np.array(P))) < 1e-5))
    rho = L.normalised_radius(L.texture_dots(n=500))
    checks.append(("the painted dots lie on the true surface: normalised radius = 1", np.allclose(rho[np.isfinite(rho)], 1.0, atol=1e-9)))
    ideal = L.texture_dots(n=20000, seed=1)
    v_ideal = L.volume_from_areas(L.slice_areas(ideal, H, 12), H / 12)
    checks.append((f"slicing alone is accurate: perfect surface points give a volume within 2 percent ({100 * (v_ideal / L.true_volume() - 1):+.1f} %)",
                   abs(v_ideal / L.true_volume() - 1) < 0.02))
    pts4 = L.reconstruct(4)
    rho4 = L.normalised_radius(pts4)
    rho4 = rho4[np.isfinite(rho4)]
    checks.append((f"4 pairs: median shape error |rho - 1| = {np.median(np.abs(rho4 - 1)):.3f} is below 0.03 (under 3 percent of the radius)",
                   len(pts4) > 800 and np.median(np.abs(rho4 - 1)) < 0.03))
    v4 = L.volume_from_areas(L.slice_areas(pts4, H, 12), H / 12)
    e4 = v4 / L.true_volume() - 1
    checks.append((f"4 pairs: volume {v4 * 1e6:.2f} cm^3 is within 10 percent of 14.14 cm^3 ({100 * e4:+.1f} %)", abs(e4) < 0.10))
    e1 = abs(L.volume_study(1)[1])
    e2 = abs(L.volume_study(2)[1])
    checks.append((f"more views, less error: |error| {100 * e1:.0f} % (1 pair) > {100 * e2:.0f} % (2 pairs) > {100 * abs(e4):.0f} % (4 pairs)",
                   e1 > e2 > abs(e4)))
    e3 = L.volume_study(3)[1]
    checks.append((f"mini-project: 3 pairs are the smallest number within 10 percent ({100 * e3:+.1f} %); 2 pairs are not ({100 * L.volume_study(2)[1]:+.1f} %)",
                   abs(e3) < 0.10 and abs(L.volume_study(2)[1]) > 0.10))
    checks.append(("reconstruction is deterministic for a fixed seed", np.allclose(L.reconstruct(1)[:20], L.reconstruct(1)[:20])))
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
