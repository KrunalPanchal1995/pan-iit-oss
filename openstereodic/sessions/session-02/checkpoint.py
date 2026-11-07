"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    X, Y, Z = L.triangulate(200.0, 100.0, 120.0)
    checks.append((f"worked example: (200, 100) and uR = 120 give X 0.02, Y 0.01, Z 0.5 m (got {float(X):.4f}, {float(Y):.4f}, {float(Z):.4f})",
                   abs(X - 0.02) < 1e-9 and abs(Y - 0.01) < 1e-9 and abs(Z - 0.5) < 1e-9))
    p = (-0.03, 0.02, 0.8)
    back = L.triangulate(*L.project_pair(p))
    checks.append(("round trip: project then triangulate returns the point", np.allclose([float(b) for b in back], p)))
    e = L.depth_error(0.5, 0.05)
    checks.append((f"worked example: depth error at 0.5 m for 0.05 px = 0.25 * 0.05 / 40 = 0.3125 mm (got {1000 * e:.4f})", abs(e - 0.25 * 0.05 / 40.0) < 1e-12))
    d = L.F * L.BASE / 0.5
    exact = L.F * L.BASE / (d - 0.05) - 0.5
    checks.append(("first-order depth error is within 1 percent of the exact change", abs(exact - e) / e < 0.01))
    B = L.baseline_for(0.5, 0.0002, 0.05)
    checks.append((f"hand calculation: baseline for 0.2 mm at 0.5 m with 0.05 px is 62.5 mm (got {1000 * B:.1f})", abs(B - 0.0625) < 1e-9))
    checks.append(("with that baseline the depth error is 0.2 mm", abs(L.depth_error(0.5, 0.05, baseline=B) - 0.0002) < 1e-9))
    checks.append(("doubling the distance quadruples the depth error", abs(L.depth_error(1.0, 0.05) / L.depth_error(0.5, 0.05) - 4) < 1e-9))
    x, y, z = L.triangulate(150.0, 80.0, 150.0)
    checks.append(("edge: zero disparity gives no depth (NaN)", bool(np.isnan(z))))

    sp = L.make_speckle_1d(120, seed=3)
    left = L.draw_row(sp, 120, 0.0)
    checks.append(("an unshifted row matches itself with correlation 1", abs(L.zncc(left[50:71], left[50:71]) - 1.0) < 1e-12))
    flat = np.full(21, 100.0)
    checks.append(("edge: a flat patch has correlation 0, not an error", L.zncc(flat, left[50:71]) == 0.0))
    right = L.draw_row(sp, 120, 3.0)
    checks.append(("a whole-pixel shift of 3 is found within 0.1 px", abs(L.match_subpixel(left, right, 60) - 3.0) < 0.1))
    neg = L.draw_row(sp, 120, -2.4)
    checks.append(("a negative shift of -2.4 px is found within 0.15 px", abs(L.match_subpixel(left, neg, 60) + 2.4) < 0.15))
    bright = 0.5 * L.draw_row(sp, 120, 3.0) + 40.0
    checks.append(("matching ignores brightness and contrast changes", abs(L.match_subpixel(left, bright, 60) - L.match_subpixel(left, right, 60)) < 1e-6))
    try:
        L.match_subpixel(left, L.draw_row(sp, 120, 9.0), 60, 10, 8)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge: a shift beyond the search range is reported, not guessed", raised))

    errs, whole = [], []
    for seed in range(20):
        s = L.make_speckle_1d(120, seed=seed)
        lf = L.draw_row(s, 120, 0.0)
        for t in (0.15, 0.3, 0.45, 0.7):
            rt = L.draw_row(s, 120, t)
            errs.append(L.match_subpixel(lf, rt, 60) - t)
            ks, c = L.correlation_curve(lf, rt, 60)
            whole.append(ks[np.argmax(c)] - t)
    rs, rw = float(np.sqrt(np.mean(np.square(errs)))), float(np.sqrt(np.mean(np.square(whole))))
    checks.append((f"sub-pixel error (RMS {rs:.3f} px) is at least 4 times smaller than whole-pixel error (RMS {rw:.3f} px)", rs * 4 < rw))
    t = np.array([0.0, 0.5, 1.0, 0.3])
    pb = L.parabola_bias(t, 1.5)
    checks.append(("parabola bias model is zero at fractional shifts 0 and 0.5", abs(pb[0]) < 1e-12 and abs(pb[1]) < 1e-12))
    checks.append(("parabola bias model is odd about 0.5: bias(0.3) = -bias(0.7)", abs(pb[3] + L.parabola_bias(0.7, 1.5)) < 1e-12))
    checks.append(("bigger dots give a smaller predicted bias", abs(L.parabola_bias(0.3, 3.0)) < abs(L.parabola_bias(0.3, 1.0))))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
