"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    designs = L.fewest_teeth_designs(20)
    best = designs[0]
    stages = [best[1], best[2]]
    checks.append(("worked example: the smallest exact 1:20 design is 17-68 then 17-85 (187 teeth)",
                   best[0] == 187 and set(stages) == {(17, 68), (17, 85)}))
    checks.append(("worked example: its stage ratios are 4 and 5 and the overall ratio is exactly 20",
                   sorted([L.stage_ratio(*s) for s in stages]) == [4.0, 5.0] and abs(L.compound_ratio(stages) - 20.0) < 1e-12))
    checks.append(("worked example: 1200 rpm in gives 60 rpm out, same direction (two meshes)",
                   abs(L.output_speed(1200, stages) - 60.0) < 1e-9))
    checks.append(("worked example: 2 N m in gives 40 N m out for the ideal train",
                   abs(L.output_torque_ideal(2.0, stages) - 40.0) < 1e-9))
    sp = L.shaft_speeds(1200, stages)
    checks.append(("middle shaft turns at 300 rpm the other way (1200 / 4 with the 17-68 stage first)",
                   abs(sp[1] + 300.0) < 1e-9))
    checks.append(("a single stage for 1:20 with a 17-tooth pinion needs 340 teeth",
                   abs(L.stage_ratio(17, 340) - 20.0) < 1e-12))
    p_in = 2.0 * 1200
    p_out = L.output_torque_ideal(2.0, stages) * abs(L.output_speed(1200, stages))
    checks.append(("power T x w is unchanged by the ideal train", abs(p_in - p_out) < 1e-6))
    checks.append(("the number of exact two-stage designs with 17 to 100 teeth is 146", len(designs) == 146))
    coax = [d for d in designs if sum(d[1]) == sum(d[2])]
    checks.append(("only 4 of those 146 have equal centre distances (same module)", len(coax) == 4))
    checks.append(("centre distances at module 2 mm: 85 mm and 102 mm, which are not equal",
                   L.centre_distance(2, 17, 68) == 85.0 and L.centre_distance(2, 17, 85) == 102.0))
    checks.append(("pitch diameter d = m N: module 2 and 17 teeth gives 34 mm", L.pitch_diameter(2, 17) == 34))
    checks.append(("undercut limit 2 / sin^2(20 degrees) = 17.1", abs(L.min_teeth_no_undercut() - 17.097) < 1e-3))
    c = L.contact_ratio(20, 40)
    checks.append(("contact ratio of a 20:40 pair is 1.635 (above 1)", abs(c - 1.635) < 1e-3 and c > 1.0))
    checks.append(("contact ratio of a 17:17 pair is 1.515, smaller than for 100:100 (1.853)",
                   abs(L.contact_ratio(17, 17) - 1.515) < 1e-3 and L.contact_ratio(17, 17) < L.contact_ratio(100, 100)))
    checks.append(("middle shaft ideal torque is 8 N m (2 N m x 4)", abs(abs(L.output_torque_ideal(2.0, [stages[0]])) - 8.0) < 1e-9))
    s_b = [(20, 50), (18, 72)]
    checks.append(("hand calculation: 20-50 then 18-72 at 900 rpm and 3 N m gives 90 rpm and 30 N m, same direction",
                   abs(L.compound_ratio(s_b) - 10.0) < 1e-12 and abs(L.output_speed(900, s_b) - 90.0) < 1e-9
                   and abs(L.output_torque_ideal(3.0, s_b) - 30.0) < 1e-9))
    checks.append(("graph reading: with N1 = N3 = 20 and N2 = 60 the ratio 20 needs N4 = 133.3 (more than 100)",
                   abs(20 * 20 * 20 / 60 - 133.33) < 0.01))
    d12 = L.fewest_teeth_designs(12)
    checks.append(("design problem: the smallest exact 1:12 design is 17-51 then 17-68 (153 teeth)",
                   d12[0][0] == 153 and set(d12[0][1:]) == {(17, 51), (17, 68)}))
    checks.append(("module 2 mm: a 340-tooth gear is 680 mm across, an 85-tooth gear 170 mm",
                   L.pitch_diameter(2, 340) == 680 and L.pitch_diameter(2, 85) == 170))
    checks.append(("1:12 design at module 2 mm: centre distances 68 mm and 85 mm",
                   L.centre_distance(2, 17, 51) == 68.0 and L.centre_distance(2, 17, 68) == 85.0))
    checks.append(("direction: three stages (three meshes) turn the output the other way",
                   L.output_speed(100, [(20, 40)] * 3) < 0))
    checks.append(("edge case: equal teeth give ratio exactly 1", L.compound_ratio([(30, 30), (25, 25)]) == 1.0))
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
