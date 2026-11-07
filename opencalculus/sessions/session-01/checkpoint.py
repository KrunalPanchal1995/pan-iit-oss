"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    steady = L.knot_speeds(10.0, 10.0, 10.0)
    checks.append(("steady 10 m/s for 2 s (t = 2 to 4) covers 20 m", abs(float(L.distance(4.0, steady) - L.distance(2.0, steady)) - 20.0) < 1e-9))
    checks.append(("start: distance 0 and speed 0", float(L.distance(0.0, steady)) == 0.0 and float(L.speed(0.0, steady)) == 0.0))
    v = L.knot_speeds(10.0, 14.0, 6.0)
    # hand calculation: trapezoids (0+10)/2*2 = 10, (10+14)/2*2 = 24, (14+6)/2*2 = 20 -> 10, 34, 54
    d = L.distance_at_knots(v)
    checks.append(("worked example: distances at knots are 0, 10, 34, 54 m", np.allclose(d, [0, 10, 34, 54])))
    checks.append(("distance(t) agrees with the knot table", np.allclose(L.distance(L.KNOT_T, v), d)))
    # middle of a slice: t = 1 s, speed 5 m/s, area of a triangle 0.5 * 1 * 5 = 2.5 m
    checks.append(("half-way through the first slice: 2.5 m", abs(float(L.distance(1.0, v)) - 2.5) < 1e-9))
    checks.append(("speed at t = 3 s is 12 m/s", abs(float(L.speed(3.0, v)) - 12.0) < 1e-9))
    checks.append(("slope of the distance graph at t = 3 s is 12 m/s", abs(L.slope_of_distance(3.0, v) - 12.0) < 1e-6))
    checks.append(("slope of the distance graph at t = 1 s is 5 m/s", abs(L.slope_of_distance(1.0, v) - 5.0) < 1e-6))
    # edge: car that stops has zero slope and distance stops growing
    stop = L.knot_speeds(10.0, 0.0, 0.0)
    checks.append(("a stopped car adds no distance", abs(float(L.distance(6.0, stop)) - float(L.distance(4.0, stop))) < 1e-9))
    checks.append(("distance never decreases for non-negative speeds", bool(np.all(np.diff(L.distance(np.linspace(0, 6, 61), v)) >= 0))))
    # second example: a car that starts already moving (issue: second example car)
    mv = L.knot_speeds(10.0, 14.0, 6.0, v0=8.0)
    dm = L.distance_at_knots(mv)
    checks.append((f"moving start: v0 = 8 m/s gives distances 0, 18, 42, 62 m at the knots (got {np.round(dm, 3).tolist()})",
                   np.allclose(dm, [0, 18, 42, 62])))
    checks.append(("moving start: speed at t = 0 is v0 and the default v0 is still 0",
                   float(L.speed(0.0, mv)) == 8.0 and float(L.knot_speeds(1, 2, 3)[0]) == 0.0))
    checks.append(("moving start: distance(1 s) = 8 * 1 + 0.5 * 1 * 1 = 8.5 m, and the tangent slope there is 9 m/s",
                   abs(float(L.distance(1.0, mv)) - 8.5) < 1e-12 and abs(L.slope_of_distance(1.0, mv) - 9.0) < 1e-6))
    checks.append(("moving start: a steady 12 m/s from the start gives exactly 12 * 6 = 72 m",
                   abs(float(L.distance_at_knots(L.knot_speeds(12.0, 12.0, 12.0, v0=12.0))[-1]) - 72.0) < 1e-12))
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
