"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    s = L.stress(20.0, 16.0)
    checks.append(("worked example: 20 kN on d = 16 mm gives 99.5 MPa", abs(s - 99.472) < 0.01))
    e = L.extension(20.0, 2000.0, 16.0, 200000.0)
    checks.append(("worked example: steel d = 16 mm stretches 0.995 mm", abs(e - 0.9947) < 1e-3))
    checks.append(("worked example: steel factor of safety 2.51", abs(L.factor_of_safety(250.0, s) - 2.5133) < 1e-3))
    d = L.design("steel (mild)")
    checks.append(("worked example: steel needs d = 14.27 mm for strength, 15.96 mm for stiffness, so 16 mm",
                   abs(d["d_strength"] - 14.27) < 0.01 and abs(d["d_stiffness"] - 15.96) < 0.01 and d["d"] == 16.0 and d["limit"] == "stiffness"))
    checks.append(("hand calculation: 10 kN, 1 m, 100 mm^2, E = 100 GPa gives 1 mm",
                   abs(L.extension(10.0, 1000.0, np.sqrt(400 / np.pi), 100000.0) - 1.0) < 1e-9))
    best, rows = L.best_design()
    checks.append(("every returned design passes both limits",
                   all(r["ext"] <= 1.0 + 1e-9 and r["fos"] >= 2.0 - 1e-9 for r in rows)))
    checks.append(("copper is governed by strength, the others by stiffness",
                   [r["limit"] for r in rows] == ["stiffness", "stiffness", "strength", "stiffness"]))
    checks.append(("lightest passing bar is the aluminium alloy, about 3.09 kg",
                   best["name"] == "aluminium alloy" and abs(best["mass"] - 3.09) < 0.01))
    checks.append(("doubling E halves the extension", abs(L.extension(5, 100, 10, 2e5) * 2 - L.extension(5, 100, 10, 1e5)) < 1e-12))
    checks.append(("zero load gives zero extension",
                   L.extension(0.0, 2000.0, 10.0, 2e5) == 0.0))
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
