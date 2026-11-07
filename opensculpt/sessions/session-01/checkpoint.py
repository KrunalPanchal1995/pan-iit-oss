"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c0 = (0.0, 0.0)
    checks.append(("circle: point (3, 4) is 3 units outside a circle of radius 2", abs(float(L.sd_circle((3, 4), c0, 2.0)) - 3.0) < 1e-12))
    checks.append(("circle: the centre has value -r (negative = inside)", abs(float(L.sd_circle(c0, c0, 2.0)) + 2.0) < 1e-12))
    checks.append(("circle: a point on the edge has value 0", abs(float(L.sd_circle((0, 2), c0, 2.0))) < 1e-12))
    checks.append(("box: (3, 0) is 2 units from a box of half-size 1", abs(float(L.sd_box((3, 0), c0, (1, 1))) - 2.0) < 1e-12))
    checks.append(("box: the centre of a box of half-size 1 has value -1", abs(float(L.sd_box(c0, c0, (1, 1))) + 1.0) < 1e-12))
    checks.append(("box: a corner point (2, 2) is sqrt(2) from the box", abs(float(L.sd_box((2, 2), c0, (1, 1))) - np.sqrt(2.0)) < 1e-12))

    # worked example: circle (0,0) r=1, box centre (2,0) half (0.5,0.5), point (1.2, 0.3)
    p = np.array([1.2, 0.3])
    dc = float(L.sd_circle(p, c0, 1.0))
    db = float(L.sd_box(p, (2.0, 0.0), (0.5, 0.5)))
    du = float(L.union(dc, db))
    checks.append((f"worked example: circle {dc:.3f}, box {db:.3f}, union = min = {du:.3f}",
                   abs(dc - (np.sqrt(1.53) - 1.0)) < 1e-12 and abs(db - 0.3) < 1e-12 and abs(du - 0.237) < 1e-3))

    # the union is inside where either shape is inside
    pts = np.array([[0.0, 0.0], [2.0, 0.0], [1.2, 1.2]])
    inside = L.union(L.sd_circle(pts, c0, 1.0), L.sd_box(pts, (2.0, 0.0), (0.5, 0.5))) < 0
    checks.append(("union: inside the circle, inside the box, outside both", list(inside) == [True, True, False]))

    # the profile along y = 0.3 (Section C) and the touching/overlapping design (Section F)
    xs = np.array([-0.96, -0.95, 0.95, 0.96, 1.49, 1.51, 2.49, 2.51])
    line = np.stack([xs, np.full_like(xs, 0.3)], axis=-1)
    prof = L.union(L.sd_circle(line, c0, 1.0), L.sd_box(line, (2.0, 0.0), (0.5, 0.5))) < 0
    checks.append(("profile along y = 0.3: inside for -0.954 < x < 0.954 and for 1.5 < x < 2.5",
                   list(prof) == [False, True, True, False, False, True, True, False]))
    checks.append(("design: a circle of radius 1.5 at the origin touches the box at (1.5, 0) (both values 0)",
                   abs(float(L.sd_circle((1.5, 0.0), c0, 1.5))) < 1e-12 and abs(float(L.sd_box((1.5, 0.0), (2.0, 0.0), (0.5, 0.5)))) < 1e-12))
    checks.append(("design: radius 1.6 overlaps the box, the point (1.5, 0) has value -0.1 in the circle",
                   abs(float(L.sd_circle((1.5, 0.0), c0, 1.6)) + 0.1) < 1e-12))
    # the app's challenge: a point at the circle centre is inside
    checks.append(("app challenge: the point (-0.6, 0) is inside a circle of radius 0.5 centred at (-0.6, 0)",
                   float(L.sd_circle((-0.6, 0.0), (-0.6, 0.0), 0.5)) < 0))

    # a signed distance changes by at most the step you take
    rng = np.random.default_rng(0)
    a = rng.uniform(-3, 3, (200, 2))
    e = rng.normal(size=(200, 2)) * 0.1
    d1 = L.sd_circle(a, c0, 1.0) - L.sd_circle(a + e, c0, 1.0)
    d2 = L.sd_box(a, c0, (1.0, 0.5)) - L.sd_box(a + e, c0, (1.0, 0.5))
    step = np.linalg.norm(e, axis=1)
    checks.append(("a step of length s changes the distance by at most s", bool(np.all(np.abs(d1) <= step + 1e-12) and np.all(np.abs(d2) <= step + 1e-12))))

    # counting grid cells approximates the area pi r^2
    frac = L.inside_fraction(lambda q: L.sd_circle(q, c0, 1.0), (-1.5, 1.5), (-1.5, 1.5), 300)
    checks.append((f"counting cells: circle area {frac * 9.0:.4f} is within 0.5% of pi", abs(frac * 9.0 - np.pi) / np.pi < 0.005))
    # edge: a grid with all cells outside gives 0
    checks.append(("edge case: a shape far outside the grid has fraction 0",
                   L.inside_fraction(lambda q: L.sd_circle(q, (10, 10), 1.0), (-1, 1), (-1, 1), 20) == 0.0))
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
