"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    I = L.I_rect(0.100, 0.200)
    checks.append((f"worked example: I = b h^3 / 12 = 6.667e-5 m^4 (got {I:.4g})", abs(I - 6.6667e-5) < 1e-8))
    d = L.centre_deflection(10e3, 4.0, 10e9, I)
    checks.append((f"worked example: centre deflection P L^3 / (48 E I) = 20.0 mm (got {d * 1e3:.2f})", abs(d - 0.020) < 1e-6))
    s = L.bending_stress(L.moment_max(10e3, 2.0, 4.0), 0.100, I)
    checks.append((f"worked example: max stress M y / I = 15.0 MPa (got {s / 1e6:.2f})", abs(s - 15e6) < 1e3))
    checks.append(("general formula agrees with P L^3/(48 E I) for a centred load",
                   abs(L.max_deflection(10e3, 2.0, 4.0, 10e9, I) - d) < 1e-9))
    x = np.array([0.0, 4.0])
    checks.append(("deflection is zero at both supports", bool(np.all(np.abs(L.deflection(x, 10e3, 1.3, 4.0, 10e9, I)) < 1e-12))))
    checks.append(("doubling depth multiplies I by 8", abs(L.I_rect(0.1, 0.4) / L.I_rect(0.1, 0.2) - 8) < 1e-12))
    checks.append(("doubling width multiplies I by 2", abs(L.I_rect(0.2, 0.2) / L.I_rect(0.1, 0.2) - 2) < 1e-12))
    checks.append(("+20% area as depth gives more I than +20% as width", L.I_rect(0.1, 0.24) > L.I_rect(0.12, 0.2)))
    checks.append(("deflection is inversely proportional to E",
                   abs(L.centre_deflection(10e3, 4.0, 20e9, I) * 2 - d) < 1e-12))
    # I-section: with tf = h/2 and tw = bf it degenerates to a solid rectangle
    checks.append(("I-section formula reduces to b h^3 / 12 when the web fills the section",
                   abs(L.I_isection(0.1, 0.1, 0.1, 0.2) - L.I_rect(0.1, 0.2)) < 1e-12))
    Ii = L.I_isection(0.100, 0.010, 0.006, 0.200)
    Ir = L.I_rect(L.area_isection(0.100, 0.010, 0.006, 0.200) / 0.200, 0.200)
    checks.append(("I-section beats a solid rectangle of equal area and depth", Ii > 1.9 * Ir))
    h = L.lightest_rect(10e3, 2.0, 4.0, 10e9, 0.100, 12e6)
    checks.append((f"design: lightest 100 mm wide rectangle is 244 mm deep (got {h * 1e3:.0f})", abs(h - 0.244) < 1e-9))
    d1, s1, ok1 = L.check_rect(10e3, 2.0, 4.0, 10e9, 0.100, 0.243, 12e6)
    checks.append(("design: 243 mm fails the deflection limit", not ok1 and d1 > 4.0 / 360))
    checks.append(("edge case: a very shallow beam fails", not L.check_rect(10e3, 2.0, 4.0, 10e9, 0.100, 0.05, 12e6)[2]))
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
