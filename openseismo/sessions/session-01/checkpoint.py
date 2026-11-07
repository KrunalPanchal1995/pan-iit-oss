"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("100 km at 6.0 km/s takes 16.7 s", abs(float(L.travel_time(100.0, 6.0)) - 16.667) < 1e-3))
    tp, ts = float(L.travel_time(100.0, L.VP)), float(L.travel_time(100.0, L.VS))
    checks.append(("worked example: station at 100 km sees P at 16.67 s, S at 28.57 s, gap 11.90 s",
                   abs(tp - 16.667) < 1e-3 and abs(ts - 28.571) < 1e-3 and abs((ts - tp) - 11.905) < 1e-3))
    checks.append(("worked example: gap 11.9 s gives back 100 km (hand: 11.905 * 8.4)",
                   abs(float(L.distance_from_gap(ts - tp)) - 100.0) < 1e-9 and abs(11.905 * 8.4 - 100.0) < 0.1))
    checks.append(("one second of gap is worth 8.4 km (6.0 * 3.5 / 2.5)", abs(L.km_per_second() - 8.4) < 1e-12))
    d = np.linspace(0, 300, 7)
    back = L.distance_from_gap(L.sp_gap(d))
    checks.append(("distance -> gap -> distance round trip is exact", np.allclose(back, d, atol=1e-9)))
    checks.append(("the gap is zero at the source", float(L.sp_gap(0.0)) == 0.0))
    g = L.sp_gap(np.array([50.0, 100.0, 200.0]))
    checks.append(("gap is proportional to distance (double the distance, double the gap)",
                   abs(g[1] / g[0] - 2.0) < 1e-12 and abs(g[2] / g[1] - 2.0) < 1e-12))
    checks.append(("a faster S wave (4.0 km/s) shrinks the gap at 100 km to 8.33 s",
                   abs(float(L.sp_gap(100.0, 6.0, 4.0)) - 8.333) < 1e-3))
    t, tr = L.synthetic_trace(100.0)
    quiet = np.abs(tr[t < 10.0]).max()
    checks.append(("synthetic trace is quiet before P and larger after S",
                   quiet < 0.2 and np.abs(tr[(t > 28.57) & (t < 35)]).max() > 0.5))
    checks.append(("a 15 s gap means 126 km", abs(float(L.distance_from_gap(15.0)) - 126.0) < 1e-9))
    checks.append(("at 300 km the gap is 35.7 s", abs(float(L.sp_gap(300.0)) - 35.714) < 1e-3))
    checks.append(("a 0.5 s timing error is worth 4.2 km", abs(0.5 * L.km_per_second() - 4.2) < 1e-9))
    checks.append(("thunder: sound at 343 m/s needs 2.9 s per kilometre", abs(1000.0 / 343.0 - 2.915) < 0.01))
    checks.append(("a 9 s flash-to-bang count is about 3 km", abs(9.0 * 343.0 / 1000.0 - 3.09) < 0.01))
    checks.append(("126 km: P needs 21.0 s, S needs 36.0 s", abs(126.0 / 6.0 - 21.0) < 1e-9 and abs(126.0 / 3.5 - 36.0) < 1e-9))
    checks.append(("slope of the gap line is 0.119 s per km", abs(float(L.sp_gap(1.0)) - 0.1190) < 5e-5))
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
