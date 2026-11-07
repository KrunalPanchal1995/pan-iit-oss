"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    H = 28.4
    a1 = math.degrees(math.atan(H / 40))
    a2 = math.degrees(math.atan(H / 30))
    checks.append(("exact readings recover the height: two angles at 40 m and 30 m give 30 m",
                   abs(L.height_two_angles(10, a1, a2, 1.6) - 30.0) < 1e-9))
    h = L.height_two_angles(10, 35.4, 43.5, 1.6)
    checks.append((f"worked example: b = 10 m, 35.4 and 43.5 degrees, eye 1.6 m gives 29.90 m (got {h:.2f})", abs(h - 29.900) < 0.01))
    checks.append(("distance to the base is found too: 30 m for the exact readings", abs(L.distance_to_base(10, a1, a2) - 30.0) < 1e-9))
    checks.append(("hand calculation: 45 degrees at 28.4 m, sigma 0.5 degrees, error = 2 H sigma = 0.496 m",
                   abs(L.height_error(28.4, 45, 0.5) - 2 * 28.4 * math.radians(0.5)) < 1e-9))
    e20, e45, e70 = (L.height_error(H / math.tan(math.radians(t)), t, 0.5) for t in (20, 45, 70))
    checks.append(("error is smallest at 45 degrees", e45 < e20 and e45 < e70))
    w = L.best_window(H, 0.5, 0.5)
    checks.append((f"worked example: design window is 24.9 to 32.4 m (got {w[0]:.1f} to {w[1]:.1f})",
                   abs(w[0] - 24.9) < 0.06 and abs(w[1] - 32.4) < 0.06))
    checks.append(("error equals the target at both edges of the window",
                   all(abs(L.height_error(d, math.degrees(math.atan(H / d)), 0.5) - 0.5) < 1e-6 for d in w)))
    checks.append(("edge: a 0.3 m target cannot be met with a 0.5 degree reading (window is None)", L.best_window(H, 0.5, 0.3) is None))
    edge = L.best_window(H, 0.5, 2 * H * math.radians(0.5))
    checks.append(("edge: a target equal to the 45 degree error gives a single point at d = H",
                   edge is not None and abs(edge[0] - H) < 1e-6 and abs(edge[1] - H) < 1e-6))
    for a, b in ((40, 30), (30, 30), (0, 30), (30, 90)):
        try:
            L.height_two_angles(10, a, b)
            ok = False
        except ValueError:
            ok = True
        checks.append((f"edge: readings ({a}, {b}) are rejected", ok))
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
