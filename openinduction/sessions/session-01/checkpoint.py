"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: 200 turns, 0.5 mWb in 0.05 s gives 2 V; twice as fast gives 4 V",
                   abs(L.average_emf(200, 0.0005, 0.05) - 2.0) < 1e-12 and abs(L.average_emf(200, 0.0005, 0.025) - 4.0) < 1e-12))
    checks.append(("hand calculation: 100 turns, 0.1 T, 0.002 m^2, 5 Hz peak is 0.628 V",
                   abs(L.peak_emf(100, 0.1, 0.002, 5) - 0.6283185) < 1e-6))
    checks.append(("no change of flux gives no voltage", L.average_emf(500, 0.0, 1.0) == 0.0))
    checks.append(("double the turns doubles the average voltage",
                   abs(L.average_emf(400, 0.001, 0.1) / L.average_emf(200, 0.001, 0.1) - 2) < 1e-12))

    t1, _, e1 = L.magnet_pass(0.5, 200)
    t2, _, e2 = L.magnet_pass(1.0, 200)
    t3, _, e3 = L.magnet_pass(0.5, 400)
    checks.append(("twice the magnet speed doubles the peak voltage", abs(abs(e2).max() / abs(e1).max() - 2) < 0.01))
    checks.append(("twice the turns doubles the peak voltage", abs(abs(e3).max() / abs(e1).max() - 2) < 0.01))
    area1 = np.trapezoid(np.clip(e1, 0, None), t1)
    area2 = np.trapezoid(np.clip(e2, 0, None), t2)
    checks.append(("the area of one pulse (volt-seconds) does not depend on speed", abs(area1 - area2) < 1e-4))
    checks.append(("Lenz: voltage going in and coming out have opposite signs",
                   e1[:len(e1) // 2].mean() * e1[len(e1) // 2:].mean() < 0))

    t = np.linspace(0, 0.4, 4001)
    e = L.rotating_emf(t, 100, 0.1, 0.002, 5)
    checks.append(("a rotating coil gives an alternating voltage (both signs)", e.max() > 0.6 and e.min() < -0.6))
    checks.append(("the voltage never exceeds the peak formula", abs(e).max() <= L.peak_emf(100, 0.1, 0.002, 5) + 1e-12))
    checks.append(("voltage is zero at time zero (coil facing the field)", abs(L.rotating_emf(0.0, 100, 0.1, 0.002, 5)) < 1e-12))
    try:
        L.average_emf(100, 0.001, 0.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("a zero time interval is rejected", ok))
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
