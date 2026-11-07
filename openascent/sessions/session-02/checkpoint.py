"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    g0 = 9.80665
    checks.append(("worked example: TWR of 1.5 MN on 100 t is 1.53", abs(L.thrust_to_weight(1.5e6, 100e3) - 1.5296) < 1e-3))
    checks.append(("worked example: mass flow 510 kg/s", abs(L.mass_flow(1.5e6, 300.0) - 509.9) < 0.1))
    tb, vb, hb = L.analytic_burn(300.0, 1.5e6, 100e3, 75e3)
    checks.append(("worked example: burn time 147.1 s, burnout speed 2636 m/s, height 126.7 km",
                   abs(tb - 147.1) < 0.1 and abs(vb - 2635.9) < 0.5 and abs(hb - 126690) < 100))
    checks.append(("hand calculation: speed = rocket equation minus g0 t_b",
                   abs(vb - (300 * g0 * np.log(4) - g0 * tb)) < 1e-6))
    checks.append(("worked example: coasts to about 481 km", abs(L.coast_height(hb, vb) - 480.9e3) < 500))
    single = [dict(prop=75e3, dry=25e3, isp=300.0, F=1.5e6)]
    r = L.vertical_flight(single, 0.0, dt=1.0, method="rk4", gravity="constant", drag=False, t_end=tb)
    checks.append(("RK4 with dt = 1 s matches the exact burnout speed within 0.01 m/s", abs(r["v"][-1] - vb) < 0.01))
    checks.append(("RK4 matches the exact burnout height within 1 m", abs(r["h"][-1] - hb) < 1.0))
    e1 = L.vertical_flight(single, 0.0, dt=1.0, method="euler", gravity="constant", drag=False, t_end=tb)
    e2 = L.vertical_flight(single, 0.0, dt=0.5, method="euler", gravity="constant", drag=False, t_end=tb)
    err1, err2 = abs(e1["v"][-1] - vb), abs(e2["v"][-1] - vb)
    checks.append((f"Euler is first order: halving dt halves the error ({err1:.2f} -> {err2:.2f} m/s)", 1.8 < err1 / err2 < 2.2))
    nog = L.vertical_flight(single, 0.0, dt=1.0, gravity="constant", drag=False, t_end=tb)
    checks.append(("gravity loss is g0 t_b: rocket equation - simulated speed",
                   abs((300 * g0 * np.log(4) - nog["v"][-1]) - g0 * tb) < 0.05))
    full, nodrag = L.vertical_flight(), L.vertical_flight(drag=False)
    checks.append(("drag lowers the top of the flight", full["h"].max() < nodrag["h"].max()))
    checks.append(("straight up, the launcher falls back to the ground (no orbit)", full["h"][-1] <= 0.0))
    checks.append(("staging happens: two burnouts recorded", len(full["events"]) == 2))
    losses = L.gravity_loss_vs_twr(np.array([1.2, 2.4]))
    checks.append(("doubling TWR halves the gravity loss", abs(losses[0] / losses[1] - 2.0) < 1e-9))
    bad = 0
    for call in (lambda: L.thrust_to_weight(1e6, 0), lambda: L.analytic_burn(300, 1e6, 1e5, 2e5),
                 lambda: L.vertical_flight([dict(prop=9e4, dry=1e4, isp=300, F=5e5)], 0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs (including TWR below 1) raise ValueError", bad == 3))
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
