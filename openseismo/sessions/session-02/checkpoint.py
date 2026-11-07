"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("vp/vs = sqrt(3) = 1.732 for Poisson's ratio 0.25", abs(L.vp_vs_ratio(0.25) - np.sqrt(3.0)) < 1e-12))
    checks.append(("typical speeds 6.0 / 3.5 = 1.714 are within 2 percent of sqrt(3)", abs(L.VP / L.VS - np.sqrt(3.0)) / np.sqrt(3.0) < 0.02))
    try:
        L.vp_vs_ratio(0.5)
        bad = False
    except ValueError:
        bad = True
    checks.append(("Poisson's ratio 0.5 (fluid limit) is rejected", bad))
    d = L.station_distances(L.STATIONS, L.QUAKE)
    checks.append(("worked example: distances are 69.46, 53.15, 58.52 km",
                   np.allclose(d, [69.462, 53.151, 58.523], atol=1e-3)))
    tp, ts = L.travel_time_curves(d)
    checks.append(("worked example: S-P gap at station A is 8.27 s and gives 69.5 km",
                   abs((ts - tp)[0] - 8.269) < 1e-3 and abs(float(L.distance_sp(ts[0], tp[0])) - d[0]) < 1e-9
                   and abs(8.27 * 8.4 - 69.5) < 0.05))
    est = L.trilaterate(L.STATIONS, L.distance_sp(ts, tp))
    checks.append(("worked example: three circles recover the epicentre (60, 35) km", np.allclose(est, [60.0, 35.0], atol=1e-9)))
    # hand calculation of the first row: 200 x = 12000 -> x = 60
    r2 = d ** 2
    checks.append(("hand calculation: first line is 200 x = 12000, so x = 60",
                   abs((r2[0] - r2[1] + 100.0 ** 2) - 12000.0) < 1e-6))
    pts = L.circle_intersections(L.STATIONS[0], d[0], L.STATIONS[1], d[1])
    checks.append(("two stations give two points: (60, 35) and its mirror (60, -35)",
                   len(pts) == 2 and any(np.allclose(p, [60, 35], atol=1e-6) for p in pts)
                   and any(np.allclose(p, [60, -35], atol=1e-6) for p in pts)))
    mirror = np.array([60.0, -35.0])
    checks.append(("the third station rejects the mirror point (126.6 km away, not 58.5)",
                   abs(np.linalg.norm(L.STATIONS[2] - mirror) - 126.6) < 0.1))
    checks.append(("circles that do not touch give no intersection; tangent circles give one",
                   L.circle_intersections((0, 0), 10, (100, 0), 10) == [] and len(L.circle_intersections((0, 0), 10, (20, 0), 10)) == 1))
    try:
        L.trilaterate([[0, 0], [50, 0], [100, 0]], [10.0, 40.0, 90.0])
        bad = False
    except ValueError:
        bad = True
    checks.append(("three stations on one line cannot fix the epicentre (rejected)", bad))
    g = ts - tp
    g[0] += 0.5
    off = L.trilaterate(L.STATIONS, L.distance_sp(g, 0.0))
    checks.append(("a 0.5 s error in one S-P gap moves the epicentre by about 3.6 km",
                   abs(np.linalg.norm(off - L.QUAKE) - 3.61) < 0.05))
    checks.append(("S-P gaps at the three stations are 8.27, 6.33 and 6.97 s", np.allclose(ts - tp, [8.269, 6.327, 6.967], atol=6e-3)))
    checks.append(("hand calculation: second line is 80 x + 180 y = 11100, solved by (60, 35)",
                   abs((r2[0] - r2[2] + 40.0 ** 2 + 90.0 ** 2) - 11100.0) < 1e-6 and abs(80 * 60 + 180 * 35 - 11100) < 1e-9))
    near = np.array([10.0, 10.0])
    g2 = L.station_distances(L.STATIONS, near) * (1 / L.VS - 1 / L.VP)
    g2[0] += 1.0
    est2 = L.trilaterate(L.STATIONS, L.distance_sp(g2, 0.0))
    checks.append(("a 1.0 s error at station A: quake at (10, 10) is off by 1.9 km, quake at (60, 35) by 7.4 km",
                   abs(np.linalg.norm(est2 - near) - 1.9) < 0.1))
    g3 = ts - tp
    g3[0] += 1.0
    e3 = L.trilaterate(L.STATIONS, L.distance_sp(g3, 0.0))
    checks.append(("(60, 35) with a 1.0 s error is off by 7.4 km", abs(np.linalg.norm(e3 - L.QUAKE) - 7.44) < 0.05))
    checks.append(("Poisson's ratio 0.242 reproduces 6.0 / 3.5", abs(L.vp_vs_ratio(0.242) - 6.0 / 3.5) < 1e-3))
    on_line = np.array([[0.0, 0.0], [100.0, 0.0], [50.0, 0.0]])
    try:
        L.trilaterate(on_line, [69.0, 53.0, 40.0])
        bad = False
    except ValueError:
        bad = True
    alt = np.array([[0.0, 0.0], [100.0, 0.0], [100.0, 90.0]])
    est_alt = L.trilaterate(alt, L.station_distances(alt, L.QUAKE))
    checks.append(("design: station (50, 0) is collinear and refused; (100, 90) works and finds (60, 35)",
                   bad and np.allclose(est_alt, [60.0, 35.0], atol=1e-9)))
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
