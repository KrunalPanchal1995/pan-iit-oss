"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    Ts = L.spring_period(0.5, 20.0)
    checks.append(("worked example: spring 0.5 kg, 20 N/m has T = 0.993 s and f = 1.007 Hz",
                   abs(Ts - 0.9935) < 1e-3 and abs(L.frequency(Ts) - 1.0066) < 1e-3))
    Tp = L.pendulum_period(1.0)
    checks.append(("worked example: pendulum of 1 m has T = 2.006 s", abs(Tp - 2.0061) < 1e-3))
    checks.append(("hand calculation: 2 pi sqrt(0.25 / 9.81) = 1.003 s for L = 0.25 m", abs(L.pendulum_period(0.25) - 1.0030) < 1e-3))
    checks.append(("four times the length doubles the period", abs(L.pendulum_period(4.0) / L.pendulum_period(1.0) - 2.0) < 1e-9))
    checks.append(("four times the mass doubles the spring period", abs(L.spring_period(2.0, 20.0) / L.spring_period(0.5, 20.0) - 2.0) < 1e-9))
    t = np.linspace(0, 4, 4001)
    checks.append(("measured spring period matches the formula within 0.1 percent",
                   abs(L.measure_period(t, L.spring_x(t, 0.05, 0.5, 20.0)) - Ts) < 1e-3 * Ts))
    xp = L.pendulum_x(t, 8.0, 1.0)
    checks.append(("measured pendulum period matches the formula within 0.1 percent", abs(L.measure_period(t, xp) - Tp) < 1e-3 * Tp))
    checks.append(("amplitude of a 5 cm spring swing is 5 cm", abs(L.amplitude(L.spring_x(t, 0.05, 0.5, 20.0)) - 0.05) < 1e-4))
    checks.append(("edge: less than one full swing gives nan, not a number",
                   np.isnan(L.measure_period(np.linspace(0, 0.5, 100), L.spring_x(np.linspace(0, 0.5, 100), 0.05, 0.5, 20.0)))))
    try:
        L.spring_period(0.0, 20.0)
        bad = True
    except ValueError:
        bad = False
    checks.append(("edge: zero mass is rejected", not bad))
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
