"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("36 km/h is 10 m/s", abs(L.kmh_to_ms(36.0) - 10.0) < 1e-12))
    checks.append(("kinetic energy of 1000 kg at 10 m/s is 50 kJ", abs(L.kinetic_energy(1000.0, 10.0) - 50000.0) < 1e-6))
    f = L.stopping_force(1000.0, 10.0, 0.5)
    checks.append(("hand calculation: 1000 kg, 10 m/s, 0.5 m needs 100 kN", abs(f - 100000.0) < 1e-6))
    checks.append(("doubling the distance halves the force", abs(L.stopping_force(1000.0, 10.0, 1.0) * 2 - f) < 1e-6))
    checks.append(("doubling the speed quadruples the force", abs(L.stopping_force(1000.0, 20.0, 0.5) / f - 4.0) < 1e-9))
    # worked example: 1000 kg at 50 km/h stopped in 0.5 m
    v = L.kmh_to_ms(50.0)
    fw = L.stopping_force(1000.0, v, 0.5)
    gw = L.deceleration_g(1000.0, v, 0.5)
    checks.append((f"worked example: 1000 kg at 50 km/h in 0.5 m gives {fw / 1000:.1f} kN = {gw:.1f} g",
                   abs(fw / 1000 - 192.9) < 0.1 and abs(gw - 19.7) < 0.05))
    checks.append(("deceleration in g does not depend on mass",
                   abs(L.deceleration_g(500.0, v, 0.5) - L.deceleration_g(2000.0, v, 0.5)) < 1e-9))
    try:
        L.stopping_force(1000.0, 10.0, 0.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("a zero stopping distance is rejected (it would need an infinite force)", ok))
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
