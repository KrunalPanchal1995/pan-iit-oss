"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: bs 1.525 and fs 2.310 give a fall of 0.785 m",
                   abs(L.height_difference(1.525, 2.310) + 0.785) < 1e-9))
    checks.append(("worked example: RL of B = 100.000 - 0.785 = 99.215 m",
                   abs(L.next_rl(100.0, 1.525, 2.310) - 99.215) < 1e-9))
    pairs = L.level_run()
    rls = L.run_rls(pairs)
    checks.append(("run: first set-up reads bs 1.5 and fs 2.7", np.allclose(pairs[0], [1.5, 2.7], atol=1e-9)))
    checks.append(("run: each set-up falls 1.2 m (4 percent of 30 m)",
                   np.allclose([b - f for b, f in pairs], -1.2, atol=1e-9)))
    checks.append(("run: B is at 96.4 m, a fall of 3.6 m over 90 m", abs(rls[-1] - 96.4) < 1e-9 and abs(rls[0] - rls[-1] - 3.6) < 1e-9))
    checks.append(("run: sum of bs is 4.0 m and sum of fs is 7.6 m",
                   abs(sum(b for b, _ in pairs) - 4.0) < 1e-9 and abs(sum(f for _, f in pairs) - 7.6) < 1e-9))
    checks.append(("3.6 m over 90 m is a 4 percent grade", abs(3.6 / 90.0 * 100.0 - 4.0) < 1e-9))
    d1 = L.difference_for_hi(101.5, 100.0, 98.8)
    d2 = L.difference_for_hi(101.9, 100.0, 98.8)
    checks.append(("raising the instrument by 0.40 m leaves bs - fs unchanged (-1.2 m)",
                   abs(d1 - d2) < 1e-9 and abs(d1 + 1.2) < 1e-9))
    checks.append(("hand calculation: bs 0.872 and fs 2.134 from RL 54.320 give 53.058 m",
                   abs(L.next_rl(54.320, 0.872, 2.134) - 53.058) < 1e-9))
    checks.append(("calibration: 20.0 m in 27 paces is 0.741 m per pace", abs(L.pace_length(20.0, 27) - 0.7407) < 5e-4))
    checks.append(("pacing: 40 paces of 0.75 m is 30 m", abs(L.pace_distance(40, 0.75) - 30.0) < 1e-9))
    checks.append(("pacing: a true pace of 0.74 m instead of 0.75 m shifts 40 paces by 0.4 m",
                   abs(L.pace_distance(40, 0.75) - L.pace_distance(40, 0.74) - 0.4) < 1e-9))
    checks.append(("design: ground falling 5 percent, bs 1.0 m, staff 4.0 m: the foresight reaches the top at 60 m",
                   abs(1.0 + 0.05 * 60.0 - 4.0) < 1e-9))
    checks.append(("hand calculation: 0.872 - 2.134 = -1.262 m", abs(L.height_difference(0.872, 2.134) + 1.262) < 1e-9))
    checks.append(("app challenge: 4 percent over 40 m puts B at 98.4 m", abs(float(L.ground_rl(40.0)) - 98.4) < 1e-9))
    checks.append(("limit: zero distance gives a zero height difference",
                   abs(L.difference_for_hi(101.5, 100.0, 100.0)) < 1e-12))
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
