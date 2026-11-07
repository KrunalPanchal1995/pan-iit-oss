"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    x5, v5 = float(L.position(5, 0, 4, 2)), float(L.velocity(5, 4, 2))
    checks.append(("worked example: v0 = 4 m/s, a = 2 m/s^2 gives x = 45 m and v = 14 m/s at 5 s",
                   abs(x5 - 45.0) < 1e-9 and abs(v5 - 14.0) < 1e-9))
    checks.append(("slope of x-t at 5 s equals the velocity 14 m/s",
                   abs(L.slope(lambda u: L.position(u, 0, 4, 2), 5.0) - 14.0) < 1e-6))
    checks.append(("area under v-t from 0 to 5 s equals the distance 45 m",
                   abs(L.area(lambda u: L.velocity(u, 4, 2), 0, 5) - 45.0) < 1e-6))
    checks.append(("slope of v-t equals the acceleration 2 m/s^2",
                   abs(L.slope(lambda u: L.velocity(u, 4, 2), 3.0) - 2.0) < 1e-6))
    ts = L.stop_time(10, -2)
    checks.append(("hand calculation: braking from 10 m/s at -2 m/s^2 stops at 5 s after 25 m",
                   abs(ts - 5.0) < 1e-12 and abs(float(L.position(ts, 0, 10, -2)) - 25.0) < 1e-9))
    checks.append(("edge: a = 0 gives constant velocity and a straight x-t line",
                   np.allclose(L.velocity([0, 3, 9], 5, 0), 5) and abs(float(L.position(3, 1, 5, 0)) - 16.0) < 1e-12))
    checks.append(("area below the axis counts negative: v = -3 m/s for 4 s is -12 m",
                   abs(L.area(lambda u: L.velocity(u, -3, 0), 0, 4) + 12.0) < 1e-9))
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
