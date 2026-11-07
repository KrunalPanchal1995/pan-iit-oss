"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    ra, rb = L.reactions(12.0, 2.0, 8.0)
    checks.append((f"worked example: P=12 kN at a=2 m, L=8 m gives RA=9 and RB=3 kN (got {ra:.2f}, {rb:.2f})",
                   abs(ra - 9) < 1e-9 and abs(rb - 3) < 1e-9))
    checks.append(("reactions add up to the load", abs(sum(L.reactions(7.5, 1.3, 5.0)) - 7.5) < 1e-9))
    checks.append(("worked example: M max = P a b / L = 18 kN m", abs(L.max_moment(12.0, 2.0, 8.0) - 18.0) < 1e-9))
    x = np.linspace(0, 8, 8001)
    m = L.moment(x, 12.0, 2.0, 8.0)
    checks.append(("moment is zero at both supports", abs(m[0]) < 1e-9 and abs(m[-1]) < 1e-9))
    checks.append(("largest moment of the diagram equals the formula", abs(m.max() - 18.0) < 1e-3))
    v = L.shear(x, 12.0, 2.0, 8.0)
    checks.append(("shear is +9 before the load and -3 after it", abs(v[0] - 9) < 1e-9 and abs(v[-1] + 3) < 1e-9))
    # hand check: slope of M equals V
    slope = np.gradient(m, x)
    checks.append(("slope of the moment diagram equals the shear force", abs(slope[1000] - 9) < 1e-6 and abs(slope[6000] + 3) < 1e-6))
    # edge: load on a support goes straight into it and bends nothing
    ra0, rb0 = L.reactions(10.0, 0.0, 4.0)
    checks.append(("edge case: load directly on support A: RA = P, no bending", abs(ra0 - 10) < 1e-9 and L.max_moment(10.0, 0.0, 4.0) == 0))
    best = max(range(0, 801), key=lambda i: L.max_moment(12.0, i / 100.0, 8.0))
    checks.append(("worst load position is the centre", best == 400))
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
