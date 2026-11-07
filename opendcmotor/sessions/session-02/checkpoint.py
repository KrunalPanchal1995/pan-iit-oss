"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: stall torque 0.300 N m and no-load speed 240 rad/s (2292 rpm)",
                   abs(L.stall_torque() - 0.30) < 1e-12 and abs(L.no_load_speed() - 240.0) < 1e-12
                   and abs(L.rpm(240.0) - 2291.8) < 0.1))
    checks.append(("worked example: stall current V/R = 6 A", abs(L.current_at_speed(0.0) - 6.0) < 1e-12))
    wp, Pp = L.peak_power()
    checks.append(("worked example: ideal peak power 18 W at 120 rad/s with efficiency exactly 50 percent",
                   abs(wp - 120.0) < 1e-9 and abs(Pp - 18.0) < 1e-9 and abs(L.efficiency(wp) - 0.5) < 1e-12))
    wf, Pf = L.peak_power(b=L.B0)
    checks.append(("worked example: with friction the peak is 17.31 W at 115.4 rad/s and efficiency 46.3 percent (below 50)",
                   abs(wf - 115.385) < 0.01 and abs(Pf - 17.308) < 0.01 and abs(L.efficiency(wf, b=L.B0) - 0.4630) < 0.001
                   and L.efficiency(wf, b=L.B0) < 0.5))
    T0, w0, err = L.numeric_line()
    checks.append(("numeric fit of T = k I agrees with the formulas", abs(T0 - 0.30) < 1e-9 and abs(w0 - 240.0) < 1e-6 and err < 1e-9))
    w = np.linspace(0, 235, 60)
    scan = [max(L.mech_power(x, b=L.B0) for x in np.linspace(0, 230.7, 4001))]
    checks.append(("brute-force scan finds the same peak power as the formula", abs(scan[0] - Pf) < 0.01))
    checks.append(("k_e = k_t: back-voltage power k w I equals mechanical power T w when b = 0",
                   all(abs(L.K0 * x * L.current_at_speed(x) - L.shaft_torque(x) * x) < 1e-12 for x in w)))
    ws = np.linspace(1.0, 229.0, 4561)
    eff = np.array([L.efficiency(x, b=L.B0) for x in ws])
    checks.append(("best efficiency with friction is about 67 percent near 193 rad/s, above the peak-power speed",
                   abs(eff.max() - 0.672) < 0.005 and abs(ws[eff.argmax()] - 193.0) < 2.0 and ws[eff.argmax()] > wf))
    checks.append(("hand calculation: 1000 rpm is 104.72 rad/s", abs(L.rad_per_s(1000) - 104.72) < 0.01))
    T_load = 5.0 * 9.81 * 0.02
    best, op = L.choose_ratio(T_load, 5.0, 1.5, range(5, 61))
    checks.append(("worked example: best gear ratio for the winch is 22 with output about 8.8 rad/s",
                   best == 22 and 8.7 < op["w_out"] < 8.8 and op["current"] <= 1.5 and 0.60 < op["eff"] < 0.61))
    ok = [N for N in range(5, 61) if (lambda o: o["moves"] and o["w_out"] >= 5.0 and o["current"] <= 1.5)(L.operating_point(T_load, N))]
    checks.append(("the allowed ratio window is 17 to 42", ok[0] == 17 and ok[-1] == 42))
    checks.append(("a ratio of 3 cannot lift the load (motor stalls)", not L.operating_point(T_load, 3)["moves"]))
    checks.append(("gear box: torque x ratio, speed / ratio (power x eta)",
                   abs(L.operating_point(0.5, 10)["w_out"] * 10 - L.operating_point(0.5, 10)["w_motor"]) < 1e-12))
    none, _ = L.choose_ratio(T_load, 50.0, 1.5, range(5, 61))
    checks.append(("an impossible speed requirement returns no ratio", none is None))
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
