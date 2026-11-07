"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    err = L.validate_fixed_angle(30.0, 0.40, 0.30)
    checks.append(("simulation matches x = (1/2) a t^2 at 30 degrees to better than 1e-6 m", err < 1e-6))
    out = L.simulate_block(lambda t: 30.0, 0.40, 0.30, 2.0)
    checks.append(("worked example: after 2 s at 30 degrees the block has moved 4.71 m at 4.71 m/s",
                   abs(out["x"][-1] - 4.712) < 0.01 and abs(out["v"][-1] - 4.712) < 0.01))
    s = L.tilt_experiment(0.5, 0.4, 0.5)
    checks.append(("slow tilt: simulated slip angle equals atan(0.5) = 26.57 degrees within 0.01",
                   abs(s - 26.565) < 0.01 and abs(s - L.analytic_slip_angle(0.5)) < 0.01))
    checks.append(("slip angle does not depend on dt (4e-3 versus 1e-3 within 0.01 degrees)",
                   abs(L.tilt_experiment(0.5, 0.4, 0.5, 4e-3) - L.tilt_experiment(0.5, 0.4, 0.5, 1e-3)) < 0.01))
    still = L.simulate_block(lambda t: 20.0, 0.5, 0.4, 2.0)
    checks.append(("limit case: below the slide angle the block never moves", still["x"].max() == 0.0 and not still["sliding"].any()))
    mid = L.simulate_block(lambda t: 30.0 if t < 1.0 else 5.0, 0.4, 0.3, 6.0)
    a1 = L.analytic_acceleration(30.0, 0.3)
    a2 = L.analytic_acceleration(5.0, 0.3)
    expect = 0.5 * a1 + (a1 * 1.0) ** 2 / (2 * -a2)
    checks.append(("flatten the ramp: the block slides, stops and is stuck again at the exact stopping distance",
                   abs(mid["x"][-1] - expect) < 0.01 and mid["v"][-1] == 0.0 and not mid["sliding"][-1]))
    lo, hi = L.slip_angle_range(0.5, 0.05)
    checks.append(("hand calculation: mu_s 0.50 +- 0.05 gives slide angles 24.23 to 28.81 degrees",
                   abs(lo - 24.23) < 0.01 and abs(hi - 28.81) < 0.01))
    checks.append(("sensitivity formula: 0.05 / (1 + 0.5^2) rad = 2.29 degrees",
                   abs(0.05 * L.slip_angle_sensitivity(0.5) - 2.292) < 0.01))
    checks.append(("rolling: solid cylinder a = g sin t / 1.5 = 3.270 m/s^2 at 30 degrees",
                   abs(L.rolling_acceleration(30, 0.5) - 3.270) < 0.001))
    checks.append(("rolling: hollow tube a = 2.452 and time for 2 m is 1.277 s",
                   abs(L.rolling_acceleration(30, 1.0) - 2.4525) < 0.001 and abs(L.descent_time(2.4525, 2.0) - 1.277) < 0.001))
    checks.append(("rolling needs enough friction: solid cylinder at 30 degrees needs mu_s >= 0.192",
                   L.rolls_without_slipping(30, 0.5, 0.2) and not L.rolls_without_slipping(30, 0.5, 0.1)))
    ang = L.synthetic_tilt_trials()
    mu, low, high = L.estimate_mu(ang)
    checks.append(("mini-project data: estimate 0.418 with a range containing the true value 0.42",
                   abs(mu - 0.418) < 0.002 and low < 0.42 < high))
    checks.append(("edge case: frictionless block (mu = 0) slips at once and a = g sin t",
                   L.tilt_experiment(0.0, 0.0, 0.5) < 0.01 and abs(L.analytic_acceleration(30, 0.0) - 4.905) < 1e-3))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
