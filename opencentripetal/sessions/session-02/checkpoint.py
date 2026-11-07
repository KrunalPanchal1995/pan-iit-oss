"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # worked example: design angle for 80 km/h at r = 100 m
    v = 80 / 3.6
    th = L.ideal_bank_angle(v, 100.0)
    tan_hand = (80 / 3.6) ** 2 / (9.81 * 100.0)
    checks.append((f"worked example: 80 km/h at r = 100 m needs tan(theta) = 0.5034, theta = 26.72 degrees (got {np.degrees(th):.2f})",
                   abs(np.tan(th) - tan_hand) < 1e-9 and abs(np.degrees(th) - 26.72) < 0.01))
    checks.append(("worked example: flat wet curve (mu = 0.4, r = 100 m) top speed is 19.81 m/s = 71.3 km/h",
                   abs(L.flat_max_speed(0.4, 100.0) - 19.81) < 0.01 and abs(L.kmh(L.flat_max_speed(0.4, 100.0)) - 71.3) < 0.1))
    lo, hi = L.bank_speed_limits(th, 0.4, 100.0)
    checks.append(("worked example: on that 26.72 degree bank with mu = 0.4 the safe range is 33.1 to 119.9 km/h",
                   abs(L.kmh(lo) - 33.1) < 0.1 and abs(L.kmh(hi) - 119.9) < 0.1))
    # frictionless limit: both limits collapse to the ideal speed
    lo0, hi0 = L.bank_speed_limits(th, 0.0, 100.0)
    checks.append(("mu = 0: both limits equal the ideal speed 80 km/h", abs(lo0 - v) < 1e-9 and abs(hi0 - v) < 1e-9))
    # three-way verification of the derived formula
    ok = True
    for deg, mu, r in ((30, 0.3, 100.0), (20, 0.5, 60.0), (35, 0.2, 150.0), (45, 0.1, 80.0)):
        t = np.radians(deg)
        lo, hi = L.bank_speed_limits(t, mu, r)
        s_hi = L.limit_speed_by_solving(t, mu, r, +1)[0]
        s_lo = L.limit_speed_by_solving(t, mu, r, -1)[0]
        ok &= abs(hi - s_hi) < 1e-9 and abs(lo - s_lo) < 1e-9
        ok &= L.grips(hi * 0.999, t, mu, r) and not L.grips(hi * 1.001, t, mu, r)
        if lo > 0:
            ok &= L.grips(lo * 1.001, t, mu, r) and not L.grips(lo * 0.999, t, mu, r)
    checks.append(("formula agrees with the solved force equations and with the grip test at four banks", bool(ok)))
    slo, shi = L.limits_by_scan(np.radians(30), 0.3, 100.0)
    flo, fhi = L.bank_speed_limits(np.radians(30), 0.3, 100.0)
    checks.append(("a brute-force scan finds the same range to within its 0.04 m/s step", abs(slo - flo) < 0.05 and abs(shi - fhi) < 0.05))
    # flat curve is the special case theta = 0
    lo, hi = L.bank_speed_limits(0.0, 0.7, 100.0)
    checks.append(("zero bank reproduces the flat-curve limit sqrt(mu g r)", abs(hi - L.flat_max_speed(0.7, 100.0)) < 1e-9 and lo == 0.0))
    # edge: very steep bank with high friction cannot slide outward
    checks.append(("edge case: mu tan(theta) >= 1 gives no upper limit", L.bank_speed_limits(np.radians(50), 0.9, 100.0)[1] == np.inf))
    # design with wet margin
    t = L.min_bank_for_speed(v, 0.3, 100.0)
    checks.append((f"design: smallest bank for 80 km/h at mu = 0.3 is 10.02 degrees (got {np.degrees(t):.2f}) and 80 km/h is then exactly the top speed",
                   abs(np.degrees(t) - 10.02) < 0.01 and abs(L.bank_speed_limits(t, 0.3, 100.0)[1] - v) < 1e-6))
    checks.append(("design: a flat road is already enough when v <= sqrt(mu g r)", L.min_bank_for_speed(10.0, 0.7, 100.0) == 0.0))
    checks.append(("a wetter road lowers the flat limit", L.flat_max_speed(0.4, 100) < L.flat_max_speed(0.7, 100)))
    checks.append(("units: 80 km/h is 22.22 m/s", abs(L.ms(80) - 22.2222) < 1e-3))
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
