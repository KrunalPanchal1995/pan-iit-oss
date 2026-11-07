"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("at 101.325 kPa the boiling point is 100 C", abs(L.boiling_point_c(101.325) - 100.0) < 1e-9))
    t100g = L.boiling_point_c(L.gauge_to_abs(100.0))
    checks.append((f"worked example: 100 kPa gauge (201.325 kPa absolute) boils at {t100g:.1f} C, about 120.6",
                   abs(t100g - 120.6) < 0.05 and abs(L.rate_factor(t100g) - 4.17) < 0.02))
    checks.append(("near 200 kPa the result is within 0.5 C of the steam table (120.2 C)", abs(L.boiling_point_c(200.0) - 120.2) < 0.5))
    errs = [abs(L.boiling_point_c(p) - t) for p, t in L.TABLE]
    checks.append(("all table points are within 0.6 C", max(errs) < 0.6))
    checks.append(("vapour_pressure_kpa undoes boiling_point_c", abs(L.vapour_pressure_kpa(L.boiling_point_c(250.0)) - 250.0) < 1e-6))
    # hand calculation: 1/T2 = 1/373.15 - ln(2) R / L when the pressure doubles
    inv = 1 / 373.15 - np.log(2.0) * 8.314 / 40700.0
    checks.append(("hand calculation: doubling the pressure gives 1/T2 = 1/373.15 - ln2*R/L", abs(L.boiling_point_k(2 * 101.325) - 1 / inv) < 1e-6))
    checks.append(("boiling point rises with pressure", L.boiling_point_c(150.0) < L.boiling_point_c(250.0)))
    checks.append(("rate factor doubles per 10 C", abs(L.rate_factor(110.0) - 2.0) < 1e-12))
    m = L.valve_mass_kg(100.0, 0.004)
    checks.append((f"design: 100 kPa gauge on a 4 mm opening needs {m * 1000:.1f} g (about 128)", abs(m * 1000 - 128.1) < 0.2))
    checks.append(("valve mass and pressure formulas are inverses", abs(L.valve_gauge_kpa(m, 0.004) - 100.0) < 1e-9))
    try:
        L.boiling_point_k(0.0)
        edge = False
    except ValueError:
        edge = True
    checks.append(("zero absolute pressure raises ValueError", edge))
    checks.append(("a larger opening needs a heavier valve for the same pressure", L.valve_mass_kg(100.0, 0.005) > L.valve_mass_kg(100.0, 0.004)))
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
