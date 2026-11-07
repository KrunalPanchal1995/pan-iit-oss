"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    v = L.stick(2, 4, 1, 0)
    checks.append((f"worked example: sticking speed 8 / 3 = 2.667 m/s (got {v:.3f})", abs(v - 8 / 3) < 1e-9))
    a, b = L.bounce(2, 4, 1, 0)
    checks.append((f"worked example: bouncing speeds 1.333 and 5.333 m/s (got {a:.3f} and {b:.3f})", abs(a - 4 / 3) < 1e-9 and abs(b - 16 / 3) < 1e-9))
    checks.append(("worked example: sticking loses 5.33 J of kinetic energy (one third)", abs(L.ke_lost_sticking(2, 4, 1, 0) - 16 / 3) < 1e-9))
    cases = [(2, 4, 1, 0), (3, 2, 1, 0), (1, 5, 4, -2), (5, 0, 2, -3)]
    checks.append(("momentum is kept when sticking", all(abs(L.total_momentum(m1, v1, m2, v2) - L.total_momentum(m1, L.stick(m1, v1, m2, v2), m2, L.stick(m1, v1, m2, v2))) < 1e-9 for m1, v1, m2, v2 in cases)))
    checks.append(("momentum is kept when bouncing", all(abs(L.total_momentum(m1, v1, m2, v2) - (m1 * L.bounce(m1, v1, m2, v2)[0] + m2 * L.bounce(m1, v1, m2, v2)[1])) < 1e-9 for m1, v1, m2, v2 in cases)))
    checks.append(("kinetic energy is kept when bouncing", all(abs(L.total_ke(m1, v1, m2, v2) - L.total_ke(m1, L.bounce(m1, v1, m2, v2)[0], m2, L.bounce(m1, v1, m2, v2)[1])) < 1e-9 for m1, v1, m2, v2 in cases)))
    checks.append(("kinetic energy is never gained when sticking", all(L.ke_lost_sticking(*c) >= -1e-12 for c in cases)))
    a, b = L.bounce(3, 2, 3, 0)
    checks.append(("equal masses and a body at rest: the moving body stops and the other takes its speed", abs(a) < 1e-12 and abs(b - 2) < 1e-12))
    a, b = L.bounce(1, 4, 5, 0)
    checks.append(("a light body hitting a heavy one at rest bounces back", a < 0 < b))
    checks.append(("design: m2 = 8 kg loses at least 75 percent, m2 = 4 kg does not (m1 = 2 kg, v1 = 4 m/s, v2 = 0)",
                   L.ke_lost_sticking(2, 4, 8, 0) / L.total_ke(2, 4, 8, 0) >= 0.75 > L.ke_lost_sticking(2, 4, 4, 0) / L.total_ke(2, 4, 4, 0)))
    checks.append(("edge case: both bodies at rest stay at rest", L.stick(2, 0, 3, 0) == 0 and L.bounce(2, 0, 3, 0) == (0, 0)))
    for bad, label in ((lambda: L.stick(0, 1, 1, 0), "mass 0 when sticking"), (lambda: L.bounce(1, 1, -2, 0), "a negative mass when bouncing")):
        try:
            bad()
            raised = False
        except ValueError:
            raised = True
        checks.append((f"edge case: {label} gives an error", raised))
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
