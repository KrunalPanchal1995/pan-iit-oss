"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("hand calculation: 10 m at 2 m/s with a = 1 m/s^2 takes 2 + 3 + 2 = 7 s",
                   np.allclose(L.ride_times(10, 2, 1), (2.0, 3.0, 2.0)) and abs(L.travel_time(10, 2, 1) - 7.0) < 1e-12))
    N_up = L.apparent_weight(60.0, 1.0)
    N_rest = L.apparent_weight(60.0, 0.0)
    checks.append(("worked example: a 60 kg person speeding up at 1.0 m/s^2 feels 648.6 N (588.6 N at rest)",
                   abs(N_up - 648.6) < 0.05 and abs(N_rest - 588.6) < 0.05))
    t = np.linspace(0, L.travel_time(21, 2, 1), 20001)
    v = np.array([L.speed_at(x, 21, 2, 1) for x in t])
    area = float(np.sum(0.5 * (v[1:] + v[:-1]) * np.diff(t)))
    checks.append(("the area under the speed-time graph equals the distance (21 m)", abs(area - 21.0) < 0.01))
    checks.append(("slowing down at 1 m/s^2 makes a 60 kg person feel lighter than at rest",
                   L.apparent_weight(60.0, -1.0) < L.apparent_weight(60.0, 0.0)))
    checks.append(("free fall (a = -g) gives zero floor force", abs(L.apparent_weight(60.0, -L.G)) < 1e-9))
    t1, tc, t2 = L.ride_times(3.0, 2.0, 1.0)
    top = 1.0 * t1
    checks.append(("short ride: no cruise, the top speed is lower than the limit (sqrt(3) = 1.73 m/s)",
                   tc == 0.0 and abs(top - np.sqrt(3.0)) < 1e-9 and top < 2.0))
    checks.append(("boundary: d = v^2/a exactly gives zero cruise time and no error",
                   abs(L.ride_times(4.0, 2.0, 1.0)[1]) < 1e-12))
    checks.append(("feel ratio 1 + a/g is 1 at rest and above 1 when speeding up",
                   L.feel_ratio(0.0) == 1.0 and L.feel_ratio(1.0) > 1.0))
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
