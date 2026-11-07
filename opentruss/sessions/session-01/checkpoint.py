"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("a 4 x 3 rectangle at 90 degrees has a 5.0 m diagonal",
                   abs(L.diagonal_length(4.0, 3.0, 90.0) - 5.0) < 1e-9))
    checks.append(("leaning the rectangle to 60 degrees shortens the diagonal to 3.606 m",
                   abs(L.diagonal_length(4.0, 3.0, 60.0) - 3.606) < 1e-3))
    checks.append(("a fixed 5 m diagonal allows only the 90 degree corner",
                   abs(L.corner_angle_for_diagonal(4.0, 3.0, 5.0) - 90.0) < 1e-6))
    checks.append(("a triangle needs 3 bars and a rectangle needs 5",
                   L.bars_needed(3) == 3 and L.bars_needed(4) == 5))
    checks.append(("a four-bar rectangle is not rigid, a triangle is",
                   (not L.is_rigid_by_count(4, 4)) and L.is_rigid_by_count(3, 3)))
    ft, fb = L.triangle_truss_forces(10.0, 6.0, 3.0)
    checks.append(("worked example: 10 kN, span 6 m, height 3 m gives -7.07 kN (top) and +5.00 kN (bottom)",
                   abs(ft + 7.07) < 0.005 and abs(fb - 5.00) < 0.005))
    ft2, fb2 = L.triangle_truss_forces(10.0, 6.0, 2.0)
    checks.append(("height 2 m gives -9.01 kN and +7.50 kN (a flatter truss pulls and pushes harder)",
                   abs(ft2 + 9.01) < 0.005 and abs(fb2 - 7.50) < 0.005))
    # hand calculation: equilibrium of the apex pin, sum Fy = 0 -> -2 F_top sin(theta) = P ... F_top is negative
    th = L.slope_angle(6.0, 3.0)
    checks.append(("apex pin: sum of vertical forces is zero (2 |F| sin(theta) = P)",
                   abs(2 * abs(ft) * np.sin(th) - 10.0) < 1e-9))
    # right foot pin: horizontal parts balance (bottom bar pulls inwards, sloping bar pushes outwards)
    checks.append(("foot pin: sum of horizontal forces is zero (|F_top| cos(theta) = F_bottom)",
                   abs(abs(ft) * np.cos(th) - fb) < 1e-9))
    checks.append(("force is proportional to load (doubling the load doubles both forces)",
                   np.allclose(L.triangle_truss_forces(20.0, 6.0, 3.0), [2 * ft, 2 * fb])))
    f12 = L.triangle_truss_forces(12.0, 6.0, 1.5)
    checks.append(("12 kN, height 1.5 m: top bars -13.42 kN and bottom bar +12.00 kN",
                   abs(f12[0] + 13.416) < 0.001 and abs(f12[1] - 12.0) < 1e-9))
    f375 = L.triangle_truss_forces(10.0, 6.0, 3.75)
    checks.append(("design: height 3.75 m keeps the bottom tension at 4.00 kN (top bars -6.40 kN)",
                   abs(f375[1] - 4.0) < 1e-9 and abs(f375[0] + 6.403) < 0.001))
    checks.append(("height 3 m means a 45 degree slope, height 2 m means 33.7 degrees",
                   abs(np.degrees(L.slope_angle(6.0, 3.0)) - 45.0) < 1e-9 and abs(np.degrees(L.slope_angle(6.0, 2.0)) - 33.69) < 0.005
                   and abs(np.degrees(L.slope_angle(6.0, 3.75)) - 51.34) < 0.005))
    checks.append(("12 kN, height 1.5 m: the vertical part of a sloping bar's force is 6.0 kN, half the load",
                   abs(abs(f12[0]) * np.sin(L.slope_angle(6.0, 1.5)) - 6.0) < 1e-9))
    f05 = L.triangle_truss_forces(10.0, 6.0, 0.5)
    checks.append(("height 0.5 m gives 30.41 kN compression and 30.00 kN tension; height 4 m gives 6.25 and 3.75 kN",
                   abs(f05[0] + 30.414) < 0.001 and abs(f05[1] - 30.0) < 1e-9
                   and np.allclose(L.triangle_truss_forces(10.0, 6.0, 4.0), [-6.25, 3.75], atol=1e-9)))
    checks.append(("colours: tension blue, compression red",
                   L.force_colour(5.0) == "tab:blue" and L.force_colour(-5.0) == "tab:red"))
    # limit: a very flat truss gives enormous forces
    f_flat = L.triangle_truss_forces(10.0, 6.0, 0.01)
    checks.append(("limit: an almost flat truss (h = 0.01 m) has forces over 1000 kN", abs(f_flat[0]) > 1000))
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
