"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d2_min = L.min_big_diameter(1200.0, 200.0, 10.0, 0.020)
    checks.append(("worked example: the smallest big piston is 48.5 mm", abs(d2_min * 1000 - 48.5) < 0.05))
    r = L.design_jack(1200.0, 200.0, 10.0, 0.020, 0.050, 0.040)
    checks.append(("worked example: 50 mm piston, lever 10: F1 = 2000 N, MA = 6.25, F2 = 12 500 N",
                   abs(r["F1"] - 2000.0) < 1e-9 and abs(r["MA"] - 6.25) < 1e-9 and abs(r["F2"] - 12500.0) < 1e-6))
    checks.append(("worked example: pressure 6.37 MPa = 63.7 bar", abs(L.to_bar(r["pressure"]) - 63.66) < 0.01))
    checks.append(("worked example: 6.4 mm of lift per 40 mm stroke, 1.56 pumps per cm",
                   abs(r["lift_per_stroke"] - 0.0064) < 1e-9 and abs(r["pumps_per_cm"] - 1.5625) < 1e-9))
    checks.append(("worked example: the car weighs 11 772 N and the 50 mm jack lifts it", abs(r["weight"] - 11772.0) < 1e-9 and r["lifts"]))
    # work balance
    w_in = r["F1"] * 0.040
    w_out = r["F2"] * r["lift_per_stroke"]
    checks.append(("work balance: F1 d1 = F2 d2 = 80 J", abs(w_in - w_out) < 1e-9 and abs(w_in - 80.0) < 1e-9))
    # hand calculations
    checks.append(("hand calculation: 10 m of water gives 98 100 Pa", abs(L.hydrostatic_pressure(1000.0, 10.0) - 98100.0) < 1e-9))
    checks.append(("units: 250 kPa = 2.5 bar", abs(L.to_bar(250e3) - 2.5) < 1e-12 and abs(L.to_kpa(1e5) - 100.0) < 1e-12))
    # edge and limit cases
    checks.append(("edge: at exactly the minimum diameter the jack just lifts (round-off safe)",
                   L.design_jack(1200.0, 200.0, 10.0, 0.020, d2_min, 0.040)["lifts"]))
    checks.append(("edge: 1 mm below the minimum diameter does not lift",
                   not L.design_jack(1200.0, 200.0, 10.0, 0.020, d2_min - 0.001, 0.040)["lifts"]))
    checks.append(("limit: zero depth gives zero gauge pressure", L.hydrostatic_pressure(870.0, 0.0) == 0.0))
    checks.append(("oil column of 0.5 m adds only 4.27 kPa, under 0.1 percent of 6.37 MPa",
                   abs(L.hydrostatic_pressure(L.RHO_OIL, 0.5) - 4267.35) < 0.01 and 4267.35 / r["pressure"] < 0.001))
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
