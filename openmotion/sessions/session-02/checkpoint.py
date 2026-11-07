"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    tr = L.trip(2.0, 12.0, 10.0, 3.0)
    checks.append(("worked example: trip pieces last 6, 10, 4 s and cover 36, 120, 24 m (total 180 m, 20 s)",
                   np.allclose([tr["t1"], tr["t2"], tr["t3"], tr["d1"], tr["d2"], tr["d3"], tr["D"], tr["T"]],
                               [6, 10, 4, 36, 120, 24, 180, 20])))
    t = np.linspace(0, tr["T"], 4001)
    a, v, x = L.trip_state(t, tr)
    checks.append(("area under v-t equals the distance 180 m", abs(L.displacement_from_velocity(t, v) - 180.0) < 0.05))
    checks.append(("position at the end equals the area under v-t", abs(x[-1] - 180.0) < 1e-9))
    segs = L.acceleration_intervals(t, a)
    checks.append(("three intervals: speeding up, cruising, slowing down at 6 s and 16 s",
                   [s[2] for s in segs] == ["speeding up", "cruising", "slowing down"]
                   and abs(segs[0][1] - 6.0) < 0.01 and abs(segs[1][1] - 16.0) < 0.01))
    checks.append(("hand calculation: 20 m/s, 0.8 s, 6 m/s^2 needs 16 + 33.33 = 49.33 m",
                   abs(L.stopping_distance(20, 0.8, 6.0) - (16.0 + 400.0 / 12.0)) < 1e-9))
    vs = L.max_safe_speed(40, 0.8, 6.0)
    checks.append(("largest safe speed for 40 m is 17.63 m/s and it stops in exactly 40 m",
                   abs(vs - 17.63) < 0.01 and abs(L.stopping_distance(vs, 0.8, 6.0) - 40.0) < 1e-9))
    checks.append(("speed when reaching the hurdle at 40 m is 10.58 m/s",
                   abs(np.sqrt(L.final_speed_squared(20, -6.0, 24.0)) - 10.58) < 0.01))
    checks.append(("edge: zero reaction time reduces to braking distance v^2/(2a)",
                   abs(L.stopping_distance(15, 0.0, 5.0) - 22.5) < 1e-12))
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
