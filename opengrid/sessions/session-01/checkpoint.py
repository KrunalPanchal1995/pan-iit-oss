"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d = L.demand_curve(np.array([0.0, 8.0, 19.5]))
    checks.append(("demand curve: 500 MW at midnight, 750 MW at 19:30",
                   abs(d[0] - 500.0) < 1.0 and abs(d[2] - 750.0) < 1.0 and d[2] > d[1] > d[0]))
    f = L.grid_frequency(700.0, 800.0)
    checks.append(("worked example: 800 MW demand, 700 MW supply gives 49.762 Hz (a drop of 0.238 Hz)",
                   abs(f - 49.762) < 5e-4 and abs((50.0 - f) - 0.238) < 5e-4))
    checks.append(("hand calculation: a 50 MW shortage on the 1000 MW grid drops frequency by 0.119 Hz",
                   abs((50.0 - L.grid_frequency(950.0, 1000.0)) - 0.119) < 5e-4))
    checks.append(("balanced supply and demand gives exactly 50 Hz", L.grid_frequency(640.0, 640.0) == 50.0))
    checks.append(("surplus raises the frequency above 50 Hz", L.grid_frequency(900.0, 800.0) > 50.0))
    hrs, dem, sup, units = L.run_day()
    checks.append(("units add up to the supply at every hour", np.allclose(units.sum(axis=1), sup)))
    cap = np.array([u[1] for u in L.FLEET])
    checks.append(("no unit exceeds its size or goes negative", bool((units <= cap + 1e-9).all() and (units >= -1e-9).all())))
    ramp = np.array([u[2] for u in L.FLEET])
    checks.append(("no unit changes by more than its hourly ramp rate",
                   bool((np.abs(np.diff(units, axis=0)) <= ramp + 1e-9).all())))
    checks.append(("normal ramp rates keep supply within 5 MW of demand all day", float(np.abs(sup - dem).max()) < 5.0))
    _, dem2, sup2, _ = L.run_day(ramp_scale=0.25)
    checks.append(("with ramp rates cut to a quarter the gap exceeds 40 MW and the frequency falls below 49.95 Hz",
                   float(np.abs(sup2 - dem2).max()) > 40.0 and float(L.grid_frequency(sup2, dem2).min()) < 49.95))
    checks.append(("peak demand is 740 MW at hour 19 and the minimum is 500 MW (hourly steps)",
                   abs(dem.max() - 740.0) < 1.0 and int(hrs[dem.argmax()]) == 19 and abs(dem.min() - 500.0) < 1.0))
    checks.append(("grid stiffness 1/R + D = 20 + 1 = 21 on a 1000 MW base", L.STIFF == 1.0 / 0.05 + 1.0 and L.BASE == 1000.0))
    checks.append(("fleet: sizes add to 1200 MW and ramp rates to 230 MW per hour",
                   abs(sum(u[1] for u in L.FLEET) - 1200.0) < 1e-9 and abs(sum(u[2] for u in L.FLEET) - 230.0) < 1e-9))
    checks.append(("Section F answer B: 40 MW surplus gives 50.095 Hz", abs(L.grid_frequency(640.0, 600.0) - 50.095) < 5e-4))
    checks.append(("slope: 0.002381 Hz per MW, so a 42 MW imbalance moves the frequency by 0.1 Hz",
                   abs(50.0 / 21000.0 - 0.002381) < 5e-7 and abs((50.0 - L.grid_frequency(958.0, 1000.0)) - 0.1) < 1e-3))
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
