"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("hand calculation: stable dt for alpha = 20 mm^2/s, dx = 1 mm is 0.0125 s",
                   abs(L.stable_dt(20.0, 1.0) - 0.0125) < 1e-12))
    T0 = np.zeros((9, 9))
    T0[4, 4] = 100.0
    T1 = L.step(T0, 0.2)
    checks.append(("one step with r = 0.2: the hot cell falls 100 -> 20 and each neighbour rises to 20",
                   abs(T1[4, 4] - 20.0) < 1e-12 and abs(T1[4, 5] - 20.0) < 1e-12))
    checks.append(("insulated edges conserve the total heat", abs(L.step(T0, 0.25).sum() - 100.0) < 1e-9))
    x, num, ex = L.wall_test()
    checks.append(("steady 1D wall: solver gives the straight line 80 -> 40 (within 0.001 K)",
                   float(np.abs(num - ex).max()) < 1e-3))
    T, E, X, Y = L.gaussian_run(1.0)
    checks.append(("worked example: peak rise after 1 s is 10.99 K (solver) against 11.02 K (exact)",
                   abs(T.max() - 10.993) < 0.01 and abs(E.max() - 11.020) < 0.005))
    e1, e2 = L.max_error(2.0), L.max_error(1.0)
    checks.append(("grid convergence: halving dx cuts the error by about 4 (second order)",
                   3.5 < e1 / e2 < 4.5))
    checks.append(("grid convergence continues: error at dx = 0.25 mm is 0.0017 K (4 times below dx = 0.5)",
                   abs(L.max_error(0.25) - 0.00172) < 0.0001))
    checks.append(("past the limit (r = 0.26) a 0.001 K wiggle explodes; at r = 0.24 it does not",
                   L.wiggle_growth(0.26) > 1e3 and L.wiggle_growth(0.24) < 1e-3))
    pk = [L.gaussian_run(1.0, alpha=a)[0].max() for a in (18.0, 22.0)]
    checks.append(("sensitivity: more conductivity (alpha 22 against 18) lowers the peak", pk[1] < pk[0]))
    Tb, Xb, Yb, lost = L.board_run(12.0, 8.0, 0.5, 40.0)
    checks.append(("energy balance: power lost to the air equals the 20 W put in (within 1 percent)",
                   abs(lost - 20.0) < 0.2))
    checks.append(("two hot spots: the CPU spot (12 W) is hotter than the GPU spot (8 W)",
                   Tb[15, 14] > Tb[15, 36]))
    checks.append(("a thicker spreader lowers the peak rise",
                   L.peak_rise(12.0, 8.0, 1.0, 40.0) < L.peak_rise(12.0, 8.0, 0.5, 40.0)))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
