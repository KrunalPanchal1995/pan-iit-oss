"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("pressure: 100 N on 0.001 m^2 is 100 000 Pa", abs(L.pressure(100.0, 0.001) - 1e5) < 1e-6))
    f2 = L.output_force(200.0, 0.02, 0.06)
    checks.append(("worked example: 200 N on a 2 cm piston gives 1800 N on a 6 cm piston",
                   abs(f2 - 1800.0) < 1e-6))
    checks.append(("worked example: the multiplier is 9 and a 5 cm push moves the big piston 5.6 mm",
                   abs(L.multiplier(0.02, 0.06) - 9.0) < 1e-12 and abs(L.output_distance(50.0, 0.02, 0.06) - 5.5556) < 1e-3))
    checks.append(("equal pistons give no multiplication", abs(L.output_force(150.0, 0.03, 0.03) - 150.0) < 1e-9))
    checks.append(("doubling the big diameter makes the force 4 times bigger",
                   abs(L.output_force(100.0, 0.02, 0.08) / L.output_force(100.0, 0.02, 0.04) - 4.0) < 1e-9))
    # hand calculation: p = 200 / (pi * 0.01^2) = 636 620 Pa
    p = L.pressure(200.0, L.area_circle(0.02))
    checks.append(("hand calculation: 200 N on 2 cm gives about 636.6 kPa", abs(p - 636619.8) < 1.0))
    # force times distance is the same on both sides (ideal, no losses)
    w_in = 200.0 * 0.05
    w_out = f2 * L.output_distance(0.05, 0.02, 0.06)
    checks.append(("work in equals work out (10 J) for the ideal jack", abs(w_in - w_out) < 1e-9 and abs(w_in - 10.0) < 1e-9))
    checks.append(("car weight is 1200 * 9.81 = 11 772 N", abs(L.CAR_WEIGHT - 11772.0) < 1e-6))
    checks.append(("limit: a zero push gives zero force", L.output_force(0.0, 0.02, 0.06) == 0.0))
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
