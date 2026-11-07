"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    v1 = L.velocity(0.010, 0.100)
    v2 = L.velocity(0.010, 0.050)
    checks.append(("worked example: 10 L/s gives 1.273 m/s in 100 mm and 5.093 m/s in 50 mm",
                   abs(v1 - 1.2732) < 1e-3 and abs(v2 - 5.0930) < 1e-3))
    p2 = L.pressure_after(100e3, v1, v2)
    checks.append((f"worked example: pressure after the narrowing is 87.87 kPa (got {p2 / 1e3:.2f})",
                   abs(p2 / 1e3 - 87.87) < 0.01))
    checks.append(("hand calculation: halving the diameter quadruples the speed", abs(v2 / v1 - 4.0) < 1e-9))
    checks.append(("continuity: A1 v1 = A2 v2 = Q",
                   abs(L.area(0.100) * v1 - 0.010) < 1e-12 and abs(L.area(0.050) * v2 - 0.010) < 1e-12))
    x, d, v, p = L.profile(0.010, 0.100, 0.050, 100e3)
    tot = L.total_pressure(p, v)
    checks.append(("Bernoulli: p + 1/2 rho v^2 is constant along the pipe", np.allclose(tot, tot[0], atol=1e-6)))
    checks.append(("pressure falls where the pipe is narrow", p[-1] < p[0] and np.all(np.diff(p) <= 1e-9)))
    x, d, v, p = L.profile(0.010, 0.080, 0.080, 50e3)
    checks.append(("limit: equal diameters change neither speed nor pressure",
                   np.allclose(v, v[0]) and np.allclose(p, 50e3)))
    x, d, v, p = L.profile(0.010, 0.050, 0.100, 100e3)
    checks.append(("a widening pipe recovers pressure (p rises above the start)", p[-1] > p[0]))
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
