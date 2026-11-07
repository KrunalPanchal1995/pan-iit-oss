"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    k800 = float(L.arrhenius_k(800.0))
    checks.append(("worked example: k(800 K) = 1.0e13 * exp(-150000/(8.3145*800)) = 1608 per s", abs(k800 - 1608.0) < 1.0))
    checks.append(("worked example: the exponent Ea/(R T) at 800 K is 22.55", abs(150000.0 / (L.R_GAS * 800.0) - 22.55) < 0.01))
    checks.append(("at T -> very large the law tends to A", abs(float(L.arrhenius_k(1e9)) / 1.0e13 - 1.0) < 1e-3))
    checks.append(("speed-up from 600 K to 700 K is 73.4 times", abs(L.speedup(600, 700) - 73.4) < 0.05))
    checks.append(("speed-up from 300 K to 310 K is about 7.0 times", abs(L.speedup(300, 310) - 6.96) < 0.01))
    checks.append(("speed-up from 300 K to 300 K is exactly 1", L.speedup(300, 300) == 1.0))
    # exact data lie exactly on a line whose slope gives Ea back
    x, y = L.to_xy(L.T_DATA, L.arrhenius_k(L.T_DATA))
    s, b = L.fit_line(x, y)
    checks.append(("noise-free data: slope -18.04 and intercept ln A = 29.93", abs(s + 18.04) < 0.005 and abs(b - np.log(1e13)) < 1e-6))
    checks.append(("noise-free data: Ea from the slope is 150.0 kJ/mol", abs(L.ea_from_slope(s) - 150.0) < 1e-6))
    T, k = L.make_data()
    x, y = L.to_xy(T, k)
    s, b = L.fit_line(x, y)
    checks.append(("noisy data (seed 1): fitted slope -18.005 and intercept 29.898", abs(s + 18.005) < 0.001 and abs(b - 29.898) < 0.001))
    checks.append(("noisy data (seed 1): Ea = 149.7 kJ/mol, within 1 percent of 150", abs(L.ea_from_slope(s) - 149.7) < 0.05))
    p = np.polyfit(x, y, 1)
    checks.append(("the hand formulas agree with numpy.polyfit", np.allclose([s, b], p, atol=1e-9)))
    checks.append(("two points define the line exactly", np.allclose(L.fit_line([1.0, 2.0], [3.0, 5.0]), [2.0, 1.0])))
    checks.append(("measured k rises with T (data are increasing)", bool(np.all(np.diff(k) > 0))))
    checks.append(("speed-up from 700 K to 800 K is 25.1 times (smaller than 73.4 from 600 to 700 K)", abs(L.speedup(700, 800) - 25.07) < 0.01))
    checks.append(("Ea = 100 kJ/mol: speed-up 600 to 700 K is 17.5 times and the slope is -12.03", abs(L.speedup(600, 700, 100.0) - 17.52) < 0.01 and abs(-100.0 / L.R_GAS + 12.03) < 0.005))
    checks.append(("with A = 1e13 per s, k = 1000 per s needs 783.5 K for Ea = 150 and 522.3 K for Ea = 100",
                   abs(150e3 / (L.R_GAS * np.log(1e10)) - 783.5) < 0.05 and abs(100e3 / (L.R_GAS * np.log(1e10)) - 522.3) < 0.05))
    checks.append(("at 600 K the largest Ea that still gives k = 1000 per s is 114.9 kJ/mol", abs(L.R_GAS * 600.0 * np.log(1e10) / 1000.0 - 114.9) < 0.05))
    checks.append(("app challenge: Ea = 80 kJ/mol at 500 K gives k above 1000 per s", float(L.arrhenius_k(500.0, 1e13, 80.0)) > 1000.0))
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
