"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("at t = 0 all of A is still there", abs(float(L.conc_A(0.0, 1.0, 0.1)) - 1.0) < 1e-12))
    checks.append(("A decreases with time", bool(np.all(np.diff(L.conc_A(np.linspace(0, 30, 50), 1.0, 0.1)) < 0))))
    t = np.linspace(0, 50, 7)
    checks.append(("A + B is always A0 (mass is conserved)", np.allclose(L.conc_A(t, 2.0, 0.07) + L.conc_B(t, 2.0, 0.07), 2.0)))
    a10 = float(L.conc_A(10.0, 1.0, 0.10))
    checks.append((f"worked example: [A] after 10 s with k = 0.10 1/s is exp(-1) = 0.368 (got {a10:.3f})", abs(a10 - np.exp(-1)) < 1e-9))
    checks.append(("half-life for k = 0.10 1/s is ln 2 / 0.10 = 6.93 s", abs(L.half_life(0.10) - 6.9315) < 1e-3))
    checks.append(("at the half-life [A] is A0/2", abs(float(L.conc_A(L.half_life(0.3), 4.0, 0.3)) - 2.0) < 1e-9))
    checks.append(("hand calculation: 90 percent takes ln(10)/k = 23.0 s", abs(L.time_to_fraction(0.10, 0.9) - 23.026) < 1e-2))
    checks.append(("a 5 times faster catalyst finishes 5 times sooner", abs(L.time_to_fraction(L.with_catalyst(0.1, 5), 0.9) * 5 - L.time_to_fraction(0.1, 0.9)) < 1e-9))
    checks.append(("limit: k = 0 means nothing reacts", abs(float(L.conc_A(100.0, 1.0, 0.0)) - 1.0) < 1e-12))
    counts = L.count_molecules(2000, 0.05, 60)
    checks.append(("counting molecules agrees with (1 - p)^n within 3 percent", abs(counts[-1] / 2000 - 0.95 ** 60) < 0.03))
    checks.append(("the molecule count never increases", bool(np.all(np.diff(counts) <= 0))))
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
