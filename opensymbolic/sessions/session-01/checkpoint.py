"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("a ball dropped for 2 s on Earth falls 19.62 m (worked example, noise-free)",
                   abs(float(L.fall_distance(2.0)) - 19.62) < 1e-9))
    d = L.fall_data()
    c, mse = L.fit_c(L.T_OBS ** 2, d)
    checks.append(("worked example: fitted c = 4.907 and mean squared error 0.205 m^2 for d = c t^2",
                   round(c, 3) == 4.907 and round(mse, 3) == 0.205))
    checks.append(("worked example: g = 2c is 9.81 m/s^2 to 3 significant figures",
                   round(L.gravity_from_c(c), 2) == 9.81))
    checks.append(("worked example: the six measured distances are 1.251, 4.758, 11.147, 19.228, 31.576, 43.704 m",
                   np.allclose(d, [1.251, 4.758, 11.147, 19.228, 31.576, 43.704], atol=5e-4)))
    checks.append(("worked example: sum(f d) = 697.742 and sum(f f) = 142.1875, so c = 4.907",
                   abs(float(np.sum(L.T_OBS ** 2 * d)) - 697.742) < 5e-4 and abs(float(np.sum(L.T_OBS ** 4)) - 142.1875) < 1e-9))
    cm, _ = L.fit_c(L.T_OBS ** 2, L.fall_data(1.62))
    checks.append(("on the Moon (g = 1.62) the same measurement errors give an estimated g of 1.62",
                   round(L.gravity_from_c(cm), 2) == 1.62))
    checks.append(("errors at n = 1.9 and 2.1 are 0.37 and 0.48 m^2",
                   round(L.fit_c(L.T_OBS ** 1.9, d)[1], 2) == 0.37 and round(L.fit_c(L.T_OBS ** 2.1, d)[1], 2) == 0.48))
    c_hand, mse_hand = L.fit_c(np.array([1.0, 2.0]), np.array([3.0, 5.0]))
    checks.append(("hand calculation: shape (1, 2), data (3, 5) gives c = 13/5 = 2.6 and MSE 0.1",
                   abs(c_hand - 2.6) < 1e-12 and abs(mse_hand - 0.1) < 1e-12))
    rows = L.search_library(L.T_OBS, d)
    checks.append(("the library search ranks c * t^2 first, and the runner-up has 20 times more error",
                   rows[0][0] == "c * t^2" and rows[1][2] > 20 * rows[0][2]))
    n, c2, m2, curve, exps = L.best_exponent(L.T_OBS, d)
    checks.append(("the exponent search finds n = 2.0", abs(n - 2.0) < 1e-9))
    checks.append(("errors at n = 1, 1.5, 2, 2.5, 3 are 34.39, 6.71, 0.20, 5.00, 15.73 m^2",
                   [round(L.fit_c(L.T_OBS ** k, d)[1], 2) for k in (1.0, 1.5, 2.0, 2.5, 3.0)] == [34.39, 6.71, 0.20, 5.00, 15.73]))
    checks.append(("with no noise the t^2 formula fits exactly (MSE below 1e-20)",
                   L.fit_c(L.T_OBS ** 2, L.fall_distance(L.T_OBS))[1] < 1e-20))
    checks.append(("edge: at t = 0 the ball has not fallen, and on the Moon (g = 1.62) 2 s gives 3.24 m",
                   float(L.fall_distance(0.0)) == 0.0 and abs(float(L.fall_distance(2.0, 1.62)) - 3.24) < 1e-9))
    checks.append(("the measured data differ from the law by at most 3 percent",
                   float(np.max(np.abs(d / L.fall_distance(L.T_OBS) - 1))) <= 0.03 + 1e-12))
    cooling_t, excess = L.cooling_data()
    cooling_c, cooling_mse = L.fit_c(L.LIBRARY["c * exp(-t)"](cooling_t), excess)
    checks.append(("cooling tea: synthetic temperature excess fits c * exp(-t) with c = 60 °C and zero error",
                   abs(cooling_c - 60.0) < 1e-12 and cooling_mse < 1e-20))
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
