"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    x, y = L.equirect(0.0, 0.0)
    checks.append(("the point (0, 0) maps to the map origin", abs(x) < 1e-9 and abs(y) < 1e-9))
    x, y = L.equirect(90.0, 180.0)
    checks.append(("lat 90 lon 180 maps to (pi R, pi R / 2)",
                   abs(x - np.pi * L.R_EARTH) < 1e-6 and abs(y - np.pi * L.R_EARTH / 2) < 1e-6))
    checks.append(("the equator is drawn at true length (stretch 1)", abs(L.ew_stretch(0.0) - 1.0) < 1e-12))

    # worked example: the circle of latitude at 60 degrees north
    true60 = L.parallel_length_sphere(60.0)
    map60 = L.parallel_length_map(60.0)
    checks.append((f"worked example: 60 degrees N circle is {true60:.1f} km, the map draws {map60:.1f} km, stretch 2",
                   abs(true60 - 20015.1) < 0.2 and abs(map60 - 40030.2) < 0.2 and abs(map60 / true60 - 2.0) < 1e-9))

    # hand calculation: 1 degree of longitude at 0 and at 60 degrees
    one0 = L.patch_width_true(0.0, 1.0)
    one60 = L.patch_width_true(60.0, 1.0)
    checks.append(("1 degree of longitude is 111.19 km at the equator", abs(one0 - 111.19) < 0.01))
    checks.append(("1 degree of longitude is half of that at 60 degrees", abs(one60 - one0 / 2) < 1e-9))
    checks.append(("the map draws every degree of longitude the same length", abs(L.patch_width_map(1.0) - one0) < 1e-9))

    # stretch grows toward the poles; symmetric in north and south
    lats = np.arange(0, 85, 5.0)
    s = np.array([L.ew_stretch(v) for v in lats])
    checks.append(("stretch never decreases toward the pole", bool(np.all(np.diff(s) > 0))))
    checks.append(("north and south are symmetric", abs(L.ew_stretch(-45.0) - L.ew_stretch(45.0)) < 1e-12))
    checks.append(("area stretch equals east-west stretch", abs(L.area_stretch(50.0) - L.ew_stretch(50.0)) < 1e-12))

    # edge cases: a pole and bad rounding
    checks.append(("at the pole the stretch is infinite (a point drawn as a line)", L.ew_stretch(90.0) == float("inf")))
    checks.append(("gap fraction is 0 at the equator and 0.5 at 60 degrees",
                   abs(L.gap_fraction(0.0)) < 1e-12 and abs(L.gap_fraction(60.0) - 0.5) < 1e-12))
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
