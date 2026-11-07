"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    r = L.R_EARTH + 400e3
    v = L.circular_speed(r)
    checks.append((f"worked example: 400 km orbit speed is 7.67 km/s (got {v / 1e3:.3f})", abs(v / 1e3 - 7.67) < 0.005))
    checks.append((f"worked example: 400 km orbit period is 92.4 min (got {L.period(r) / 60:.2f})", abs(L.period(r) / 60 - 92.4) < 0.05))
    checks.append(("gravity at 400 km is 8.69 m/s^2", abs(L.gravity(r) - 8.69) < 0.005))
    checks.append(("gravity at the surface is about 9.82 m/s^2", abs(L.gravity(L.R_EARTH) - 9.82) < 0.005))
    fall, curve = L.free_fall(r, 1.0), L.ground_curves_away(r, v, 1.0)
    checks.append((f"in 1 s a satellite falls 4.35 m and the ground curves away 4.35 m (got {fall:.3f}, {curve:.3f})",
                   abs(fall - 4.35) < 0.005 and abs(fall - curve) < 0.01))
    checks.append(("a slower object falls further than the ground curves away",
                   L.free_fall(r, 1.0) > L.ground_curves_away(r, 0.5 * v, 1.0)))
    rg = 42164e3
    checks.append((f"geostationary radius: period is 86164 s, speed 3.07 km/s (got {L.period(rg):.1f} s)",
                   abs(L.period(rg) - 86164) < 1.0 and abs(L.circular_speed(rg) / 1e3 - 3.07) < 0.005))
    rows = {int(h): (vv, tt) for h, vv, tt in L.altitude_table([200, 400, 1000, 20200, 35786])}
    checks.append(("1000 km: 7.35 km/s and 105.0 min", abs(rows[1000][0] - 7.35) < 0.005 and abs(rows[1000][1] - 105.0) < 0.05))
    checks.append(("200 km: 7.79 km/s and 88.4 min", abs(rows[200][0] - 7.79) < 0.005 and abs(rows[200][1] - 88.4) < 0.05))
    checks.append(("20200 km: 3.87 km/s and 718.4 min", abs(rows[20200][0] - 3.87) < 0.005 and abs(rows[20200][1] - 718.4) < 0.05))
    checks.append(("35786 km: 3.07 km/s and 1435.7 min (23.93 hours)", abs(rows[35786][0] - 3.07) < 0.005 and abs(rows[35786][1] - 1435.7) < 0.1))
    r100 = L.radius_for_period(6000.0)
    checks.append((f"design: a 100 minute orbit is at 765.6 km altitude and 7.473 km/s (got {(r100 - L.R_EARTH) / 1e3:.1f}, {L.circular_speed(r100) / 1e3:.3f})",
                   abs((r100 - L.R_EARTH) / 1e3 - 765.6) < 0.05 and abs(L.circular_speed(r100) / 1e3 - 7.473) < 0.0005 and abs(L.period(r100) - 6000.0) < 1e-6))
    speeds = [rows[k][0] for k in sorted(rows)]
    periods = [rows[k][1] for k in sorted(rows)]
    checks.append(("higher orbits are slower and take longer", bool(np.all(np.diff(speeds) < 0) and np.all(np.diff(periods) > 0))))
    ratios = [L.kepler3_constant(a) for a in (7e6, 1e7, 2.6e7, 4.2e7)]
    checks.append(("Kepler 3: T^2/a^3 is the same for every orbit", max(ratios) / min(ratios) - 1 < 1e-12))
    checks.append(("Kepler 3 constant equals 4 pi^2 / mu", abs(ratios[0] * L.MU / (4 * np.pi**2) - 1) < 1e-12))
    rp, ra, vp = 7.0e6, 1.4e7, 8000.0
    va = L.apogee_speed(vp, rp, ra)
    checks.append(("Kepler 2: farther point is slower (half the distance ratio gives half the speed)", abs(va - 4000.0) < 1e-9))
    checks.append(("Kepler 2: equal area per second at both ends", abs(L.area_per_second(rp, vp) - L.area_per_second(ra, va)) < 1e-3))
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
