"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: thermal pad (k = 5, 1 mm, 80 C to 50 C) carries 15.0 W",
                   abs(L.heat_rate(5.0, 1.0, 80.0, 50.0) - 15.0) < 1e-9))
    checks.append(("flux is 150000 W/m^2 for the worked example",
                   abs(L.heat_flux(5.0, 1.0, 80.0, 50.0) - 150000.0) < 1e-6))
    checks.append(("hand calculation: copper 5 mm, 80 C to 40 C carries 320 W",
                   abs(L.heat_rate(400.0, 5.0, 80.0, 40.0) - 320.0) < 1e-9))
    checks.append(("temperature at mid depth is the average of the faces (65 C)",
                   abs(float(L.temperature_at(0.5, 1.0, 80.0, 50.0)) - 65.0) < 1e-9))
    checks.append(("the profile starts at T_hot and ends at T_cold",
                   abs(float(L.temperature_at(0.0, 5.0, 80.0, 40.0)) - 80.0) < 1e-9
                   and abs(float(L.temperature_at(5.0, 5.0, 80.0, 40.0)) - 40.0) < 1e-9))
    checks.append(("doubling the thickness halves the heat flow",
                   abs(L.heat_rate(50.0, 10.0, 80.0, 40.0) * 2 - L.heat_rate(50.0, 5.0, 80.0, 40.0)) < 1e-9))
    checks.append(("no temperature difference means no heat flow", L.heat_rate(400.0, 5.0, 60.0, 60.0) == 0.0))
    t = L.compare_materials()
    checks.append(("copper carries 80 times more heat than the thermal pad", abs(t["copper"] / t["thermal pad"] - 80.0) < 1e-9))
    x = np.linspace(0, 5, 11)
    checks.append(("the profile is a straight line (constant slope)",
                   np.allclose(np.diff(L.temperature_at(x, 5.0, 80.0, 40.0)), -8.0 * 0.5)))
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
