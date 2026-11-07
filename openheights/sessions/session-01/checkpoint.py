"""Checkpoint for Session 1. Prints PASS or FAIL."""
import math


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: stick 1.5 m with shadow 1.0 m, tower shadow 18 m gives 27 m",
                   abs(L.shadow_height(1.5, 1.0, 18.0) - 27.0) < 1e-9))
    h = L.height_from_angle(40, 35, 1.6)
    checks.append((f"worked example: d = 40 m, 35 degrees, eye 1.6 m gives 29.61 m (got {h:.2f})", abs(h - 29.608) < 0.01))
    checks.append(("hand calculation: 45 degrees at 30 m with zero eye height is 30 m", abs(L.height_from_angle(30, 45, 0.0) - 30.0) < 1e-9))
    checks.append(("hand calculation: 30 degrees at 20 m, no eye, is 20/sqrt(3) = 11.547 m",
                   abs(L.height_from_angle(20, 30, 0.0) - 20 / math.sqrt(3)) < 1e-9))
    a = L.angle_for_height(40, 29.608, 1.6)
    checks.append(("angle_for_height undoes height_from_angle", abs(a - 35.0) < 0.01))
    checks.append(("doubling the distance doubles the height above the eye",
                   abs((L.height_from_angle(80, 20, 0) - 2 * L.height_from_angle(40, 20, 0))) < 1e-9))
    for bad in (0, 90, -5, 120):
        try:
            L.height_from_angle(10, bad)
            ok = False
        except ValueError:
            ok = True
        checks.append((f"edge: angle {bad} degrees is rejected", ok))
    try:
        L.shadow_height(1.5, 0.0, 10.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("edge: zero stick shadow is rejected", ok))
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
