"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    a = L.area_circle(10.0)
    checks.append(("worked example: d = 10 mm gives area 78.54 mm^2", abs(a - 78.5398) < 1e-3))
    r = L.pull(15.0, 10.0)
    checks.append(("worked example: 15 kN on d = 10 mm gives 191.0 MPa", abs(r["stress"] - 190.99) < 0.01))
    checks.append(("worked example: strain 0.00273 and extension 1.36 mm", abs(r["strain"] - 0.002728) < 1e-5 and abs(r["extension"] - 1.364) < 0.01))
    checks.append(("15 kN is elastic (below the 200 MPa yield) and leaves no permanent set", r["region"] == "elastic" and r["set"] == 0.0))
    r2 = L.pull(20.0, 10.0)
    checks.append(("20 kN is plastic with permanent set about 0.0070", r2["region"] == "plastic" and abs(r2["set"] - 0.00703) < 1e-4))
    checks.append(("hand calculation: 10 kN on 100 mm^2 is 100 MPa", abs(L.stress_mpa(10.0, 100.0) - 100.0) < 1e-12))
    checks.append(("hand calculation: 2 mm on 500 mm is strain 0.004", abs(L.strain(2.0, 500.0) - 0.004) < 1e-12))
    s = np.linspace(0, 400, 9)
    checks.append(("stress -> strain -> stress round trip", np.allclose(L.stress_from_strain(L.strain_from_stress(s)), s)))
    checks.append(("zero load gives zero stress, zero strain, zero set", L.pull(0.0)["stress"] == 0.0 and L.pull(0.0)["strain"] == 0.0 and L.pull(0.0)["set"] == 0.0))
    checks.append(("in the elastic range the slope equals E", abs(L.stress_from_strain(0.001) / 0.001 - L.E_TOY) < 1e-6))
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
