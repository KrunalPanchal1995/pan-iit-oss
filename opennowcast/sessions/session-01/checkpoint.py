"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("the picture is 100 x 100 pixels of 1 km, one picture every 5 minutes",
                   L.N == 100 and L.PX_KM == 1.0 and L.DT_MIN == 5.0))
    f = L.gauss_cell(50, 50, 6.0, 40.0)
    checks.append(("a cell has its peak rain rate at its centre (40 mm/h)", f.shape == (100, 100) and abs(f[50, 50] - 40.0) < 1e-9 and f.max() == f[50, 50]))
    cx, cy = L.centroid(L.gauss_cell(45.0, 38.0, 6.0, 40.0))
    checks.append(("the rain-weighted centre of a cell is where we put it", abs(cx - 45.0) < 1e-6 and abs(cy - 38.0) < 1e-6))
    u, v, sp, ang = L.wind_from_shift(3, 0)
    checks.append(("worked example: 3 pixels east in 5 minutes is 36 km/h towards the east", abs(u - 36.0) < 1e-9 and abs(v) < 1e-9 and abs(sp - 36.0) < 1e-9 and abs(ang) < 1e-9))
    u1, _, _, _ = L.wind_from_shift(1, 0)
    checks.append(("hand calculation: 1 pixel in 5 minutes is 12 km/h", abs(u1 - 12.0) < 1e-9))
    t, miss = L.closest_approach((20.0, 50.0), (36.0, 0.0), (56.0, 50.0))
    checks.append(("worked example: the cell centre reaches a town 36 km away after 60 minutes", abs(t - 60.0) < 1e-9 and abs(miss) < 1e-9))
    r = L.rain_edge_radius(6.0, 40.0, 5.0)
    checks.append(("worked example: the 5 mm/h edge of the cell is 12.24 km from its centre", abs(r - 12.2361) < 1e-3))
    ft = L.first_rain_time((20.0, 50.0), (36.0, 0.0), (56.0, 50.0), 6.0, 40.0, 5.0)
    checks.append(("worked example: rain of 5 mm/h reaches the town after 39.6 minutes", ft is not None and abs(ft - 39.6) < 0.05))
    p = L.cell_position((20.0, 50.0), (36.0, 0.0), ft)
    checks.append(("at that time the town really is 5 mm/h", abs(L.rain_at((56.0, 50.0), p, 6.0, 40.0) - 5.0) < 1e-6))
    w2 = (36.0 * np.cos(np.radians(20)), 36.0 * np.sin(np.radians(20)))
    t2, miss2 = L.closest_approach((20.0, 50.0), w2, (56.0, 50.0))
    checks.append(("a wind turned by 20 degrees misses the town by 12.3 km (36 sin 20)", abs(miss2 - 36.0 * np.sin(np.radians(20))) < 1e-9 and abs(miss2 - 12.3) < 0.05))
    peak2 = L.rain_at((56.0, 50.0), L.cell_position((20.0, 50.0), w2, t2), 6.0, 40.0)
    checks.append(("with that miss the town only sees 4.87 mm/h at best, just under 5", abs(peak2 - 4.87) < 0.01 and peak2 < 5.0))
    checks.append(("so the 5 mm/h rain never arrives", L.first_rain_time((20.0, 50.0), w2, (56.0, 50.0), 6.0, 40.0, 5.0) is None))
    checks.append(("zero wind: the cell never arrives", L.closest_approach((0.0, 0.0), (0.0, 0.0), (10.0, 0.0))[0] == float("inf")
                   and L.first_rain_time((0.0, 0.0), (0.0, 0.0), (50.0, 0.0), 6.0, 40.0, 5.0) is None))
    checks.append(("a cell moving away from the town is closest right now (t = 0)", L.closest_approach((20.0, 50.0), (-36.0, 0.0), (56.0, 50.0))[0] == 0.0))
    checks.append(("a town that is already raining on gets time 0", L.first_rain_time((50.0, 50.0), (10.0, 0.0), (52.0, 50.0), 6.0, 40.0, 5.0) == 0.0))
    checks.append(("a cell weaker than the threshold never gives it", L.first_rain_time((20.0, 50.0), (36.0, 0.0), (56.0, 50.0), 6.0, 4.0, 5.0) is None))
    u5 = L.wind_from_shift(5, 0)[0]
    t5, _ = L.closest_approach((0.0, 0.0), (u5, 0.0), (45.0, 0.0))
    checks.append(("exercise: 5 pixels in 5 minutes is 60 km/h and a town 45 km away is reached in 45 minutes", abs(u5 - 60.0) < 1e-9 and abs(t5 - 45.0) < 1e-9))
    r5 = L.rain_edge_radius(6.0, 40.0, 5.0)
    ft20 = L.first_rain_time((56.0 - 36.0 * 20 / 60 - r5, 50.0), (36.0, 0.0), (56.0, 50.0), 6.0, 40.0, 5.0)
    checks.append(("design: for 20 minutes of warning the cell centre must be 12 + 12.24 = 24.24 km away at 36 km/h",
                   abs(36.0 * 20 / 60 + r5 - 24.24) < 0.01 and abs(ft20 - 20.0) < 1e-6))
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
