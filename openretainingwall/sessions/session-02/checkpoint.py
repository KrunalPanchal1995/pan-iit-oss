"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    phis = np.linspace(5, 60, 12)
    checks.append(("the tan^2(45 - phi/2) and (1 - sin)/(1 + sin) forms agree for every phi",
                   all(abs(L.ka_tan(p) - L.ka_sin(p)) < 1e-12 for p in phis)))
    checks.append(("phi = 30 degrees gives Ka = 1/3", abs(L.ka_sin(30.0) - 1.0 / 3.0) < 1e-12))
    checks.append(("edge: phi = 0 (a fluid) gives Ka = 1", abs(L.ka_sin(0.0) - 1.0) < 1e-12))
    checks.append(("pressure at the base of 4 m is Ka gamma H = 24 kPa and zero at the top",
                   abs(float(L.pressure(4.0, 30.0, 18.0)) - 24.0) < 1e-9 and float(L.pressure(0.0, 30.0, 18.0)) == 0.0))
    checks.append(("worked example: Pa = 0.5 * (1/3) * 18 * 16 = 48 kN/m", abs(L.active_force(4.0, 30.0, 18.0) - 48.0) < 1e-9))
    # the area of the pressure triangle equals Pa, and its centroid is H/3 above the base
    z = (np.arange(4000) + 0.5) * 4.0 / 4000
    p = L.pressure(z, 30.0, 18.0)
    area = float(np.sum(p) * 4.0 / 4000)
    arm = float(np.sum(p * (4.0 - z)) * 4.0 / 4000) / area
    checks.append(("integrating the pressure gives 48 kN/m acting 1.333 m above the base",
                   abs(area - 48.0) < 1e-3 and abs(arm - 4.0 / 3.0) < 1e-3))
    checks.append(("a 10 kPa surcharge adds Ka q H = 13.33 kN/m", abs(L.surcharge_force(4.0, 30.0, 10.0) - 40.0 / 3.0) < 1e-9))
    pa, ps = L.active_force(4.0, 30.0, 18.0), L.surcharge_force(4.0, 30.0, 10.0)
    arm2 = (pa * 4.0 / 3.0 + ps * 2.0) / (pa + ps)
    checks.append(("with the surcharge the total is 61.33 kN/m and acts 1.478 m above the base",
                   abs(pa + ps - 61.3333) < 1e-3 and abs(arm2 - 1.4783) < 1e-3))
    so, wa, tot = L.saturated_force(4.0, 30.0, 20.0)
    checks.append(("saturated backfill: water alone is 0.5 * 9.81 * 16 = 78.5 kN/m, soil 27.2, total 105.7",
                   abs(wa - 78.48) < 1e-9 and abs(so - 27.1733) < 1e-3 and abs(tot - 105.65) < 0.01))
    checks.append(("saturation raises the force by a factor of about 2.2",
                   abs(tot / L.active_force(4.0, 30.0, 18.0) - 2.2011) < 1e-3))
    checks.append(("phi 25 versus 35 degrees: Ka 0.4059 versus 0.2710, Pa 58.4 versus 39.0 kN/m",
                   abs(L.ka_sin(25) - 0.4059) < 1e-4 and abs(L.ka_sin(35) - 0.2710) < 1e-4
                   and abs(L.active_force(4, 25, 18) - 58.44) < 0.01 and abs(L.active_force(4, 35, 18) - 39.02) < 0.01))
    checks.append(("Ka at 35 degrees is about one third lower than at 25 degrees",
                   abs(1.0 - L.ka_sin(35) / L.ka_sin(25) - 0.3324) < 1e-3))
    checks.append(("a 10 degree error in phi changes the 4 m push by about 50 percent of the lower value (58.44 / 39.02 = 1.498)",
                   abs(L.active_force(4, 25, 18) / L.active_force(4, 35, 18) - 1.4977) < 1e-3))
    checks.append(("the surcharge costs about half a metre of height (4.47 m to 3.95 m)", abs((4.4721 - 3.951) - 0.52) < 0.01))
    checks.append(("hand calculation: H = 3 m, gamma = 19, phi = 30 gives 28.5 kN/m",
                   abs(L.active_force(3.0, 30.0, 19.0) - 28.5) < 1e-9))
    h = L.max_height(60.0, 30.0, 18.0)
    checks.append(("design: the tallest wall with Pa <= 60 kN/m is 4.47 m",
                   abs(h - 4.4721) < 1e-3 and abs(L.active_force(h, 30.0, 18.0) - 60.0) < 1e-9))
    # with a 10 kPa surcharge: 3 H^2 + (10/3) H - 60 = 0
    hs = float(np.max(np.roots([3.0, 10.0 / 3.0, -60.0])))
    checks.append(("design with a 10 kPa surcharge: tallest wall is 3.95 m",
                   abs(hs - 3.951) < 1e-3 and abs(L.active_force(hs, 30.0, 18.0) + L.surcharge_force(hs, 30.0, 10.0) - 60.0) < 1e-6))
    t = L.active_force(4.0, 36.0, 18.0)
    checks.append(("challenge: phi = 36 degrees brings the 4 m push under 40 kN/m but phi = 34 does not",
                   t <= 40.0 and L.active_force(4.0, 34.0, 18.0) > 40.0))
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
