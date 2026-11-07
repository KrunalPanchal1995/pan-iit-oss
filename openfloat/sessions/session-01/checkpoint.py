"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("0.1 + 0.2 is not exactly 0.3 in floating point", (0.1 + 0.2) != 0.3))
    checks.append(("(0.1 + 0.2) - 0.3 is about 5.55e-17", abs(L.sum_error_01_02() - 5.551115123125783e-17) < 1e-30))
    checks.append(("the stored 0.1 starts 0.1000000000000000055", L.stored_value(0.1).startswith("0.1000000000000000055")))
    checks.append(("worked example: gap above 1 is 2^-52 = 2.22e-16", L.gap(1.0) == 2.0 ** -52))
    checks.append(("worked example: gap above 2^53 is 2, so 2^53 + 1 == 2^53", L.gap(2.0 ** 53) == 2.0 and 2.0 ** 53 + 1 == 2.0 ** 53))
    checks.append(("gap doubles when the number doubles", L.gap(2000.0) == 2 * L.gap(1000.0)))
    r = [L.relative_gap(x) for x in np.logspace(-3, 12, 50)]
    checks.append(("relative gap stays between 2^-53 and 2^-52", min(r) >= 2.0 ** -53 and max(r) <= 2.0 ** -52))
    checks.append(("hand calculation: toy format m=3 has gap 0.5 above 4", L.toy_gap(4.0, 3) == 0.5))
    v = L.toy_numbers(3, 1.0, 16.0)
    checks.append(("toy format m=3 has 8 numbers per power of two (32 in [1, 16))", len(v) == 32 and v[0] == 1.0))
    checks.append(("toy numbers in [8, 16) are 1 apart", np.allclose(np.diff(v[v >= 8]), 1.0)))
    checks.append(("edge: nearly_equal accepts 0.1 + 0.2 vs 0.3 and rejects 0.3 vs 0.31",
                   L.nearly_equal(0.1 + 0.2, 0.3) and not L.nearly_equal(0.3, 0.31)))
    checks.append(("edge: nearly_equal(0, 1e-20) needs an absolute tolerance",
                   (not L.nearly_equal(0.0, 1e-20)) and L.nearly_equal(0.0, 1e-20, abs_tol=1e-15)))
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
