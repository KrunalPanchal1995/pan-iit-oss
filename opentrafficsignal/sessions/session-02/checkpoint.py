"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    C, q1, q2 = 60.0, 0.20, 0.10
    checks.append(("worked example: x = 0.20 x 60 / (27 x 0.5) = 0.889",
                   abs(L.degree_of_saturation(C, 27, 0.20) - 0.88889) < 1e-4))
    checks.append(("worked example: d = 60 (0.55)^2 / (2 x 0.6) = 15.125 s", abs(L.uniform_delay(C, 27, 0.20) - 15.125) < 1e-9))
    checks.append(("worked example: quiet road d = 11.344 s", abs(L.uniform_delay(C, 27, 0.10) - 11.34375) < 1e-9))
    checks.append(("worked example: equal split gives 13.86 s average delay", abs(L.average_delay(C, 27, q1, q2) - 13.8646) < 1e-3))
    # hand calculation of the triangle area: q r^2 s / (2 (s - q)) per cycle divided by q C
    r, s, q = 33.0, 0.5, 0.15
    area = q * r * r * s / (2 * (s - q))
    checks.append(("triangle area / cars per cycle equals the formula",
                   abs(area / (q * 60.0) - L.uniform_delay(60.0, 27.0, q)) < 1e-9))
    checks.append(("no arrivals: formula reduces to C (1 - lam)^2 / 2", abs(L.uniform_delay(60, 27, 0.0) - 60 * 0.55 ** 2 / 2) < 1e-9))
    checks.append(("delay never decreases when arrivals grow",
                   all(L.uniform_delay(60, 27, a) <= L.uniform_delay(60, 27, b) for a, b in [(0.05, 0.1), (0.1, 0.2), (0.2, 0.225)])))
    checks.append(("exactly at x = 1 the delay is finite (edge case): 18 s",
                   abs(L.uniform_delay(60.0, 24.0, 0.2) - 18.0) < 1e-9))
    checks.append(("just above x = 1 the queue never clears (infinite delay)", L.uniform_delay(60.0, 23.9, 0.2) == float("inf")))
    checks.append(("zero green gives infinite delay", L.uniform_delay(60.0, 0.0, 0.1) == float("inf")))
    checks.append(("Webster cycle for Y = 0.6, L = 6 s is 35 s", abs(L.webster_cycle(0.6) - 35.0) < 1e-9))
    checks.append(("Webster cycle is infinite when Y >= 1", L.webster_cycle(1.0) == float("inf")))
    g90 = L.best_split(C, q1, q2, xmax=0.9)
    checks.append(("best split with x <= 0.9 gives the quiet road about 13.3 s (hand calculation q2 C / (0.9 s))",
                   abs((C - L.LOST - g90) - 0.1 * 60 / (0.9 * 0.5)) < 0.02))
    checks.append(("unconstrained best split puts the quiet road at x = 1 (g2 = 12 s)", abs(L.best_split(C, q1, q2) - 42.0) < 0.02))
    checks.append(("the designed split beats the equal split",
                   L.average_delay(C, g90, q1, q2) < L.average_delay(C, 27.0, q1, q2) - 2.0))
    checks.append(("proportional split gives 36 s to the busy road", abs(L.proportional_split(C, q1, q2) - 36.0) < 1e-9))
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
