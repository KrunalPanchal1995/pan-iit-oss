"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    r = L.range_from(25.0, 35.0)
    h = L.peak_height(25.0, 35.0)
    t = L.time_of_flight(25.0, 35.0)
    checks.append((f"worked example: 25 m/s at 35 degrees gives R = 59.87 m, H = 10.48 m, T = 2.92 s (got {r:.2f}, {h:.2f}, {t:.2f})",
                   abs(r - 59.87) < 0.01 and abs(h - 10.48) < 0.01 and abs(t - 2.92) < 0.01))
    checks.append(("worked example: launching from 1.5 m adds 2.07 m of range at 25 m/s and 35 degrees",
                   abs(L.range_from(25.0, 35.0, 1.5) - r - 2.07) < 0.01))
    x, y, vx, vy = L.trajectory(t, 25.0, 35.0)
    checks.append(("the equations of motion land the ball at y = 0 with the same R and vy = -vy(0)",
                   abs(float(y)) < 1e-9 and abs(float(x) - r) < 1e-9 and abs(float(vy) + 25 * np.sin(np.radians(35))) < 1e-9))
    checks.append(("level-ground formula: R = v^2 sin(2a) / g",
                   abs(r - 25.0 ** 2 * np.sin(np.radians(70)) / L.G) < 1e-9))
    angs = np.arange(1.0, 90.0, 0.5)
    best = angs[int(np.argmax([L.range_from(30.0, a) for a in angs]))]
    checks.append(("a scan of angles finds the maximum range at 45 degrees on level ground", abs(best - 45.0) < 0.26))
    checks.append(("launch height lowers the best angle below 45 degrees and extends the range",
                   L.best_angle_with_height(30, 2.0) < 45 and abs(L.best_angle_with_height(30, 0.0) - 45.0) < 1e-9
                   and L.range_from(30, L.best_angle_with_height(30, 2.0), 2.0) > L.range_from(30, 45, 2.0) - 1e-12))
    pair = L.angles_for_range(25.0, 50.0)
    checks.append(("two angles per range: they add up to 90 degrees and both land at 50 m",
                   len(pair) == 2 and abs(sum(pair) - 90) < 1e-9 and all(abs(L.range_from(25.0, a) - 50.0) < 1e-6 for a in pair)))
    vmax_r = 25.0 ** 2 / L.G
    checks.append(("edge: the maximum range v^2/g gives one angle (45) and a longer target gives none",
                   L.angles_for_range(25.0, vmax_r) == [45.0] and L.angles_for_range(25.0, vmax_r + 0.01) == []))
    vm, am = L.min_speed_to_hit(50.0, 10.0)
    checks.append((f"worked example: lowest speed to hit (50 m, 10 m) is 24.46 m/s at 50.65 degrees (got {vm:.2f}, {am:.2f})",
                   abs(vm - 24.46) < 0.01 and abs(am - 50.65) < 0.01))
    checks.append(("at that speed the path passes through the target, and just below it no angle works",
                   abs(float(L.height_at(50.0, vm, am)) - 10.0) < 1e-6 and L.angles_to_hit(50.0, 10.0, vm - 0.05) == []))
    a26 = L.angles_to_hit(50.0, 10.0, 26.0)
    checks.append(("at 26 m/s there are two angles (38.2 and 63.1 degrees) and both hit the target",
                   len(a26) == 2 and all(abs(float(L.height_at(50.0, 26.0, a)) - 10.0) < 1e-6 for a in a26)
                   and abs(a26[0] - 38.24) < 0.01 and abs(a26[1] - 63.07) < 0.01))
    checks.append(("edge: level target, h = 0, needs v^2 = g d at 45 degrees",
                   abs(L.min_speed_to_hit(40.0, 0.0)[0] - np.sqrt(L.G * 40.0)) < 1e-9 and abs(L.min_speed_to_hit(40.0, 0.0)[1] - 45) < 1e-9))
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
