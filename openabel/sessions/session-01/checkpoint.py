"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: chord at y = 1.8 cm in a ball of radius 3 cm is 4.8 cm",
                   abs(float(L.chord_length(1.8, 3.0)) - 4.8) < 1e-9))
    checks.append(("worked example: brightness there is 9.6 a.u. when eps0 = 2 a.u. per cm",
                   abs(float(L.ball_profile(1.8, 3.0, 2.0)) - 9.6) < 1e-9))
    checks.append(("centre of a solid ball: I(0) = 2 R eps0", abs(float(L.ball_profile(0.0, 3.0, 1.5)) - 9.0) < 1e-9))
    checks.append(("edge of the ball: chord is 0 at y = R and beyond", L.chord_length(3.0, 3.0) == 0 and L.chord_length(3.5, 3.0) == 0))
    checks.append(("profile is symmetric: I(-y) = I(y)", abs(float(L.ball_profile(-1.3, 3.0)) - float(L.ball_profile(1.3, 3.0))) < 1e-12))
    brute = L.ray_sum(L.uniform_ball(3.0), 1.8)
    checks.append((f"brute-force ray sum agrees with the formula (got {brute:.3f}, formula 4.800)", abs(brute - 4.8) < 0.01))
    brute2 = L.ray_sum(L.uniform_ball(3.0, 1.0, 2.0), 1.0)
    formula2 = float(L.ball_profile(1.0, 3.0, 1.0, 2.0))
    checks.append(("hollow shell: ray sum agrees with the formula at y = 1 cm", abs(brute2 - formula2) < 0.01))
    # limb brightening: the shell is brightest at y = r_in (hand calculation 2 sqrt(R^2 - r_in^2) = 2 sqrt(5))
    y = np.linspace(0, 3, 3001)
    prof = L.ball_profile(y, 3.0, 1.0, 2.0)
    checks.append(("a shell is brightest at its inner radius, 2 sqrt(5) = 4.472",
                   abs(y[np.argmax(prof)] - 2.0) < 0.01 and abs(prof.max() - 2 * np.sqrt(5)) < 1e-3))
    checks.append(("a shell is darker at the centre than at its brightest point", float(L.ball_profile(0.0, 3.0, 1.0, 2.0)) < prof.max()))
    xs, img = L.photo(3.0)
    checks.append(("the photo is round: pixel on the x axis equals pixel on the y axis at the same distance",
                   abs(img[80, 120] - img[120, 80]) < 1e-9))
    # second shape: the glowing cylinder (issue: second shape in the Session 1 app)
    cyl = L.uniform_cylinder(3.0, 5.0)
    checks.append(("cylinder: flat along the axis, I = 2 R eps0 = 6 for |y| <= length / 2",
                   all(abs(float(L.cylinder_profile(v, 3.0, 5.0)) - 6.0) < 1e-12 for v in (0.0, 1.0, 2.4))))
    checks.append(("cylinder: dark beyond its ends, I = 0 at y = 2.6 cm", float(L.cylinder_profile(2.6, 3.0, 5.0)) == 0.0))
    checks.append(("cylinder: ray sums agree with the formula at the centre line (y = 0, 1, 2, x = 0)",
                   all(abs(L.ray_sum_3d(cyl, 0.0, v) - float(L.cylinder_profile(v, 3.0, 5.0))) < 0.01 for v in (0.0, 1.0, 2.0))))
    checks.append(("cylinder: ray sum is 0 outside the length (y = 3 cm)", abs(L.ray_sum_3d(cyl, 0.0, 3.0)) < 1e-12))
    checks.append(("cylinder: across the axis it is round, ray sum at x = 1.8 cm is 4.8 like the ball",
                   abs(L.ray_sum_3d(cyl, 1.8, 0.0) - 4.8) < 0.01 and abs(float(L.cylinder_profile(0.0, 3.0, 5.0, x=1.8)) - 4.8) < 1e-9))
    hol = L.uniform_cylinder(3.0, 5.0, 1.0, 2.0)
    checks.append(("hollow cylinder: centre-line brightness is 2 (R - r_in) = 2, formula and ray sum",
                   abs(float(L.cylinder_profile(1.0, 3.0, 5.0, 1.0, 2.0)) - 2.0) < 1e-12 and abs(L.ray_sum_3d(hol, 0.0, 1.0) - 2.0) < 0.01))
    checks.append(("the ball is not flat but the cylinder is: ball I(2.4) = 3.6 < cylinder 6.0",
                   abs(float(L.ball_profile(2.4, 3.0)) - 3.6) < 1e-9 and float(L.cylinder_profile(2.4, 3.0, 5.0)) > float(L.ball_profile(2.4, 3.0))))
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
