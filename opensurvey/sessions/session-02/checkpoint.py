"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    rh, his = L.hi_method(L.BOOK)
    rr, rises = L.rise_fall(L.BOOK)
    want = [100.000, 99.555, 99.110, 98.520, 98.520, 98.690, 99.030]
    checks.append(("worked example: height of instrument method gives 99.555, 99.110, 98.520, 98.690, 99.030",
                   np.allclose(rh, want, atol=1e-9)))
    checks.append(("worked example: first height of instrument is 101.425 m and the second 99.670 m",
                   abs(his[0] - 101.425) < 1e-9 and abs(his[4] - 99.670) < 1e-9))
    checks.append(("rise and fall gives the same levels as height of instrument", np.allclose(rh, rr, atol=1e-9)))
    checks.append(("rise and fall: first intermediate point is a fall of 0.445 m", abs(rises[1] + 0.445) < 1e-9))
    sb, sf, dr = L.arithmetic_check(L.BOOK, rh)
    checks.append(("worked example: sum BS 2.575 - sum FS 3.545 = -0.970 = last RL - first RL",
                   abs(sb - 2.575) < 1e-9 and abs(sf - 3.545) < 1e-9 and abs((sb - sf) - dr) < 1e-9 and abs(dr + 0.970) < 1e-9))
    bad = list(rh)
    bad[-1] += 0.010
    checks.append(("an arithmetic slip of 0.010 m in the last level breaks the check",
                   abs((sb - sf) - (bad[-1] - bad[0])) > 0.009))
    book2 = list(L.BOOK)
    book2[1] = ("IS", 1.970)           # misread intermediate sight (0.100 m too big)
    r2, _ = L.hi_method(book2)
    s1, s2, d2 = L.arithmetic_check(book2, r2)
    checks.append(("a wrong intermediate sight still passes the check but its own level is wrong by 0.100 m",
                   abs((s1 - s2) - d2) < 1e-9 and abs(r2[1] - rh[1] + 0.100) < 1e-9))
    checks.append(("worked example: S = 85.340 m at 7.5 degrees gives D = 84.610 m",
                   abs(L.horizontal_distance(85.340, 7.5) - 84.610) < 5e-4))
    p = L.total_station_point(1000.0, 5000.0, 50.0, 1.55, 1.80, 85.340, 7.5, 63.5)
    checks.append(("worked example: bearing 63.5 gives E = 1075.720 and N = 5037.753",
                   abs(p["E"] - 1075.720) < 5e-4 and abs(p["N"] - 5037.753) < 5e-4))
    checks.append(("worked example: the prism point is at RL 60.889 m", abs(p["RL"] - 60.889) < 5e-4))
    b, d = L.inverse(1000.0, 5000.0, p["E"], p["N"])
    checks.append(("the inverse returns the bearing 63.5 degrees and distance 84.610 m",
                   abs(b - 63.5) < 1e-9 and abs(d - 84.610) < 5e-4))
    checks.append(("hand calculation: S = 120.50 m at 12 degrees gives D = 117.87 m and V = 25.05 m",
                   abs(L.horizontal_distance(120.5, 12) - 117.87) < 5e-3 and abs(L.vertical_component(120.5, 12) - 25.05) < 5e-3))
    checks.append(("hand calculation: 50 m at bearing 245 degrees lands at E 954.68, N 4978.87",
                   abs(1000 + 50 * np.sin(np.radians(245)) - 954.68) < 5e-3 and abs(5000 + 50 * np.cos(np.radians(245)) - 4978.87) < 5e-3))
    b0, d0 = L.inverse(0.0, 0.0, 10.0, 0.0)
    checks.append(("edge: due east is bearing 90 degrees and due south is 180", abs(b0 - 90) < 1e-9 and abs(L.inverse(0, 0, 0, -5)[0] - 180) < 1e-9))
    checks.append(("edge: due west gives bearing 270 degrees (not -90)", abs(L.inverse(0, 0, -3, 0)[0] - 270) < 1e-9))
    checks.append(("edge: a level slope (0 degrees) gives D = S", abs(L.horizontal_distance(77.7, 0.0) - 77.7) < 1e-12))
    checks.append(("a 10 degree slope shortens the distance by 1.5 percent, a 25 degree slope by 9.4 percent",
                   abs((1 - np.cos(np.radians(10))) * 100 - 1.5) < 0.05 and abs((1 - np.cos(np.radians(25))) * 100 - 9.4) < 0.05))
    checks.append(("worked example: 2 mm x sqrt(24) = 9.80 mm, 2 mm x sqrt(25) = 10.00 mm (not below 10)",
                   abs(L.levelling_error(24, 2.0) - 9.798) < 5e-4 and abs(L.levelling_error(25, 2.0) - 10.0) < 1e-12))
    checks.append(("worked example: at most 24 set-ups, so spacing at least 41.7 m over 1 km",
                   L.max_setups(2.0, 10.0) == 24 and abs(L.min_spacing(1000.0, 2.0, 10.0) - 41.667) < 5e-3))
    checks.append(("a systematic 1 mm per set-up over 24 set-ups reaches 24 mm, far above 9.8 mm", 1.0 * 24 > 2 * L.levelling_error(24, 2.0)))
    checks.append(("Monte Carlo (seeded) agrees with 2 sqrt(24) within 2 percent",
                   abs(L.simulate_levelling(24, 2.0) / L.levelling_error(24, 2.0) - 1.0) < 0.02))
    checks.append(("design: 4 km with 1.5 mm per set-up allows 44 set-ups; 40 set-ups give 9.49 mm",
                   L.max_setups(1.5, 10.0) == 44 and abs(L.levelling_error(40, 1.5) - 9.487) < 5e-4))
    checks.append(("design: 4 km with 40 set-ups means staffs 100 m apart; the minimum spacing is 90.9 m",
                   abs(4000.0 / 40 - 100.0) < 1e-9 and abs(L.min_spacing(4000.0, 1.5, 10.0) - 90.909) < 5e-3))
    checks.append(("worked example: V = 85.340 sin 7.5 degrees = 11.139 m; (10 / 1.5)^2 = 44.4",
                   abs(L.vertical_component(85.340, 7.5) - 11.139) < 5e-4 and abs((10 / 1.5) ** 2 - 44.4) < 0.05))
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
