"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    a = L.accel_from_rest(30, 0.40, 0.30)
    checks.append(("worked example: 30 degrees, mu_k 0.30 gives a = 2.356 m/s^2", abs(a - 2.356) < 0.001))
    checks.append(("worked example: speed 4.71 m/s and distance 4.71 m after 2 s",
                   abs(L.speed_after(a, 2) - 4.712) < 0.01 and abs(L.distance_after(a, 2) - 4.712) < 0.01))
    checks.append(("hand calculation: g (0.5 - 0.3 * 0.8660) = 2.356",
                   abs(9.81 * (0.5 - 0.3 * np.sqrt(3) / 2) - a) < 1e-9))
    checks.append(("slide angle for mu_s 0.40 is 21.80 degrees", abs(L.slide_angle(0.40) - 21.80) < 0.01))
    checks.append(("at 21 degrees the block holds (a = 0), at 22 it slides",
                   L.accel_from_rest(21, 0.4, 0.3) == 0.0 and L.accel_from_rest(22, 0.4, 0.3) > 0))
    checks.append(("mu_s from a measured slip angle of 21.8 degrees is 0.40", abs(L.mu_s_from_angle(21.8) - 0.40) < 0.001))
    th = L.angle_for_acceleration(1.5, 0.30)
    closed = np.degrees(np.arctan(0.30) + np.arcsin(1.5 / (9.81 * np.sqrt(1 + 0.30 ** 2))))
    checks.append(("design angle for a = 1.5 m/s^2 is 25.12 degrees and matches the closed form",
                   abs(th - 25.12) < 0.01 and abs(th - closed) < 1e-6))
    checks.append(("design angle is steep enough to start (tan t > mu_s)", np.tan(np.radians(th)) > 0.40))
    checks.append(("friction drops at slipping: just above the slide angle it is mu_k N, below the static limit",
                   L.friction_acting(10, 22, 0.4, 0.3) < L.friction_acting(10, 21.7, 0.4, 0.3)))
    try:
        L.angle_for_acceleration(20.0, 0.3)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge case: an acceleration larger than g sin(89 deg) raises ValueError", raised))
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
