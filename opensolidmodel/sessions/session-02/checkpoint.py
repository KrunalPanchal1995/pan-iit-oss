"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    pr = L.section_properties([(1, "poly", L.l_section(60, 40, 10))])
    checks.append((f"worked example: area 900 mm2 (got {pr['area']:.1f})", abs(pr["area"] - 900.0) < 1e-9))
    checks.append((f"worked example: centroid (21.67, 11.67) mm (got {pr['cx']:.2f}, {pr['cy']:.2f})", abs(pr["cx"] - 21.6667) < 1e-3 and abs(pr["cy"] - 11.6667) < 1e-3))
    checks.append((f"worked example: Ixx = 107 500 mm4 (got {pr['ixx']:.0f})", abs(pr["ixx"] - 107500.0) < 0.5))
    checks.append((f"worked example: Iyy = 307 500 mm4 (got {pr['iyy']:.0f})", abs(pr["iyy"] - 307500.0) < 0.5))
    e = L.extrude(pr, 300)
    checks.append((f"worked example: 300 mm long weighs 2.12 kg (got {e['mass_kg']:.2f})", abs(e["mass_kg"] - 2.1195) < 0.001))
    # validation 1: a second, independent method: two rectangles and the parallel-axis rule
    ok1 = True
    for b, h, t in ((60, 40, 10), (50, 50, 5), (80, 30, 4), (100, 100, 15)):
        a1, a2 = b * t, (h - t) * t
        y1, y2 = t / 2, t + (h - t) / 2
        cy = (a1 * y1 + a2 * y2) / (a1 + a2)
        ixx = b * t ** 3 / 12 + a1 * (y1 - cy) ** 2 + t * (h - t) ** 3 / 12 + a2 * (y2 - cy) ** 2
        q = L.section_properties([(1, "poly", L.l_section(b, h, t))])
        ok1 &= abs(q["ixx"] - ixx) < 1e-6 * ixx and abs(q["cy"] - cy) < 1e-9
    checks.append(("validation: Ixx and the centroid agree with two rectangles and the parallel-axis rule for four sections", ok1))
    plate = L.section_properties([(1, "poly", L.rectangle(100, 20)), (-1, "circle", (50, 10, 5))])
    by_hand = 100 * 20 ** 3 / 12 - 3.141592653589793 * 5 ** 4 / 4
    checks.append((f"validation: plate with a hole, Ixx = b h^3 / 12 - pi r^4 / 4 = {by_hand:.0f} (got {plate['ixx']:.0f})", abs(plate["ixx"] - by_hand) < 1e-6 * by_hand))
    checks.append((f"validation: the hole removes pi r^2 = 78.5 mm2 (got {2000 - plate['area']:.1f})", abs(2000 - plate["area"] - 78.5398) < 1e-3))
    pts = L.l_section(60, 40, 10)
    rev = L.section_properties([(1, "poly", pts[::-1])])
    checks.append(("the corner order (clockwise or counter-clockwise) does not matter", abs(rev["ixx"] - pr["ixx"]) < 1e-6 and abs(rev["area"] - 900) < 1e-9))
    shifted = L.section_properties([(1, "poly", [(x + 100, y + 200) for x, y in pts])])
    checks.append(("moving the sketch by (100, 200) moves the centroid by the same amount and leaves Ixx, Iyy and the area alone",
                   abs(shifted["cx"] - pr["cx"] - 100) < 1e-6 and abs(shifted["cy"] - pr["cy"] - 200) < 1e-6 and abs(shifted["ixx"] - pr["ixx"]) < 1e-3 and abs(shifted["iyy"] - pr["iyy"]) < 1e-3))
    sw = L.section_properties([(1, "poly", L.l_section(40, 60, 10))])
    checks.append(("swapping the two legs swaps Ixx and Iyy", abs(sw["ixx"] - pr["iyy"]) < 1e-6 and abs(sw["iyy"] - pr["ixx"]) < 1e-6))
    p505 = L.section_properties([(1, "poly", L.l_section(50, 50, 5))])
    s = L.bending_stress(100000.0, 50 - p505["cy"], p505["ixx"])
    checks.append((f"worked example: 100 N m on the 50 x 50 x 5 L gives 31.7 MPa at the far edge (got {s:.1f})", abs(s - 31.7) < 0.05))
    checks.append(("a thicker section is stiffer and heavier",
                   L.section_properties([(1, "poly", L.l_section(50, 50, 8))])["ixx"] > p505["ixx"] > L.section_properties([(1, "poly", L.l_section(50, 50, 3))])["ixx"]))
    sq = lambda t: L.section_properties([(1, "poly", L.l_section(50, 50, t))])     # noqa: E731
    checks.append(("design: t = 7.1 mm reaches Ixx = 150 000 mm4 and t = 7.0 mm does not", sq(7.1)["ixx"] >= 150000 > sq(7.0)["ixx"]))
    for bad, label in ((lambda: L.l_section(50, 50, 60), "a thickness larger than the legs"),
                       (lambda: L.section_properties([(1, "poly", L.rectangle(10, 10)), (-1, "circle", (5, 5, 20))]), "a hole larger than the plate"),
                       (lambda: L.section_properties([(2, "poly", L.rectangle(10, 10))]), "a sign other than +1 or -1"),
                       (lambda: L.polygon_moments([(0, 0), (1, 1)]), "a polygon with two points"),
                       (lambda: L.circle_moments(0, 0, -1), "a negative radius")):
        try:
            bad()
            raised = False
        except ValueError:
            raised = True
        checks.append((f"edge case: {label} gives an error", raised))
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
