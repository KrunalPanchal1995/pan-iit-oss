"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: 12 V across 6 ohm gives 2 A and 24 W",
                   abs(L.current(12, 6) - 2.0) < 1e-12 and abs(L.power(12, 6) - 24.0) < 1e-12))
    checks.append(("hand calculation: 24 ohm on 12 V draws 0.5 A", abs(L.current(12, 24) - 0.5) < 1e-12))
    a, b, c = L.power_forms(7.5, 3.0)
    checks.append(("V*I, I^2*R and V^2/R agree", np.allclose([a, b], c)))
    checks.append(("doubling V doubles I and quadruples P",
                   abs(L.current(2, 5) / L.current(1, 5) - 2) < 1e-12 and abs(L.power(2, 5) / L.power(1, 5) - 4) < 1e-12))
    checks.append(("doubling R halves I", abs(L.current(12, 12) / L.current(12, 6) - 0.5) < 1e-12))
    try:
        L.current(12, 0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("zero resistance is rejected (short circuit, not a number)", ok))
    checks.append(("table has 12 preset rows", len(L.table()) == 12))
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
