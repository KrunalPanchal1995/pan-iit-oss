"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # worked example: x = 3 t^2 + 2 t, v = 6 t + 2, a = 6; at t = 2: 16 m, 14 m/s
    checks.append(("worked example: x(2) = 16 m", abs(float(L.x_car(2.0)) - 16.0) < 1e-12))
    checks.append(("worked example: v(2) = 14 m/s by the polynomial rule", abs(float(L.poly_value(L.poly_derivative([0.0, 2.0, 3.0]), 2.0)) - 14.0) < 1e-12))
    checks.append(("worked example: a = 6 m/s^2 by differentiating twice", L.poly_derivative(L.poly_derivative([0.0, 2.0, 3.0])) == [6.0]))
    checks.append(("secant slope for h = 0.001 is within 0.01 of 14", abs(float(L.secant_slope(L.x_car, 2.0, 0.001)) - 14.0) < 0.01))
    checks.append(("secant slope for h = 1 is 17 (3 h + 14)", abs(float(L.secant_slope(L.x_car, 2.0, 1.0)) - 17.0) < 1e-9))
    checks.append(("velocity function matches a finite-difference slope of x(t)", abs(float(L.central_slope(L.x_car, 1.3)) - float(L.v_car(1.3))) < 1e-6))
    checks.append(("(sin t)' = cos t by finite differences", abs(L.central_slope(np.sin, 0.7) - np.cos(0.7)) < 1e-8))
    checks.append(("(e^t)' = e^t by finite differences", abs(L.central_slope(np.exp, 0.7) - np.exp(0.7)) < 1e-8))
    checks.append(("derivative of a constant is 0", L.poly_derivative([5.0]) == [0.0]))
    # integral
    checks.append(("left sum with n = 4 is 13 m (hand: 0.5 * (2 + 5 + 8 + 11))", abs(L.riemann_sum(L.v_car, 0, 2, 4) - 13.0) < 1e-9))
    checks.append(("midpoint sum is exact for a straight line (16 m)", abs(L.riemann_sum(L.v_car, 0, 2, 4, "mid") - 16.0) < 1e-9))
    checks.append(("more rectangles are closer to 16 m", abs(L.riemann_sum(L.v_car, 0, 2, 64) - 16) < abs(L.riemann_sum(L.v_car, 0, 2, 4) - 16)))
    checks.append(("fundamental theorem: integral of v = x(2) - x(0)", abs(L.riemann_sum(L.v_car, 0, 2, 4000, "mid") - float(L.x_car(2) - L.x_car(0))) < 1e-6))
    anti = L.poly_antiderivative([2.0, 6.0])
    checks.append(("antiderivative of 6 t + 2 is 3 t^2 + 2 t", anti == [0.0, 2.0, 3.0]))
    # braking
    checks.append(("stopping from 20 m/s at 5 m/s^2 takes 40 m", abs(L.stopping_distance(20, 5) - 40.0) < 1e-9))
    checks.append(("reaction time adds v * tr", abs(L.stopping_distance(20, 5, 1.0) - 60.0) < 1e-9))
    vmax = L.max_speed_for(40.0, 6.0, 0.75)
    checks.append((f"max speed for 40 m is about 17.87 m/s (got {vmax:.2f}) and stops in exactly 40 m", abs(vmax - 17.87) < 0.01 and abs(L.stopping_distance(vmax, 6.0, 0.75) - 40.0) < 1e-9))
    checks.append(("zero speed needs zero distance", L.stopping_distance(0.0, 5.0) == 0.0))
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
