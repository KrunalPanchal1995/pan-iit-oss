"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: alpha = 2.5, x = 0.20 gives y = 0.5 / 1.3 = 0.3846",
                   abs(float(L.vapour_fraction(0.20, 2.5)) - 0.5 / 1.3) < 1e-12))
    d, b = L.split(100.0, 0.10, 0.80, 0.02)
    checks.append(("worked example: D = 100 x 0.08 / 0.78 = 10.26 mol and B = 89.74 mol",
                   abs(d - 800.0 / 78.0) < 1e-9 and abs(b - (100.0 - 800.0 / 78.0)) < 1e-9))
    checks.append(("material balance: ethanol in = ethanol out", abs(d * 0.80 + b * 0.02 - 100.0 * 0.10) < 1e-9))
    checks.append(("worked example: ethanol recovery 0.821", abs(L.recovery(100.0, 0.10, 0.80, 0.02) - 0.8205) < 1e-3))
    checks.append(("worked example: Fenske N_min = ln(196) / ln(2.5) = 5.76 stages",
                   abs(L.min_stages(0.80, 0.02, 2.5) - np.log(4.0 / (0.02 / 0.98)) / np.log(2.5)) < 1e-12
                   and abs(L.min_stages(0.80, 0.02, 2.5) - 5.76) < 0.01))
    x = np.linspace(0.0, 1.0, 101)
    checks.append(("alpha = 1 gives no separation (y = x)", np.allclose(L.vapour_fraction(x, 1.0), x)))
    checks.append(("pure liquids stay pure: y(0) = 0 and y(1) = 1",
                   float(L.vapour_fraction(0.0, 3.0)) == 0.0 and abs(float(L.vapour_fraction(1.0, 3.0)) - 1.0) < 1e-12))
    checks.append(("vapour is richer than liquid for alpha > 1 (0 < x < 1)",
                   bool(np.all(L.vapour_fraction(x[1:-1], 2.5) > x[1:-1]))))
    checks.append(("liquid_fraction undoes vapour_fraction", np.allclose(L.liquid_fraction(L.vapour_fraction(x, 4.0), 4.0), x)))
    xs = L.climb(0.02, 2.5, 6)
    ratios = L.odds(xs[1:]) / L.odds(xs[:-1])
    checks.append(("each stage multiplies the odds by exactly alpha", np.allclose(ratios, 2.5)))
    n = L.min_stages(0.80, 0.02, 2.5)
    checks.append(("climbing ceil(N_min) = 6 stages reaches 0.80, and 5 stages do not",
                   L.climb(0.02, 2.5, int(np.ceil(n)))[-1] >= 0.80 > L.climb(0.02, 2.5, int(np.floor(n)))[-1]))
    checks.append(("a larger alpha needs fewer stages", L.min_stages(0.80, 0.02, 6.0) < L.min_stages(0.80, 0.02, 2.5)))
    bad = 0
    for call in (lambda: L.min_stages(0.8, 0.02, 1.0), lambda: L.split(100, 0.10, 0.05, 0.02),
                 lambda: L.vapour_fraction(1.2, 2.0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
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
