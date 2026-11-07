"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    vd, i, k = L.solve_newton(5.0, 150.0)
    checks.append(("worked example: 5 V and 150 ohm give 20.0 mA and an LED drop of 2.000 V",
                   abs(i - 0.020) < 1e-6 and abs(vd - 2.0) < 1e-4))
    checks.append(("Newton converges in a few dozen steps or fewer", k < 40))
    ok = all(abs(L.solve_newton(vs, r)[1] - L.solve_bisection(vs, r)[1]) < 1e-9
             for vs, r in ((5, 150), (3, 100), (12, 470), (2.2, 10), (24, 1000), (5, 60)))
    checks.append(("Newton agrees with bisection on six circuits", ok))
    vd2, i2, _ = L.solve_newton(3.0, 100.0)
    checks.append(("Kirchhoff voltage law: Vs = I R + Vd (residual below 1e-9 V)", abs(3.0 - (i2 * 100.0 + vd2)) < 1e-9))
    v, k = L.newton_linear(5.0, 150.0, 150.0)
    checks.append(("ohmic limit: a 150 ohm part makes a voltage divider, 2.5 V, in one step", abs(v - 2.5) < 1e-12 and k <= 2))
    checks.append(("hand calculation: ohmic shortcut 5/150 = 33.3 mA overestimates the real 20 mA",
                   abs(5 / 150 - 0.03333) < 1e-4 and 5 / 150 > 1.5 * i))
    fd, formula = L.sensitivity(5.0, 150.0)
    checks.append(("sensitivity dI/dVs matches 1/(R + N_VT/I), about 6.56 mA per volt",
                   abs(fd - formula) < 1e-6 and abs(1000 * formula - 6.557) < 0.01))
    lo, hi = L.current_range(5.0, 0.10, 150.0)
    checks.append(("supply 4.5 to 5.5 V gives 16.7 to 23.3 mA",
                   abs(1000 * lo - 16.73) < 0.02 and abs(1000 * hi - 23.28) < 0.02))
    checks.append(("current rises with supply and falls with resistance",
                   L.solve_newton(5.5, 150)[1] > L.solve_newton(4.5, 150)[1] and L.solve_newton(5, 220)[1] < L.solve_newton(5, 150)[1]))
    checks.append(("below the turn-on voltage almost no current flows", L.solve_newton(1.0, 150.0)[1] < 1e-6))
    checks.append(("mini-project: 180 and 220 ohm are the safe E12 choices",
                   L.pick_resistor(5.0, 0.10, 0.010, 0.025, 0.12) == [180.0, 220.0]))
    try:
        L.solve_newton(5.0, 0.0)
        bad = False
    except ValueError:
        bad = True
    checks.append(("zero resistor is rejected", bad))
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
