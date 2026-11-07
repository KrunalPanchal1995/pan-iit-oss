"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    rain = L.simulate_weather(365, seed=1)
    checks.append(("the weather is repeatable for a given seed", np.array_equal(rain, L.simulate_weather(365, seed=1))))
    checks.append(("the weather differs for a different seed", not np.array_equal(rain, L.simulate_weather(365, seed=2))))
    checks.append(("shop_income gives 100 on rain and 20 on dry for umbrellas",
                   np.allclose(L.shop_income(L.UMBRELLA, np.array([True, False])), [100.0, 20.0])))
    # hand calculation: all umbrella, p = 0.5: mean 60, swing 40
    m, s = L.exact_mean_std(1.0)
    checks.append(("hand calculation: all umbrella has average 60 and swing 40", abs(m - 60) < 1e-9 and abs(s - 40) < 1e-9))
    m, s = L.exact_mean_std(0.0)
    checks.append(("hand calculation: all ice cream has average 60 and swing 30", abs(m - 60) < 1e-9 and abs(s - 30) < 1e-9))
    m, s = L.exact_mean_std(0.5)
    checks.append(("worked example: half and half has average 60 and swing 5 (income 65 rain, 55 dry)",
                   abs(m - 60) < 1e-9 and abs(s - 5) < 1e-9
                   and np.allclose(L.split_income(np.array([True, False]), 0.5), [65.0, 55.0])))
    fz = L.zero_swing_split()
    checks.append(("the zero-swing split is 3/7 = 0.4286 and gives swing 0",
                   abs(fz - 3 / 7) < 1e-12 and L.exact_mean_std(fz)[1] < 1e-9))
    checks.append(("the average income is 60 for every split (the made-up numbers are chosen so)",
                   all(abs(L.exact_mean_std(f)[0] - 60) < 1e-9 for f in np.linspace(0, 1, 11))))
    # simulation agrees with the exact numbers
    sm, ss = L.sample_mean_std(0.5, n_days=20000, seed=3)
    checks.append(("20000 simulated days: half-and-half average within 0.5 of 60 and swing within 0.5 of 5",
                   abs(sm - 60) < 0.5 and abs(ss - 5) < 0.5))
    s1 = L.sample_mean_std(1.0)[1]
    s5 = L.sample_mean_std(0.5)[1]
    checks.append(("365 simulated days: splitting cuts the swing from about 40 to about 5 (all umbrella > 35, half < 7)",
                   s1 > 35 and s5 < 7))
    checks.append(("seed 1: 189 rainy days; sample averages 61.4 (umbrella), 58.9 (ice cream), 60.2 (half); swing 40.0 / 30.0 / 5.0",
                   int(rain.sum()) == 189
                   and abs(L.sample_mean_std(1.0)[0] - 61.42) < 0.01 and abs(L.sample_mean_std(0.0)[0] - 58.93) < 0.01
                   and abs(L.sample_mean_std(0.5)[0] - 60.18) < 0.01
                   and abs(L.sample_mean_std(1.0)[1] - 39.97) < 0.01 and abs(L.sample_mean_std(0.0)[1] - 29.98) < 0.01
                   and abs(L.sample_mean_std(0.5)[1] - 5.00) < 0.01))
    r25 = L.split_income(np.array([True, False]), 0.25)
    checks.append(("25% umbrella: income 47.5 on rain and 72.5 on dry, average 60 and swing 12.5",
                   np.allclose(r25, [47.5, 72.5]) and abs(L.exact_mean_std(0.25)[0] - 60) < 1e-9 and abs(L.exact_mean_std(0.25)[1] - 12.5) < 1e-9))
    checks.append(("design: swing is at most 10 exactly for splits between 2/7 = 28.6% and 4/7 = 57.1%",
                   abs(L.exact_mean_std(2 / 7)[1] - 10) < 1e-9 and abs(L.exact_mean_std(4 / 7)[1] - 10) < 1e-9
                   and L.exact_mean_std(0.25)[1] > 10 and L.exact_mean_std(0.6)[1] > 10 and L.exact_mean_std(0.5)[1] < 10))
    # edge: swing is 0 when it always rains
    checks.append(("edge: if it always rains the swing is 0", L.exact_mean_std(1.0, p_rain=1.0)[1] == 0.0))
    ok = all(L.exact_mean_std(f)[1] < 30 for f in np.linspace(0.15, 0.7, 12))
    checks.append(("every split from 15% to 70% umbrella is steadier than either shop alone (swing < 30)", ok))
    # swing of the formula |70 f - 30| used in the app, at p = 0.5
    checks.append(("swing equals |70 f - 30| at rain chance 0.5",
                   all(abs(L.exact_mean_std(f)[1] - abs(70 * f - 30)) < 1e-9 for f in np.linspace(0, 1, 11))))
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
