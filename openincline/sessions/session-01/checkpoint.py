"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("flat table: N = m g and slope pull = 0",
                   abs(L.normal_force(5, 0) - 5 * 9.81) < 1e-9 and abs(L.along_slope(5, 0)) < 1e-9))
    checks.append(("vertical wall: N = 0 and slope pull = m g",
                   abs(L.normal_force(5, 90)) < 1e-9 and abs(L.along_slope(5, 90) - 5 * 9.81) < 1e-9))
    N, F, lim = L.normal_force(5, 20), L.along_slope(5, 20), L.friction_limit(5, 20, 0.5)
    checks.append(("worked example: 5 kg, 20 degrees, mu 0.5 gives N 46.09, pull 16.78, limit 23.05 N",
                   abs(N - 46.09) < 0.01 and abs(F - 16.78) < 0.01 and abs(lim - 23.05) < 0.01))
    checks.append(("worked example: the block holds and friction equals the pull (16.78 N)",
                   (not L.slides(20, 0.5)) and abs(L.friction_force(5, 20, 0.5) - F) < 1e-9
                   and abs(L.net_force(5, 20, 0.5)) < 1e-9))
    checks.append(("worked example: critical angle for mu 0.5 is 26.57 degrees", abs(L.critical_angle(0.5) - 26.565) < 0.01))
    checks.append(("hand calculation: 35 degrees, 5 kg, mu 0.5 gives net force 8.04 N and a = 1.61 m/s^2",
                   abs(L.net_force(5, 35, 0.5) - 8.04) < 0.01 and abs(L.acceleration(5, 35, 0.5) - 1.608) < 0.01))
    checks.append(("mass cancels: a is the same for 1 kg and 50 kg, but the forces scale with m",
                   abs(L.acceleration(1, 35, 0.5) - L.acceleration(50, 35, 0.5)) < 1e-9
                   and abs(L.net_force(50, 35, 0.5) / L.net_force(1, 35, 0.5) - 50) < 1e-9))
    checks.append(("sliding exactly starts above the critical angle for several mu",
                   all(L.slides(L.critical_angle(mu) + 0.1, mu) and not L.slides(L.critical_angle(mu) - 0.1, mu)
                       for mu in (0.1, 0.3, 0.7, 1.0))))
    checks.append(("edge case: mu = 0 slides at any angle above 0 and a = g sin t",
                   L.slides(1, 0.0) and abs(L.acceleration(3, 30, 0.0) - 9.81 * 0.5) < 1e-9))
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
