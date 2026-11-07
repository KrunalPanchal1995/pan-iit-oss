"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    s = L.immediate_settlement(150, 2.0, 20000)
    checks.append(("worked example: elastic settlement 150 * 2 * 0.91 * 0.82 / 20000 = 11.2 mm", abs(s - 150 * 2 * 0.91 * 0.82 / 20000) < 1e-12 and abs(s * 1000 - 11.19) < 0.01))
    centre, avg = L.flexible_square_factors()
    checks.append(("flexible square: centre factor 1.122 and average factor 0.95", abs(centre - 1.122) < 0.002 and abs(avg - 0.95) < 0.01))
    checks.append(("chosen I = 0.82 lies between the rigid circle pi/4 = 0.785 and the flexible square average 0.95", math.pi / 4 < L.I_RIGID_SQUARE < avg))
    checks.append(("settlement is proportional to the width at equal pressure", abs(L.immediate_settlement(100, 4, 20000) / L.immediate_settlement(100, 2, 20000) - 2.0) < 1e-12))
    sc = L.consolidation_settlement(4.0, 0.3, 0.9, 100.0, 50.0)
    checks.append(("worked example: consolidation settlement 4 * 0.3 / 1.9 * log10(1.5) = 111.2 mm",
                   abs(sc - 4 * 0.3 / 1.9 * math.log10(1.5)) < 1e-12 and abs(sc * 1000 - 111.2) < 0.05))
    checks.append(("no added stress gives no settlement", abs(L.consolidation_settlement(4.0, 0.3, 0.9, 100.0, 0.0)) < 1e-12))
    checks.append(("U = 50% at T_v = 0.197", abs(L.time_factor_for(0.5) - 0.197) < 0.001))
    checks.append(("U = 90% at T_v = 0.848", abs(L.time_factor_for(0.9) - 0.848) < 0.001))
    checks.append(("U(0) is 0 and U(10) is 1 (limits of the series)", abs(L.degree_of_consolidation(0.0)) < 1e-3 and abs(L.degree_of_consolidation(10.0) - 1.0) < 1e-9))
    tvs = np.linspace(0.0, 2.0, 50)
    us = [L.degree_of_consolidation(t) for t in tvs]
    checks.append(("U never decreases as T_v grows", all(b >= a - 1e-12 for a, b in zip(us, us[1:]))))
    checks.append(("early-time check: U = sqrt(4 T_v / pi) at T_v = 0.197 gives 0.50", abs(math.sqrt(4 * 0.197 / math.pi) - 0.5) < 0.01))
    t50, t90 = L.time_for_degree(0.5, 1.5, 2.0), L.time_for_degree(0.9, 1.5, 2.0)
    checks.append(("worked example: c_v 1.5 m2/yr, H_dr 2 m gives t50 = 0.52 years and t90 = 2.26 years", abs(t50 - 0.5249) < 0.005 and abs(t90 - 2.2615) < 0.005))
    checks.append(("doubling the drainage path makes consolidation 4 times slower", abs(L.time_for_degree(0.9, 1.5, 4.0) / t90 - 4.0) < 1e-9))
    checks.append(("hand calculation: 3 * 600 / (2 pi * 9) = 31.8 kPa on the axis of a point load at 3 m",
                   abs(L.boussinesq_axis(600, 3.0) - 31.83) < 0.01 and abs(L.boussinesq_axis(600, 3.0) - L.boussinesq_point(600, 0.0, 0.0, 3.0)) < 1e-9))
    checks.append(("2:1 spread: 600 / (2 + 3)^2 = 24.0 kPa at 3 m depth", abs(L.stress_2to1(600, 2, 3) - 24.0) < 1e-12))
    num = L.stress_square_centre(150, 2, 3)
    checks.append(("Boussinesq sum over the 2 m square at 3 m depth is 26.8 kPa, so 2:1 is about 11% low", abs(num - 26.84) < 0.05 and 0.08 < (num - 24.0) / num < 0.14))
    checks.append(("close to the footing the stress is the footing pressure (z = 0.05 m gives about 150 kPa)", abs(L.stress_square_centre(150, 2, 0.05, n=120) - 150) < 3.0))
    checks.append(("far below the footing the stress tends to the point-load value (z = 50 m within 1%)", abs(L.stress_square_centre(150, 2, 50.0) / L.boussinesq_axis(600, 50.0) - 1) < 0.01))
    a, b = L.stress_circle_numeric(100, 1.0, 1.0), L.stress_circle_closed(100, 1.0, 1.0)
    checks.append(("validation: circle numeric sum 64.64 kPa equals the closed form 64.64 kPa at depth = radius", abs(a - b) < 1e-3 and abs(b - 64.645) < 0.01))
    q, qult, fs, ok = L.strip_bearing_check(150, 1.5, 50)
    checks.append(("failure case: 150 kN/m on 1.5 m of c = 50 kPa clay gives 114.4 kPa, FS 2.49, below the required 3",
                   abs(q - 114.4) < 0.01 and abs(fs - 2.49) < 0.01 and not ok))
    checks.append(("collapse load is 405.9 kN/m and there the factor of safety is 1", abs(L.collapse_line_load(1.5, 50) - 405.9) < 0.05 and abs(L.strip_bearing_check(L.collapse_line_load(1.5, 50), 1.5, 50)[2] - 1.0) < 1e-9))
    loads = [250, 450, 800, 1200]
    std = [L.bearing_side(p, 150) for p in loads]
    ss = L.settlements(loads, std, 20000)
    checks.append(("standard layout: sides 1.40, 1.85, 2.45, 3.00 m, differential settlement 8.26 mm, plan area 20.4 m2",
                   np.allclose(std, [1.4, 1.85, 2.45, 3.0]) and abs(L.differential(ss) * 1000 - 8.26) < 0.01 and abs(sum(b * b for b in std) - 20.385) < 0.01))
    checks.append(("the heaviest column settles the most when footings are sized for bearing only", int(np.argmax(ss)) == 3))
    best = None
    for k in range(12, 41):
        sides = L.design_for_target(loads, 150, k * 0.5e-3, 20000)
        sv = L.settlements(loads, sides, 20000)
        area = sum(b * b for b in sides)
        if L.differential(sv) <= 0.004 and (best is None or area < best[0]):
            best = (area, k * 0.5, sides, L.differential(sv))
    checks.append(("mini-project: smallest area with differential <= 4 mm is target 10.5 mm, sides 1.40, 1.85, 2.85, 4.30 m, 32.0 m2, 3.81 mm",
                   best is not None and abs(best[1] - 10.5) < 1e-9 and np.allclose(best[2], [1.4, 1.85, 2.85, 4.3]) and abs(best[0] - 32.0) < 0.05 and abs(best[3] * 1000 - 3.81) < 0.01))
    checks.append(("every mini-project footing still meets bearing (pressure with self-weight <= 150 kPa)",
                   all(p / b ** 2 + 24 * 0.6 <= 150 + 1e-9 for p, b in zip(loads, best[2]))))
    checks.append(("worked example: total settlement 11.2 + 111.2 = 122.4 mm", abs((s + sc) * 1000 - 122.4) < 0.05))
    d0, sg0, sf0, t90a = L.clay_layer_response(600, 2.0, 2.0, 1.5)
    checks.append(("app default case: added stress 16.7 kPa on 45 kPa, final settlement 86.4 mm, t90 2.26 years",
                   abs(d0 - 16.667) < 0.01 and abs(sg0 - 45.0) < 1e-9 and abs(sf0 * 1000 - 86.42) < 0.01 and abs(t90a - 2.26) < 0.01))
    d1, sg1, sf1, t901 = L.clay_layer_response(600, 4.0, 1.5, 3.0)
    checks.append(("app challenge: 600 kN, B 4 m, H_dr 1.5 m, c_v 3 gives 48.1 mm and 0.64 years (meets 60 mm and 1 year)",
                   abs(sf1 * 1000 - 48.09) < 0.02 and abs(t901 - 0.636) < 0.005 and sf1 <= 0.06 and t901 <= 1.0))
    checks.append(("shipped one-shot consolidation at 2 years for the default layer is 75.4 mm",
                   abs(sf0 * L.degree_of_consolidation(1.5 * 2.0 / 4.0) * 1000 - 75.4) < 0.1))
    checks.append(("standard layout settlements are 6.7, 9.1, 12.2 and 14.9 mm", np.allclose(np.array(ss) * 1000, [6.66, 9.1, 12.2, 14.9], atol=0.06)))
    ds = L.settlements([250, 1200], [1.4, 4.45], 20000)
    ds4 = L.settlements([250, 1200], [1.4, 4.4], 20000)
    checks.append(("assessment D: B = 4.40 m gives a 3.51 mm difference (too much), 4.45 m gives 3.4 mm, 4.406 m is the exact limit and the area grows from 9.0 to 19.8 m2",
                   abs(L.differential(ds4) * 1000 - 3.51) < 0.01 and L.differential(ds4) > 0.0035 and abs(L.differential(ds) * 1000 - 3.40) < 0.01
                   and abs(1200 * 0.91 * 0.82 / 20000 / (0.0035 + 250 * 0.91 * 0.82 / 20000 / 1.4) - 4.4056) < 0.001 and abs(4.45 ** 2 - 19.80) < 0.01))
    checks.append(("a 4 m thick layer settles 4/3 as much as a 3 m layer (assessment B: 83.4 mm)", abs(L.consolidation_settlement(3.0, 0.3, 0.9, 100.0, 50.0) * 1000 - 83.4) < 0.05))
    checks.append(("half the consolidation settlement comes in about 6 months for the worked layer (0.52 years)", abs(t50 * 12 - 6.3) < 0.1))
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
