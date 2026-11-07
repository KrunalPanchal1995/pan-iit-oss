"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    pl = L.scurve_plan(3.5, 2.5, 1.0, 1.5)
    v_hand = (-(1.0 / 1.5) + np.sqrt((1.0 / 1.5) ** 2 + 4 * 3.5)) / 2     # v^2 + (a/j) v - d = 0 with a = 1
    checks.append(("worked example: one floor (3.5 m) takes 4.47 s with a cruise speed of 1.57 m/s",
                   abs(pl["T"] - 4.467) < 0.005 and abs(pl["v"] - 1.567) < 0.005 and abs(pl["v"] - v_hand) < 1e-9))
    checks.append(("worked example: full-load cruise power at 1.567 m/s is 7.96 kW",
                   abs(L.cruise_power(1000.0, 800.0, 1360.0, pl["v"], 0.85) / 1000 - 7.96) < 0.01))
    checks.append(("hand calculation: trapezoid, 3.5 m, a = 1: T = 2 sqrt(3.5) = 3.74 s",
                   abs(L.trapezoid_time(3.5, 2.5, 1.0) - 2 * np.sqrt(3.5)) < 1e-12))
    p2 = L.scurve_plan(66.5, 4.0, 1.0, 1.5)
    checks.append(("express: 66.5 m at 4 m/s, T = d/v + v/a + a/j = 21.29 s",
                   abs(p2["T"] - (66.5 / 4 + 4.0 + 1 / 1.5)) < 1e-9 and abs(p2["T"] - 21.292) < 0.005))
    t, jerk, a, v, x = L.integrate_profile(p2)
    checks.append(("numerical integration: the profile ends at 66.5 m and stops (speed 0)",
                   abs(x[-1] - 66.5) < 0.02 and abs(v[-1]) < 0.005))
    checks.append(("the integrated profile respects the limits: |a| <= 1.0, |jerk| <= 1.5, v <= 4.0",
                   np.abs(a).max() <= 1.001 and np.abs(jerk).max() <= 1.5 + 1e-9 and v.max() <= 4.001))
    dd = 2.5 * L.accel_phase(2.5, 1.0, 1.5)[0]
    pb = L.scurve_plan(dd, 2.5, 1.0, 1.5)
    checks.append(("boundary: the distance that just reaches vmax gives zero cruise time",
                   abs(pb["tc"]) < 1e-9 and abs(pb["v"] - 2.5) < 1e-9))
    pn = L.scurve_plan(0.5, 2.5, 1.0, 1.5)
    checks.append(("very short ride (0.5 m): finite time and a cruise speed below the limit",
                   np.isfinite(pn["T"]) and pn["v"] < 2.5 and pn["T"] > 0))
    checks.append(("the S-curve is never faster than the trapezoid (the jerk limit costs time)",
                   all(L.scurve_time(d, 4.0, 1.0, 1.5) >= L.trapezoid_time(d, 4.0, 1.0) for d in (1.0, 3.5, 10.0, 66.5))))
    checks.append(("counterweight = car + 45% of 800 kg = 1360 kg; a balanced load makes cruise power zero",
                   L.counterweight_mass(1000.0, 800.0) == 1360.0
                   and abs(L.cruise_power(1000.0, 360.0, 1360.0, 3.0, 0.85)) < 1e-9))
    checks.append(("a light car going up is driven by the counterweight (negative power)",
                   L.cruise_power(1000.0, 0.0, 1360.0, 2.5, 0.85) < 0))
    checks.append(("peak force while accelerating: 4316 + 3160 * 1.0 = 7476 N for full load",
                   abs(L.peak_force(1000.0, 800.0, 1360.0, 1.0) - 7476.4) < 0.1))
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
