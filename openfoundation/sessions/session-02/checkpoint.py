"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    exact = math.sqrt(600 / (150 - 24 * 0.6))
    checks.append(("worked example: 600 kN, 150 kPa, t = 0.6 m needs exactly 2.104 m, rounded up to 2.15 m",
                   abs(exact - 2.1038) < 1e-3 and abs(L.required_side(600, 150) - 2.15) < 1e-9))
    checks.append(("worked example: at 2.15 m the contact pressure is 144.2 kPa, at 2.10 m it is 150.5 kPa (fails)",
                   abs(L.contact_pressure(600, 2.15) - 144.2) < 0.05 and L.contact_pressure(600, 2.10) > 150.0 > L.contact_pressure(600, 2.15)))
    checks.append(("hand calculation: contact pressure = P / B^2 + 24 t = 600/4 + 14.4 = 164.4 kPa for B = 2 m",
                   abs(L.contact_pressure(600, 2.0) - 164.4) < 1e-9))
    checks.append(("a thicker footing needs a wider base (t = 1.0 m gives a larger side than t = 0.4 m)",
                   L.required_side(600, 150, 1.0) > L.required_side(600, 150, 0.4)))
    checks.append(("weaker soil needs a wider footing (75 kPa gives more than 150 kPa)", L.required_side(600, 75) > L.required_side(600, 150)))
    try:
        L.required_side(100, 14.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("edge: allowable pressure below the footing weight is rejected", ok))
    checks.append(("Terzaghi phi = 0 strip: q_ult = 5.7 * 50 = 285 kPa", abs(L.q_ult_strip_phi0(50) - 285.0) < 1e-9))
    checks.append(("with D_f = 1 m and gamma = 18 kN/m^3 the capacity is 285 + 18 = 303 kPa", abs(L.q_ult_strip_phi0(50, 18.0, 1.0) - 303.0) < 1e-9))
    checks.append(("allowable pressure with FS = 3 is 95 kPa", abs(L.allowable_from_ultimate(285.0) - 95.0) < 1e-9))
    checks.append(("a 150 kPa pressure on a 285 kPa capacity gives FS = 1.9", abs(L.factor_of_safety(285.0, 150.0) - 1.9) < 1e-9))
    checks.append(("N_q = 1 at phi = 0", abs(L.terzaghi_nq(0.0) - 1.0) < 1e-9))
    checks.append(("the N_c formula tends to 5.7 as phi tends to 0 (5.71 at 0.0001 degrees)", abs(L.terzaghi_nc(1e-4) - 5.7) < 0.02 and L.terzaghi_nc(0) == 5.7))
    checks.append(("phi = 30 degrees: N_q = 22.5 and N_c = 37.2",
                   abs(L.terzaghi_nq(30) - 22.5) < 0.05 and abs(L.terzaghi_nc(30) - 37.2) < 0.05))
    qmax, qmin, full = L.edge_pressures(300, 2.0, 0.2)
    checks.append(("worked example: strip B = 2 m, 300 kN/m, e = 0.2 m gives 240 and 60 kPa", abs(qmax - 240) < 1e-9 and abs(qmin - 60) < 1e-9 and full))
    qmax, qmin, full = L.edge_pressures(300, 2.0, 2.0 / 6)
    checks.append(("edge: at e = B/6 the small edge pressure is exactly 0 and the large one is twice the mean (300 kPa)",
                   abs(qmin) < 1e-9 and abs(qmax - 300) < 1e-9 and full))
    qmax, qmin, full = L.edge_pressures(300, 2.0, 0.34)
    checks.append(("just beyond B/6 (e = 0.34 m) the base starts to lift off", not full and qmin == 0.0))
    ok = True
    for e in np.linspace(0, 2.0 / 6, 25):
        ok &= L.edge_pressures(300, 2.0, e)[1] >= -1e-9
    checks.append(("scan: no tension for 25 eccentricities from 0 to B/6", ok))
    qmax, qmin, full = L.edge_pressures(300, 2.0, 0.5)
    contact = 3 * (1.0 - 0.5)
    checks.append(("lift-off case e = 0.5 m: contact length 1.5 m, q_max = 400 kPa, triangle carries the 300 kN",
                   abs(qmax - 400) < 1e-9 and abs(0.5 * qmax * contact - 300) < 1e-9 and not full))
    checks.append(("lift-off case: triangle centroid sits 0.5 m from the centre = e (moment balance)", abs((1.0 - contact / 3) - 0.5) < 1e-12))
    checks.append(("design: strip load 200 kN/m on c = 50 kPa clay with FS 3 needs 2.105 m, built 2.15 m",
                   abs(200 / L.allowable_from_ultimate(L.q_ult_strip_phi0(50)) - 2.1053) < 1e-3))
    checks.append(("ignoring the footing weight the side would be exactly 2.0 m (600 / 150 = 4)", abs(math.sqrt(600 / 150) - 2.0) < 1e-12))
    checks.append(("assessment B: strip 200 kN/m on 2.15 m gives 93 kPa, below 95 kPa", abs(200 / 2.15 - 93.02) < 0.01 and 200 / 2.15 < 95.0))
    b75 = L.required_side(600, 75)
    checks.append(("assessment C: at 75 kPa the side is 3.15 m, 46% wider and more than double the area of 2.15 m",
                   abs(b75 - 3.15) < 1e-9 and abs(b75 / 2.15 - 1.465) < 0.001 and b75 ** 2 / 2.15 ** 2 > 2.0))
    def peak(b):
        return L.edge_pressures(600, b, 0.2, length_m=b)[0] + 24 * 0.6
    best = next(b for b in np.arange(2.15, 4.0, 0.05) if 0.2 <= b / 6 and peak(b) <= 150.0)
    checks.append(("assessment D: with e = 0.2 m, B = 2.55 m gives 150.1 kPa (fails), 2.60 m gives 144.1 kPa; the smallest side is 2.60 m",
                   abs(peak(2.55) - 150.1) < 0.05 and abs(peak(2.60) - 144.1) < 0.05 and abs(best - 2.6) < 1e-9))
    checks.append(("assessment D: e = 0.2 m is below B/6 = 0.43 m and the area is 6.76 m2 against 4.62 m2, 46% more",
                   abs(2.6 / 6 - 0.4333) < 1e-3 and abs(2.6 ** 2 - 6.76) < 1e-9 and abs(2.15 ** 2 - 4.6225) < 1e-9 and abs(2.6 ** 2 / 2.15 ** 2 - 1.462) < 0.001))
    checks.append(("at e = 0 the strip pressure is flat 150 kPa", L.edge_pressures(300, 2.0, 0.0)[:2] == (150.0, 150.0)))
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
