"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    o2, pa, pb, o4 = L.four_bar_joints(0.0)
    checks.append(("worked example: at crank angle 0 the pin B is at (1, 4), the 3-4-5 triangle",
                   np.allclose(pb, [1.0, 4.0], atol=1e-9) and np.allclose(pa, [1.0, 0.0], atol=1e-12)))
    lens = np.array([L.bar_lengths(L.four_bar_joints(t)) for t in np.linspace(0, 2 * np.pi, 49)])
    checks.append(("all four bar lengths stay (4, 1, 4, 5) for every crank angle",
                   np.allclose(lens, [4.0, 1.0, 4.0, 5.0], atol=1e-12)))
    fine = np.array([L.rocker_angle(t) for t in np.linspace(0, 2 * np.pi, 7201)])
    checks.append(("rocker swing from the extreme positions is 29.55 degrees",
                   abs(L.rocker_swing() - 29.552) < 0.001))
    checks.append(("the sampled rocker swing agrees with the formula to 0.001 degrees",
                   abs((fine.max() - fine.min()) - L.rocker_swing()) < 1e-3))
    checks.append(("the rocker stays between 113.58 and 143.13 degrees",
                   abs(fine.min() - 113.578) < 0.01 and abs(fine.max() - 143.130) < 0.01))
    checks.append(("the coupler midpoint at crank angle 0 is (1, 2)",
                   np.allclose(L.coupler_point(0.0, k=0.5), [1.0, 2.0], atol=1e-9)))
    curve = L.coupler_curve(k=0.5, n=361)
    checks.append(("the coupler curve closes after one crank turn", np.allclose(curve[0], curve[-1], atol=1e-9)))
    p, q = L.circle_intersections([0.0, 0.0], 1.0, [2.0, 0.0], 1.0)
    checks.append(("edge: circles that just touch give one point (1, 0) twice, no NaN",
                   np.allclose(p, [1.0, 0.0]) and np.allclose(q, [1.0, 0.0]) and np.all(np.isfinite(p))))
    try:
        L.circle_intersections([0.0, 0.0], 1.0, [5.0, 0.0], 1.0)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge: circles that do not meet raise ValueError", raised))
    checks.append(("freedom count: four bars and four pins give 1 freedom; a triangle of 3 bars and 3 pins is rigid (0); a five-bar loop has 2",
                   L.mobility(4, 4) == 1 and L.mobility(3, 3) == 0 and L.mobility(5, 5) == 2))
    checks.append(("rocker swing grows with the crank: 29.55, 44.72 and 60.49 degrees for b = 1, 1.5, 2",
                   all(abs(L.rocker_swing(b=b) - v) < 0.01 for b, v in ((1.0, 29.55), (1.5, 44.72), (2.0, 60.49)))))
    j = L.four_bar_joints(np.pi)
    checks.append(("F answers: at crank angle 180 the pin B is (0.6, 3.666) and the rocker angle 132.84; at 90 it is 115.06",
                   np.allclose(j[2], [0.6, 3.666], atol=1e-3) and abs(L.rocker_angle(np.pi) - 132.84) < 0.01
                   and abs(L.rocker_angle(np.pi / 2) - 115.06) < 0.01 and abs(L.rocker_angle(0.0) - 126.87) < 0.01))
    ts = np.linspace(0, 360, 7201)
    ra = np.array([L.rocker_angle(np.radians(t)) for t in ts])
    checks.append(("rocker extremes: 143.13 at crank 270 degrees and 113.58 at crank about 66.4 degrees",
                   abs(ts[ra.argmax()] - 270) < 0.1 and abs(ts[ra.argmin()] - 66.42) < 0.1))
    checks.append(("law of cosines: psi = 66.42 and 36.87 degrees at the extremes",
                   abs(np.degrees(np.arccos(0.4)) - 66.42) < 0.01 and abs(np.degrees(np.arccos(0.8)) - 36.87) < 0.01))
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
