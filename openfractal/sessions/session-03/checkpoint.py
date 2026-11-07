"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    def status(c, m=3000):
        n, z, _ = L.escape_counts(np.array([c], dtype=complex), m)
        return int(n[0]), complex(z[0])

    checks.append(("c = 0 is inside", status(0)[0] == -1))
    checks.append(("c = 1 is outside (escapes at step 5 with bailout 256: orbit 0, 1, 2, 5, 26, 677)", status(1)[0] == 5))
    n_m1 = status(-1)[0]
    orb, z = [], 0j
    for _ in range(6):
        z = z * z - 1
        orb.append(z)
    checks.append(("c = -1 is inside and periodic: the orbit alternates -1, 0, -1, 0", n_m1 == -1 and orb == [-1, 0, -1, 0, -1, 0]))
    z = 0j
    for _ in range(40):
        z = z * z - 2
    checks.append(("c = -2 is on the boundary: it stays (orbit 0, -2, 2, 2, 2 ...) while -2.0001 escapes",
                   status(-2)[0] == -1 and abs(z - 2) < 1e-12 and status(-2.0001)[0] > 0))
    checks.append(("c = 0.25 (cusp) stays, c = 0.3 escapes", status(0.25)[0] == -1 and status(0.3)[0] > 0))

    # the vectorised answer equals a plain scalar loop
    pts = L.pixel_grid(complex(-0.5, 0), 3.4, 20, 12)
    n, _, _ = L.escape_counts(pts, 100)
    ref = np.full(pts.shape, -1)
    for i in range(pts.shape[0]):
        for j in range(pts.shape[1]):
            c, z = pts[i, j], 0j
            for k in range(1, 101):
                z = z * z + c
                if abs(z) > 256:
                    ref[i, j] = k
                    break
    checks.append(("vectorised counts equal a scalar loop pixel by pixel", np.array_equal(n, ref)))
    checks.append(("grid is centred: the mean of the pixel coordinates is the window centre",
                   abs(pts.mean() - complex(-0.5, 0)) < 1e-12))

    # hand-calculated smooth value
    n1, z1, _ = L.escape_counts(np.array([1 + 0j]), 50)
    nu1 = float(L.smooth_value(n1, z1)[0])
    checks.append((f"worked example: c = 1 gives n = 5, z = 677, nu = 6 - log2(ln 677) = 3.296 (got {nu1:.3f})",
                   int(n1[0]) == 5 and abs(nu1 - 3.2956) < 1e-3))
    g = np.linspace(0.5, 2, 3001) + 0j
    ng, zg, _ = L.escape_counts(g, 200)
    nug = L.smooth_value(ng, zg)
    checks.append(("smooth count: along the real axis it falls without jumps (largest step below 0.01) while n jumps by 1",
                   np.abs(np.diff(nug)).max() < 0.01 and np.abs(np.diff(ng)).max() == 1 and bool((np.diff(nug) <= 1e-12).all())))
    a = L.render(complex(-0.5, 0), 3.4, 60, 40, 200, 256.0)[0]
    b = L.render(complex(-0.5, 0), 3.4, 60, 40, 200, 10000.0)[0]
    both = ~np.isnan(a) & ~np.isnan(b)
    checks.append(("nu hardly depends on the bailout radius (256 versus 10000 differ by less than 1e-4)", np.abs(a - b)[both].max() < 1e-4))

    # cost
    w50 = L.render(complex(-0.5, 0), 3.4, 80, 50, 50)[1]
    w200 = L.render(complex(-0.5, 0), 3.4, 80, 50, 200)[1]
    checks.append(("cost grows with max_iter", w200 > w50))
    checks.append(("an inside pixel costs exactly max_iter updates", L.escape_counts(np.array([0j]), 123)[2] == 123))

    # Monte Carlo area
    ins = L.sample_inside(100000, 1000, 7)
    area, err = L.area_estimate(ins)
    checks.append((f"Monte Carlo area {area:.3f} +/- {err:.3f} is within 3 error bars + 0.01 of 1.5066",
                   abs(area - L.KNOWN_AREA) < 3 * err + 0.01))
    e4 = L.area_estimate(ins[:25000])[1]
    checks.append(("quadrupling N halves the error bar", abs(err / e4 - 0.5) < 0.05))
    checks.append(("area_estimate of all-inside is the full half-box doubled (5.75) with zero error",
                   L.area_estimate(np.ones(10, dtype=bool)) == (5.75, 0.0)))

    # floating-point limit
    centre = L.SEAHORSE
    checks.append(("width 1e-10: all 200 columns differ", L.distinct_columns(centre, 1e-10, 200) == 200))
    checks.append(("width 1e-15: columns collapse (fewer than 20 distinct of 200)", L.distinct_columns(centre, 1e-15, 200) < 20))
    checks.append(("deepest usable width in decade steps is 1e-13", abs(L.deepest_width(centre) / 1e-13 - 1) < 1e-9))

    # mini copy
    c3 = L.period3_centre()
    z = 0j
    for _ in range(3):
        z = z * z + c3
    checks.append(("period-3 centre c3 = -1.754878 returns to 0 after 3 steps", abs(c3 + 1.7548776662) < 1e-9 and abs(z) < 1e-9))
    checks.append(("mini copy window: 400 iterations mislabel less than 1% of pixels, 50 more than 5%",
                   L.mislabelled(c3, 0.05, 400) < 0.01 and L.mislabelled(c3, 0.05, 50) > 0.05))
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
