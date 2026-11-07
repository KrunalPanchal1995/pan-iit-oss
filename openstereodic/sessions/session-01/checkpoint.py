"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    u, v = L.project((0.02, 0.01, 0.5))
    checks.append(("hand calculation: u = 1000 * 0.02 / 0.5 = 40 px, v = 20 px", abs(u - 40) < 1e-9 and abs(v - 20) < 1e-9))
    checks.append(("doubling the depth halves the image coordinates", abs(L.project((0.02, 0.0, 1.0))[0] - u / 2) < 1e-9))
    d = L.disparity((0.02, 0.01, 0.5))
    checks.append((f"worked example: disparity f B / Z = 1000 * 0.04 / 0.5 = 80 px (got {d:.1f})", abs(d - 80.0) < 1e-9))
    checks.append(("worked example: depth from d = 80 px is 0.5 m", abs(L.depth_from_disparity(80.0) - 0.5) < 1e-12))
    checks.append(("disparity does not depend on the sideways position X",
                   abs(L.disparity((-0.1, 0.0, 0.8)) - L.disparity((0.3, 0.2, 0.8))) < 1e-9))
    zs = np.array([0.3, 0.7, 1.5, 4.0])
    ds = np.array([L.disparity((0.01, 0.0, z)) for z in zs])
    checks.append(("round trip: depth_from_disparity(disparity(Z)) = Z", np.allclose(L.depth_from_disparity(ds), zs)))
    checks.append(("a nearer point has a larger disparity", bool(np.all(np.diff(ds) < 0))))
    checks.append(("edge: disparity 0 means infinitely far", L.depth_from_disparity(0.0) == np.inf and L.depth_from_disparity(-3.0) == np.inf))
    try:
        L.project((0.0, 0.0, 0.0))
        behind = False
    except ValueError:
        behind = True
    checks.append(("edge: a point at Z = 0 is rejected", behind))
    checks.append(("one pixel of disparity at 0.5 m is about 6.2 mm of depth", abs(1000 * L.depth_step(0.5) - 6.17) < 0.05))
    checks.append(("depth step grows with distance", L.depth_step(2.0) > 10 * L.depth_step(0.5)))
    checks.append(("design answer: baseline 0.05 m gives a depth step of 4.95 mm at 0.5 m, 0.04 m gives 6.17 mm",
                   abs(1000 * L.depth_step(0.5, baseline=0.05) - 4.95) < 0.01 and abs(1000 * L.depth_step(0.5) - 6.17) < 0.01))
    checks.append(("hand calculation: f = 1000, B = 0.06, d = 25 px gives Z = 2.4 m", abs(L.depth_from_disparity(25.0, 1000.0, 0.06) - 2.4) < 1e-12))
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
