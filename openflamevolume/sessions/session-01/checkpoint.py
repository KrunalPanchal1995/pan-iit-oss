"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    P = L.triangulate(120.0, 80.0, 60.0, 800.0, 0.10)
    checks.append(("worked example: d = 40 px, f = 800 px, B = 0.10 m gives Z = 2.00 m",
                   abs(P[2] - 2.0) < 1e-12))
    checks.append(("worked example: X = 120 x 2 / 800 = 0.30 m and Y = 60 x 2 / 800 = 0.15 m",
                   abs(P[0] - 0.30) < 1e-12 and abs(P[1] - 0.15) < 1e-12))
    checks.append(("worked example: sigma_Z = 2^2 x 0.5 / (800 x 0.10) = 2.5 cm",
                   abs(L.depth_sigma(2.0, 800.0, 0.10, 0.5) - 0.025) < 1e-12))
    checks.append(("hand calculation: disparity of a point 1 m away is f B / Z = 80 px",
                   abs(L.disparity((0.2, 0.1, 1.0), 800.0, 0.10) - 80.0) < 1e-9))
    checks.append(("disparity halves when the depth doubles",
                   abs(L.disparity((0.0, 0.0, 4.0), 800.0, 0.1) - 0.5 * L.disparity((0.0, 0.0, 2.0), 800.0, 0.1)) < 1e-9))
    rng = np.random.default_rng(7)
    ok = True
    for _ in range(50):
        pt = np.array([rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0.5, 5)])
        xl, y = L.project(pt, 800.0, 0.0)
        xr, _ = L.project(pt, 800.0, 0.1)
        ok &= bool(np.allclose(L.triangulate(xl, xr, y, 800.0, 0.1), pt, atol=1e-9))
    checks.append(("round trip: project 50 random points into both cameras and triangulate them back", ok))
    checks.append(("a point on the same ray (twice as far) lands on the same left pixel: one photo cannot see depth",
                   np.allclose(L.project((0.3, 0.2, 1.5), 800.0), L.project((0.6, 0.4, 3.0), 800.0))))
    s1, s2 = L.depth_sigma(1.0, 800, 0.1, 0.5), L.depth_sigma(2.0, 800, 0.1, 0.5)
    checks.append(("depth error grows as Z squared: four times larger at 2 m than at 1 m", abs(s2 / s1 - 4.0) < 1e-12))
    checks.append(("doubling the baseline halves the depth error",
                   abs(L.depth_sigma(2.0, 800, 0.2, 0.5) / s2 - 0.5) < 1e-12))
    mc = np.std(L.monte_carlo_depth(2.0, 800.0, 0.10, 0.5))
    checks.append((f"Monte Carlo spread {100 * mc:.2f} cm agrees with the formula 2.50 cm within 3 percent", abs(mc / 0.025 - 1) < 0.03))
    bad = 0
    for call in (lambda: L.project((0, 0, 0), 800), lambda: L.triangulate(80, 80, 0, 800, 0.1),
                 lambda: L.triangulate(70, 80, 0, 800, 0.1)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs (Z = 0, zero or negative disparity) raise ValueError", bad == 3))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
