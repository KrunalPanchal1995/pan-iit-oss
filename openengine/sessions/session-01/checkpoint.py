"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: Qh = 1000 J, Qc = 650 J gives W = 350 J and efficiency 0.35",
                   abs(L.work(1000, 650) - 350) < 1e-9 and abs(L.efficiency(1000, 650) - 0.35) < 1e-12))
    v, p = L.rectangle_loop(100.0, 300.0, 1.0, 3.0)
    checks.append(("worked example: rectangle 100 to 300 kPa and 1 to 3 L encloses 400 J", abs(L.loop_work(v, p) - 400.0) < 1e-9))
    checks.append(("hand calculation: area = (300 - 100) kPa x (3 - 1) L", abs(L.loop_work(v, p) - (300 - 100) * (3 - 1)) < 1e-9))
    checks.append(("a counter-clockwise loop gives negative work", abs(L.loop_work(v[::-1], p[::-1]) + 400.0) < 1e-9))
    checks.append(("taller loop (100 to 500 kPa) gives 800 J", abs(L.loop_work(*L.rectangle_loop(100, 500, 1, 3)) - 800.0) < 1e-9))
    checks.append(("a loop that starts at another corner has the same area",
                   abs(L.loop_work(np.roll(v, 1), np.roll(p, 1)) - 400.0) < 1e-9))
    checks.append(("Carnot limit between 600 K and 300 K is 0.5", abs(L.carnot_limit(600, 300) - 0.5) < 1e-12))
    checks.append(("zero efficiency when Qc = Qh", L.efficiency(500, 500) == 0.0))
    checks.append(("engine with efficiency 0.6 between 600 K and 300 K is not allowed", not L.is_allowed(1000, 400, 600, 300)))
    checks.append(("engine with efficiency 0.5 exactly at the limit is allowed (round-off safe)", L.is_allowed(1000, 500, 600, 300)))
    checks.append(("Qc larger than Qh is not allowed", not L.is_allowed(1000, 1200, 600, 300)))
    bad = 0
    for call in (lambda: L.efficiency(0, 0), lambda: L.carnot_limit(300, 600), lambda: L.carnot_limit(600, 0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
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
