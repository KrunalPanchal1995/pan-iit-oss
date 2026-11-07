"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    k = L.drag_k()
    vt = L.terminal_speed()
    checks.append((f"worked example: k = 9.24e-4 kg/m and terminal speed 41.2 m/s for the cricket ball (got {k:.3e}, {vt:.1f})",
                   abs(k - 9.236e-4) < 1e-6 and abs(vt - 41.22) < 0.01))
    area = np.pi * 0.07 ** 2 / 4
    checks.append(("hand calculation: v_t = sqrt(2 m g / (rho Cd A)) from the numbers",
                   abs(vt - np.sqrt(2 * 0.16 * 9.81 / (1.2 * 0.4 * area))) < 1e-9))
    a_launch = (k / L.MASS) * 35.0 ** 2
    checks.append((f"worked example: drag deceleration at 35 m/s is 7.07 m/s^2 (got {a_launch:.2f})", abs(a_launch - 7.07) < 0.01))
    s = L.simulate(35.0, 40.0, 1.0)
    checks.append((f"worked example: with drag, 35 m/s at 40 degrees from 1 m lands at 83.5 m after 4.14 s (got {s['range']:.1f} m, {s['flight']:.2f} s)",
                   abs(s["range"] - 83.5) < 0.05 and abs(s["flight"] - 4.14) < 0.01))
    # validation 1: drag off equals the exact formulas
    for ang, h0 in ((40.0, 1.0), (20.0, 0.0), (70.0, 2.0)):
        f = L.simulate(35.0, ang, h0, cd=0.0)
        ok1 = abs(f["range"] - L.exact_range(35.0, ang, h0)) < 1e-6 and abs(f["flight"] - L.exact_flight(35.0, ang, h0)) < 1e-6
        checks.append((f"validation: drag off reproduces the exact range and flight time ({ang:.0f} deg, h0 {h0} m)", ok1))
    # validation 2: energy books
    checks.append(("validation: RK4 energy + drag work stays constant to 1e-9 (relative)", L.energy_error(s) < 1e-9))
    checks.append(("validation: the energy check also holds with a wind", L.energy_error(L.simulate(35.0, 40.0, 1.0, wind=-5.0)) < 1e-9))
    checks.append(("drag always shortens the shot and lowers its peak",
                   s["range"] < L.simulate(35.0, 40.0, 1.0, cd=0.0)["range"] and s["peak"] < L.simulate(35.0, 40.0, 1.0, cd=0.0)["peak"]))
    # best angle
    ba, br = L.best_angle(35.0, 1.0)
    bf, _ = L.best_angle(35.0, 1.0, cd=0.0)
    checks.append((f"best angle with drag is about 41.5 degrees (got {ba:.2f}), below the no-drag {bf:.2f}", abs(ba - 41.47) < 0.05 and ba < bf - 3))
    checks.append(("the best angle is below 45 degrees for every speed tried and falls as speed rises",
                   all(L.best_angle(v)[0] < 45 for v in (15, 25, 45)) and L.best_angle(45)[0] < L.best_angle(15)[0]))
    checks.append(("edge: with drag off on level ground the numerical best angle is 45 degrees", abs(L.best_angle(30.0, cd=0.0)[0] - 45.0) < 0.05))
    # time step
    ref = s["range"]
    e5 = L.simulate(35.0, 40.0, 1.0, dt=0.5, method="euler")
    r5 = L.simulate(35.0, 40.0, 1.0, dt=0.5)
    checks.append((f"failure case: Euler with dt 0.5 is {100 * (e5['range'] / ref - 1):.0f} percent too long and fails the energy check; RK4 stays within 0.01 m",
                   e5["range"] / ref > 1.05 and L.energy_error(e5) > 0.1 and abs(r5["range"] - ref) < 0.01))
    checks.append(("Euler improves as dt shrinks (error roughly proportional to dt)",
                   abs(L.simulate(35.0, 40.0, 1.0, dt=0.05, method="euler")["range"] - ref) < abs(L.simulate(35.0, 40.0, 1.0, dt=0.2, method="euler")["range"] - ref)))
    # terminal speed
    checks.append(("a dropped ball approaches the terminal speed (within 0.5 percent after 20 s) and never exceeds it",
                   abs(L.fall_speed(20.0) - vt) / vt < 0.005 and L.fall_speed(40.0) <= vt + 1e-9))
    # sensitivity
    r_lo = L.simulate(35.0, 40.0, 1.0, cd=0.3)["range"]
    r_hi = L.simulate(35.0, 40.0, 1.0, cd=0.5)["range"]
    checks.append(("sensitivity: a higher drag coefficient gives a shorter range (90.5, 83.5, 77.7 m for 0.3, 0.4, 0.5)",
                   r_lo > ref > r_hi and abs(r_lo - 90.5) < 0.1 and abs(r_hi - 77.7) < 0.1))
    tail = L.simulate(35.0, 40.0, 1.0, wind=5.0)["range"]
    head = L.simulate(35.0, 40.0, 1.0, wind=-5.0)["range"]
    checks.append(("sensitivity: a 5 m/s tailwind adds about 8.5 m, a 5 m/s headwind loses about 9 m", abs(tail - 92.0) < 0.1 and abs(head - 74.4) < 0.1))
    # mini-project
    v6 = L.min_speed_for_range(70.0, 1.0)
    v6_free = L.min_speed_for_range(70.0, 1.0, cd=0.0)
    checks.append((f"mini-project: lowest speed for a six at 70 m from 1 m is 30.9 m/s (got {np.ceil(v6 * 10) / 10:.1f}); without drag it is 26.0",
                   abs(np.ceil(v6 * 10) / 10 - 30.9) < 1e-9 and abs(v6_free - 26.02) < 0.02))
    checks.append(("mini-project: at 32 m/s the whole-degree angles 32 to 52 clear the rope", L.angle_window(32.0, 70.0, 1.0) == (32, 52)))
    checks.append(("edge: a ball that is not thrown goes nowhere, and a straight-up ball comes back near the start",
                   L.simulate(0.0, 45.0)["range"] < 1e-9 and abs(L.simulate(20.0, 90.0)["range"]) < 0.5))
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
