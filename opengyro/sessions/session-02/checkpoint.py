"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    m, R, r = 2.0, 0.30, 0.25
    I = L.disc_inertia(m, R)
    checks.append(("disc: I = m R^2 / 2 = 0.09 kg m^2 for 2 kg and 0.30 m", abs(I - 0.09) < 1e-12))
    checks.append(("ring has twice the inertia of a disc", abs(L.ring_inertia(m, R) - 2 * I) < 1e-12))
    # hand calculation: m g r / (I w) = 2 * 9.81 * 0.25 / (0.09 * 20) = 2.725 rad/s
    checks.append(("hand calculation: 20 rad/s gives 2.725 rad/s", abs(L.precession_rate(m, r, I, 20.0) - 2.725) < 1e-3))
    # worked example: one circle in 4 s needs 34.70 rad/s = 331 rpm
    w = L.spin_for_period(m, r, I, 4.0)
    checks.append((f"worked example: one circle per 4 s needs 34.70 rad/s = 331 rpm (got {w:.2f}, {L.rpm(w):.0f})",
                   abs(w - 34.70) < 0.01 and round(L.rpm(w)) == 331))
    checks.append(("with that spin the period is 4 s", abs(L.precession_period(m, r, I, w) - 4.0) < 1e-9))
    checks.append(("double the spin, double the period", abs(L.precession_period(m, r, I, 2 * w) / 4.0 - 2.0) < 1e-9))
    checks.append(("horizontal axle: exact equals formula", abs(L.precession_exact(m, R, r, w, np.pi / 2) - 2 * np.pi / 4.0) < 1e-9))
    ex = L.precession_exact(m, R, r, w, np.radians(60))
    checks.append(("tilted 60 degrees the exact rate is within 5 percent of the formula here", abs(ex / L.precession_rate(m, r, I, w) - 1) < 0.05))
    big = L.precession_exact(m, R, r, 1000.0, np.radians(60))
    checks.append(("for a much faster spin the formula is better than 0.5 percent", abs(big / L.precession_rate(m, r, I, 1000.0) - 1) < 0.005))
    checks.append(("too slow a spin has no steady precession (nan)", np.isnan(L.precession_exact(m, R, r, 10.0, np.radians(30)))))
    checks.append(("fast-spin ratio is 2.92 for the design", abs(L.fast_spin_ratio(m, R, r, w) - 2.92) < 0.01))
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
