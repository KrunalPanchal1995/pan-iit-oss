"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("hand calculation: 6 ohm + 12 ohm in series is 18 ohm", abs(L.series([6, 12]) - 18.0) < 1e-12))
    checks.append(("hand calculation: 6 ohm || 12 ohm is 4 ohm", abs(L.parallel([6, 12]) - 4.0) < 1e-12))
    checks.append(("two equal resistors in parallel give half", abs(L.parallel([50, 50]) - 25.0) < 1e-12))
    checks.append(("parallel is smaller than the smallest branch", L.parallel([3, 8, 20]) < 3))
    checks.append(("worked example: 2 x 3 grid of 180 ohm is 120 ohm and 0.100 A on 12 V",
                   abs(L.grid_resistance(180, 2, 3) - 120.0) < 1e-9 and abs(12 / L.grid_resistance(180, 2, 3) - 0.1) < 1e-9))
    checks.append(("worked example: each of the six parts dissipates 0.200 W",
                   abs(L.grid_per_resistor_power(12, 180, 2, 3) - 0.2) < 1e-9))
    # total power equals V*I
    total = 6 * L.grid_per_resistor_power(12, 180, 2, 3)
    checks.append(("sum of part powers equals V*I = 1.2 W", abs(total - 1.2) < 1e-9))
    d = L.design(12.0, 0.100, 0.05, 0.25)
    checks.append(("smallest safe design needs 6 parts", d[0]["n"] == 6))
    checks.append(("no design with 5 or fewer parts exists", all(x["n"] >= 6 for x in d)))
    checks.append(("every design respects the rating and the current tolerance",
                   all(x["p_each"] <= 0.25 and abs(x["current"] - 0.1) <= 0.005 + 1e-12 for x in d)))
    d50 = L.design(12.0, 0.050, 0.05, 0.25)[0]
    checks.append(("section F design: three 82 ohm in series give 48.8 mA at 0.195 W each",
                   d50["n"] == 3 and d50["r"] == 82 and abs(d50["current"] - 0.04878) < 1e-4 and abs(d50["p_each"] - 0.1951) < 1e-3))
    checks.append(("a single 120 ohm resistor fails the 0.25 W rating", 12 ** 2 / 120 > 0.25))
    checks.append(("impossible limit gives no design", L.design(12.0, 0.100, 0.05, 0.001, max_n=4) == []))
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
