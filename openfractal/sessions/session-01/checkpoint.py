"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("(1+2i) + (3-1i) = 4+1i", L.add(1 + 2j, 3 - 1j) == 4 + 1j))
    checks.append(("multiplying by i turns 1 into i, and i into -1", L.times_i(1 + 0j) == 1j and L.times_i(1j) == -1))
    z = 2.0 + 1.0j
    checks.append(("four quarter turns bring a point back", abs(L.times_i(L.times_i(L.times_i(L.times_i(z)))) - z) < 1e-12))
    checks.append(("a quarter turn keeps the distance from 0", abs(abs(L.times_i(z)) - abs(z)) < 1e-12))
    o = L.orbit(0.5 + 0.5j, 5)
    checks.append(("worked example: c = 0.5+0.5i gives z2 = 0.5+1.0i", abs(o[2] - (0.5 + 1.0j)) < 1e-12))
    checks.append(("worked example: c = 0.5+0.5i gives z4 = -1.6875-0.25i and |z5| = 3.55 > 2 (escape step 5)",
                   abs(o[4] - (-1.6875 - 0.25j)) < 1e-12 and abs(abs(o[5]) - 3.549) < 1e-3 and L.escape_step(0.5 + 0.5j) == 5))
    checks.append(("c = 0: the orbit stays at 0", all(q == 0 for q in L.orbit(0, 10)) and not L.escapes(0)))
    checks.append(("c = 1: orbit 0, 1, 2, 5 and it escapes", L.orbit(1, 3) == [0, 1, 2, 5] and L.escapes(1)))
    checks.append(("c = -1: orbit cycles 0, -1, 0, -1 and stays", L.orbit(-1, 3) == [0, -1, 0, -1] and not L.escapes(-1)))
    checks.append(("a huge c does not overflow", len(L.orbit(1e6, 50)) < 10))
    checks.append(("c = 0.2 settles (stays), c = 0.3 escapes only at step 12",
                   not L.escapes(0.2) and L.escape_step(0.3) == 12))
    checks.append(("the settled value for c = 0.2 is 0.2764 (z = z*z + 0.2 has a fixed point)",
                   abs(abs(L.orbit(0.2, 60)[-1]) - (1 - np.sqrt(1 - 0.8)) / 2) < 1e-9))
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
