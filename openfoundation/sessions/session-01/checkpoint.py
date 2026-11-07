"""Checkpoint for Session 1. Prints PASS or FAIL."""
import math


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("hand calculation: 600 kN on 2 m x 2 m is 150 kPa", abs(L.footing_pressure(600, 2.0) - 150.0) < 1e-9))
    pp = L.person_pressures(700.0)
    heel, shoe, snow = list(pp.values())
    checks.append(("heel is 7000 kPa and snowshoes are 3.5 kPa", abs(heel - 7000.0) < 1e-6 and abs(snow - 3.5) < 1e-9))
    checks.append(("shoe pressure is about 23.3 kPa", abs(shoe - 23.333) < 0.01))
    checks.append(("worked example: 300 kN on 1.5 m square is 133.3 kPa, too much for soft clay at 75 kPa",
                   abs(L.footing_pressure(300, 1.5) - 133.333) < 0.01 and not L.is_safe(300, 1.5, 75.0)))
    checks.append(("worked example: smallest side for 300 kN at 75 kPa is exactly 2.0 m", abs(L.min_side(300, 75) - 2.0) < 1e-12))
    checks.append(("edge: exactly 2.0 m is safe at 75 kPa (boundary, no round-off failure)", L.is_safe(300, 2.0, 75.0)))
    checks.append(("edge: 1.95 m is not safe at 75 kPa", not L.is_safe(300, 1.95, 75.0)))
    checks.append(("doubling the side divides the pressure by 4", abs(L.footing_pressure(300, 1.0) / L.footing_pressure(300, 2.0) - 4.0) < 1e-12))
    checks.append(("round_up(1.732) is 1.75 and round_up(2.0) stays 2.0", abs(L.round_up(1.732) - 1.75) < 1e-9 and abs(L.round_up(2.0) - 2.0) < 1e-9))
    try:
        L.pressure(10, 0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("zero area is rejected", ok))
    checks.append(("typical ranges are ordered: soft clay below firm clay below dense sand",
                   L.SOIL_RANGES["soft clay"][1] <= L.SOIL_RANGES["firm clay"][0] and L.SOIL_RANGES["firm clay"][1] <= L.SOIL_RANGES["dense sand or gravel"][0]))
    checks.append(("assessment B: 450 kN on 1.5 m is 200 kPa, smallest side sqrt(3) = 1.732 m built 1.75 m, giving 147 kPa",
                   abs(L.footing_pressure(450, 1.5) - 200.0) < 1e-9 and abs(L.min_side(450, 150) - math.sqrt(3)) < 1e-12
                   and abs(L.round_up(L.min_side(450, 150)) - 1.75) < 1e-9 and abs(L.footing_pressure(450, 1.75) - 146.94) < 0.01))
    checks.append(("assessment C: 300 kN at 100 kPa needs 1.73 m; halving the width gives 4 times the pressure",
                   abs(L.min_side(300, 100) - 1.732) < 1e-3 and abs(L.footing_pressure(300, 0.5) / L.footing_pressure(300, 1.0) - 4.0) < 1e-12))
    checks.append(("assessment D: 300 kN needs 2.0 m (4.0 m2) on 75 kPa and 1.0 m (1.0 m2) on 300 kPa",
                   abs(L.min_side(300, 75) - 2.0) < 1e-12 and abs(L.min_side(300, 300) - 1.0) < 1e-12))
    checks.append(("app challenge: 600 kN on a 2.1 m footing is 136 kPa, safe on 150 kPa soil", L.is_safe(600, 2.1, 150.0) and abs(L.footing_pressure(600, 2.1) - 136.05) < 0.01))
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
