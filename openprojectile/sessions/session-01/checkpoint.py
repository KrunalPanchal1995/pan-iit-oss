"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    vx, vy = L.components(20.0, 30.0)
    checks.append(("worked example: 20 m/s at 30 degrees gives vx = 17.32, vy = 10.00 m/s",
                   abs(vx - 17.3205) < 1e-3 and abs(vy - 10.0) < 1e-9))
    r, h, t = L.flight(20.0, 30.0)
    checks.append((f"worked example: range 35.31 m, peak 5.10 m, time 2.04 s (got {r:.2f}, {h:.2f}, {t:.2f})",
                   abs(r - 35.31) < 0.01 and abs(h - 5.097) < 0.01 and abs(t - 2.039) < 0.01))
    checks.append(("hand calculation: straight up at 9.81 m/s takes 2 s and peaks at 4.905 m",
                   abs(L.flight(9.81, 90.0)[2] - 2.0) < 1e-9 and abs(L.flight(9.81, 90.0)[1] - 4.905) < 1e-9))
    x, y = L.position(t, 20.0, 30.0)
    checks.append(("the ball is back on the ground at the time of flight, at the range",
                   abs(float(y)) < 1e-9 and abs(float(x) - r) < 1e-9))
    checks.append(("45 degrees beats 30 and 60 at the same speed",
                   L.flight(20, 45)[0] > L.flight(20, 30)[0] and L.flight(20, 45)[0] > L.flight(20, 60)[0]))
    checks.append(("30 and 60 degrees land at the same spot",
                   abs(L.flight(20, 30)[0] - L.flight(20, 60)[0]) < 1e-9))
    t5 = np.linspace(0, 2, 9)
    x1, y1 = L.position(t5, 10.0, 45.0)
    x2, y2 = L.position(t5, 50.0, 45.0)
    thrown = L.position(t5, 7.0, 0.0)[1]
    checks.append(("independence: a sideways throw falls exactly like a dropped ball",
                   np.allclose(thrown, L.fall_height(t5, 0.0)) and np.allclose(x2, 5 * x1)))
    checks.append(("edge: angle 0 or a zero speed gives no range, no peak, no time",
                   L.flight(20, 0) == (0.0, 0.0, 0.0) and L.flight(0, 45) == (0.0, 0.0, 0.0)))
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
