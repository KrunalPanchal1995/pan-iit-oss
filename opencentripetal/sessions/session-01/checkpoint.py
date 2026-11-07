"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    a = L.centripetal_acceleration(10.0, 50.0)
    f = L.centripetal_force(1000.0, 10.0, 50.0)
    checks.append((f"worked example: 1000 kg at 10 m/s on r = 50 m needs a = 2 m/s^2 and F = 2000 N (got {a:.2f}, {f:.0f})",
                   abs(a - 2.0) < 1e-12 and abs(f - 2000.0) < 1e-9))
    checks.append(("hand calculation: doubling the speed quadruples the force", abs(L.centripetal_force(1000, 20, 50) / f - 4) < 1e-12))
    checks.append(("hand calculation: halving the radius doubles the force", abs(L.centripetal_force(1000, 10, 25) / f - 2) < 1e-12))
    checks.append(("zero speed needs no force", L.centripetal_force(1000, 0.0, 50) == 0.0))
    try:
        L.centripetal_acceleration(10.0, 0.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("edge case: a zero radius is rejected", ok))
    na = L.numeric_acceleration(10.0, 50.0)
    checks.append(("numerical second difference gives magnitude v^2/r = 2 m/s^2", abs(np.hypot(*na) - 2.0) < 1e-2))
    checks.append(("numerical acceleration points to the centre (negative x at the point (r, 0))", na[0] < 0 and abs(na[1]) < 1e-2))
    checks.append(("released ball moves in a straight line: x stays r, y grows as v t",
                   np.allclose(L.released_position(50, 10, 3.0), [50.0, 30.0])))
    checks.append(("released ball gets farther from the centre (it is not pulled outward, it goes straight)",
                   L.distance_from_centre(50, 10, 3.0) > 50.0))
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
