"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    i1, i2, i3, va = L.two_loop(10, 4, 100, 200, 300)
    checks.append(("worked example: two-loop circuit gives I1 = 34.55 mA, I2 = -12.73 mA, V_A = 6.545 V",
                   abs(i1 - 0.034545) < 1e-6 and abs(i2 + 0.012727) < 1e-6 and abs(va - 6.54545) < 1e-4))
    h = L.two_loop_by_hand(10, 4, 100, 200, 300)
    checks.append(("hand (Cramer) solution agrees with numpy.linalg.solve", np.allclose(h, (i1, i2, i3, va), atol=1e-12)))
    checks.append(("KCL at node A: currents in minus current out is zero", abs(L.kcl_residual(i1, i2, i3)) < 1e-12))
    checks.append(("KVL round loop 1 (V1, R1, R3) sums to zero", abs(L.kvl_residual(10, 100, i1, va)) < 1e-12))
    checks.append(("KVL round loop 2 (V2, R2, R3) sums to zero", abs(L.kvl_residual(4, 200, i2, va)) < 1e-12))
    checks.append(("power balance: sources supply what the resistors dissipate",
                   abs(10 * i1 + 4 * i2 - (100 * i1 ** 2 + 200 * i2 ** 2 + 300 * i3 ** 2)) < 1e-12))
    checks.append(("hand calculation: 5 V, 1700 and 3300 ohm divider gives 3.300 V unloaded",
                   abs(L.divider_out(5, 1700, 3300) - 3.3) < 1e-9))
    checks.append(("loading effect: a 4700 ohm load pulls the same divider down to 2.664 V",
                   abs(L.loaded_out(5, 1700, 3300, 4700) - 2.664) < 5e-4))
    a, b = L.current_divider(0.03, 100, 200)
    checks.append(("current divider: 30 mA into 100 ohm and 200 ohm splits 20 mA and 10 mA",
                   abs(a - 0.02) < 1e-12 and abs(b - 0.01) < 1e-12 and abs(a + b - 0.03) < 1e-12))
    checks.append(("a very large load changes almost nothing", abs(L.loaded_out(5, 1700, 3300, 1e9) - 3.3) < 1e-4))
    r2 = L.design_r2(5.0, 3.3, 1000, 4700)
    checks.append(("design: R1 = 1000 and a 4700 ohm load need R2 = 3307 ohm for exactly 3.300 V",
                   abs(r2 - 3307.0) < 0.5 and abs(L.loaded_out(5, 1000, r2, 4700) - 3.3) < 1e-9))
    checks.append(("standard value 3300 ohm lands within 2 percent of 3.3 V and draws under 6 mA",
                   abs(L.loaded_out(5, 1000, 3300, 4700) - 3.3) < 0.066 and L.supply_current(5, 1000, 3300, 4700) < 0.006))
    try:
        L.design_r2(5.0, 3.3, 4700, 4700)
        ok = False
    except ValueError:
        ok = True
    checks.append(("impossible design (R1 = 4700 with a 4700 ohm load) is rejected", ok))
    checks.append(("edge: R1 = 0 passes the full input voltage", abs(L.divider_out(5, 0, 1000) - 5.0) < 1e-12))
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
