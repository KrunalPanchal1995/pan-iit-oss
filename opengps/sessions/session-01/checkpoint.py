"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    me = np.array([45.0, 25.0])
    r = L.ranges_from(me)
    checks.append(("distance 3-4-5 triangle", abs(L.distance((0, 0), (3, 4)) - 5.0) < 1e-12))
    c = L.circle_intersections(L.BEACONS[0], r[0], L.BEACONS[1], r[1])
    checks.append(("two circles meet at two points", len(c) == 2))
    got = sorted(map(tuple, np.round(c, 6).tolist()))
    checks.append(("worked example: circles 1 and 2 meet at (45, 25) and (45, 55) km",
                   np.allclose(got, [(45.0, 25.0), (45.0, 55.0)], atol=1e-6)))
    fix, miss = L.locate_2d(r)
    checks.append(("worked example: the third circle picks (45, 25) km", np.allclose(fix, me, atol=1e-6) and miss < 1e-6))
    far = float(abs(L.distance((45.0, 55.0), L.BEACONS[2]) - r[2]))
    checks.append(("the wrong candidate misses circle 3 by about 28.9 km", abs(far - 28.87) < 0.05))
    # hand calculation: a = (d^2 + r1^2 - r2^2) / (2 d) = 45, h = 15
    a = (120.0**2 + r[0]**2 - r[1]**2) / (2 * 120.0)
    checks.append(("hand calculation: a = 45 km and h = 15 km", abs(a - 45.0) < 1e-9 and abs(np.sqrt(r[0]**2 - a * a) - 15.0) < 1e-9))
    # edge cases
    t = L.circle_intersections((0, 0), 1.0, (2, 0), 1.0)
    checks.append(("tangent circles give one point", len(t) == 1 and np.allclose(t[0], (1.0, 0.0))))
    checks.append(("far apart circles give no point", len(L.circle_intersections((0, 0), 1.0, (5, 0), 1.0)) == 0))
    checks.append(("same centre gives no point", len(L.circle_intersections((0, 0), 1.0, (0, 0), 2.0)) == 0))
    # a ranging error shows up as a misfit
    _, m2 = L.locate_2d(r + np.array([0.0, 0.0, 2.0]))
    checks.append(("a 2 km error on range 3 leaves a misfit of about 2 km", abs(m2 - 2.0) < 0.05))
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
