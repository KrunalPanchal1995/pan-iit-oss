"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("10 lux gives 10 000 ohm (the model's anchor)", abs(float(L.ldr_resistance(10.0)) - 10_000.0) < 1e-6))
    r100 = float(L.ldr_resistance(100.0))
    checks.append((f"worked example: 100 lux gives about 1 995 ohm (got {r100:.0f})", abs(r100 - 1995.3) < 1.0))
    r2 = float(L.ldr_resistance(2.0))
    checks.append((f"worked example: 2 lux gives about 30 850 ohm (got {r2:.0f})", abs(r2 - 10_000 * 0.2 ** -0.7) < 1.0 and abs(r2 - 30_852) < 5))
    lux = np.logspace(-1, 4, 60)
    checks.append(("resistance falls steadily as light rises", bool(np.all(np.diff(L.ldr_resistance(lux)) < 0))))
    checks.append(("ten times more light divides resistance by 10 ** 0.7 = 5.01",
                   abs(float(L.ldr_resistance(10.0) / L.ldr_resistance(100.0)) - 10 ** 0.7) < 1e-9))
    checks.append(("dark (5 lux) switches the LED on at a 20 lux threshold", bool(L.led_is_on(5.0, 20.0))))
    checks.append(("bright (300 lux) keeps the LED off", not bool(L.led_is_on(300.0, 20.0))))
    checks.append(("exactly at the threshold the LED stays off (strict comparison)", not bool(L.led_is_on(20.0, 20.0))))
    checks.append(("the block diagram has four blocks", len(L.BLOCKS) == 4))
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
