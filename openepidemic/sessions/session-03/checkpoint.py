"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    R0 = L.TRUE_BETA / L.TRUE_GAMMA
    Y = L.solve_sir(L.TRUE_BETA, L.TRUE_GAMMA, days=100)

    # --- validation of the solver ---
    checks.append(("conservation: S + I + R = N to within 1e-6 people", L.conservation_error(Y) < 1e-6))
    z = L.final_size(R0)
    checks.append(("final size equation: z = 1 - exp(-R0 z) holds, z = 0.7968", abs(z - (1 - np.exp(-R0 * z))) < 1e-10 and abs(z - 0.7968) < 1e-4))
    checks.append(("RK4 final size matches the equation within 0.001 of N", abs(Y[-1, 2] / L.TOWN - z) < 1e-3))
    r_meas = L.growth_rate_measured(L.TRUE_BETA, L.TRUE_GAMMA)
    checks.append((f"early growth rate is about gamma (R0 - 1) = 0.2 per day (measured {r_meas:.3f})", abs(r_meas - 0.2) < 0.01))
    coarse = L.solve_sir(0.4, 0.2, days=100, h=1.0)[:, 1].max()
    fine = L.solve_sir(0.4, 0.2, days=100, h=0.125)[:, 1].max()
    mid = Y[:, 1].max()
    checks.append(("RK4 is converged: h = 0.25 and h = 0.125 peaks differ by under 0.001 people", abs(mid - fine) < 1e-3))
    checks.append(("RK4 even with h = 1 day is within 0.01 people (peak 1538.84)", abs(coarse - fine) < 0.01 and abs(fine - 1538.84) < 0.01))
    checks.append(("peak is on day 34 with 1538.8 people infected", int(Y[:, 1].argmax()) == 34 and abs(mid - 1538.8) < 0.1))

    # --- data and the worked example ---
    d = L.make_data(1000, 60)
    checks.append(("data are reproducible (same seed, same numbers)", np.array_equal(d, L.make_data(1000, 60))))
    checks.append(("worked example: first ten synthetic days are 5 6 10 6 7 11 22 23 20 33",
                   list(d[:10]) == [5, 6, 10, 6, 7, 11, 22, 23, 20, 33]))
    inc = L.daily_incidence(0.4, 0.2, days=60)
    checks.append(("total expected cases in 60 days is 7831 (model), data total 7844 (noise)",
                   abs(inc.sum() - 7831.0) < 0.5 and d.sum() == 7844))

    th, cov = L.gauss_newton(d, L.grid_fit(d))
    sd = np.sqrt(np.diag(cov))
    checks.append((f"fit on 60 days recovers beta = 0.401, gamma = 0.201 (got {th[0]:.3f}, {th[1]:.3f}; truth 0.4, 0.2)",
                   abs(th[0] - 0.4) < 0.01 and abs(th[1] - 0.2) < 0.01 and abs(th[0] - 0.4010) < 0.0015))
    checks.append(("60-day fit: standard errors about 0.0035 and 0.0038", abs(sd[0] - 0.0035) < 0.001 and abs(sd[1] - 0.0038) < 0.001))
    early = d[:14]
    th14, cov14 = L.gauss_newton(early, L.grid_fit(early))
    sd14 = np.sqrt(np.diag(cov14))
    corr14 = cov14[0, 1] / np.sqrt(cov14[0, 0] * cov14[1, 1])
    checks.append((f"fit on 14 days: beta {th14[0]:.2f}, gamma {th14[1]:.2f} with standard errors {sd14[0]:.2f}, {sd14[1]:.2f}",
                   abs(th14[0] - 0.48) < 0.01 and abs(th14[1] - 0.29) < 0.01 and sd14[0] > 0.08 and sd14[1] > 0.1))
    checks.append(("14-day fit: correlation of beta and gamma estimates is 0.999", abs(corr14 - 0.9993) < 0.001))

    # --- repeats: uncertainty and identifiability ---
    F14, F60 = L.repeat_fits(14, 100), L.repeat_fits(60, 100)
    checks.append((f"60 days, 100 repeats: mean beta, gamma = 0.399, 0.199, sd 0.006 each (got {F60.mean(axis=0).round(3)}, {F60.std(axis=0).round(3)})",
                   abs(F60[:, 0].mean() - 0.399) < 0.002 and abs(F60[:, 1].mean() - 0.199) < 0.002 and abs(F60[:, 0].std() - 0.006) < 0.002))
    checks.append(("14 days, 100 repeats: sd of beta is 0.080 and of gamma 0.097, about 13 times larger than with 60 days",
                   abs(F14[:, 0].std() - 0.080) < 0.005 and abs(F14[:, 1].std() - 0.097) < 0.005 and F14[:, 0].std() > 10 * F60[:, 0].std()))
    c14 = np.corrcoef(F14.T)[0, 1]
    checks.append((f"14 days: beta and gamma estimates are almost perfectly correlated (corr {c14:.3f})", c14 > 0.99))
    diff14 = (F14[:, 0] - F14[:, 1]).std()
    checks.append((f"but beta - gamma (the growth rate) is well determined: sd {diff14:.3f} against 0.080 for beta",
                   abs(diff14 - 0.018) < 0.004 and diff14 < F14[:, 0].std() / 3))
    checks.append(("the mean of beta - gamma over the 14-day fits is 0.198, close to the true 0.2", abs((F14[:, 0] - F14[:, 1]).mean() - 0.198) < 0.005))

    # --- failure case: reporting delay ---
    Fd = L.repeat_fits(60, 50, delay=5)
    checks.append((f"failure: ignoring a 5-day reporting delay biases beta to 0.308 and gamma to 0.128 (got {Fd[:, 0].mean():.3f}, {Fd[:, 1].mean():.3f})",
                   abs(Fd[:, 0].mean() - 0.308) < 0.005 and abs(Fd[:, 1].mean() - 0.128) < 0.005))

    # --- stochastic ---
    p2 = L.extinction_probability(0.4, 0.2)
    p3 = L.extinction_probability(0.6, 0.2)
    checks.append((f"R0 = 2: extinction probability is about 1/R0 = 0.5 (simulated {p2:.3f}, 2000 runs)", abs(p2 - 0.5) < 0.04 and abs(p2 - 0.4855) < 1e-9))
    checks.append((f"R0 = 3: extinction probability is about 1/3 (simulated {p3:.3f})", abs(p3 - 1 / 3) < 0.04 and abs(p3 - 0.319) < 1e-9))
    checks.append(("edge: R0 = 1.5 gives about 2/3 and a run starting with 0 cases is already over",
                   abs(L.extinction_probability(0.3, 0.2) - 0.663) < 1e-9 and len(L.gillespie(0.4, 0.2, 100, 0, np.random.default_rng(0))[0]) == 1))

    # --- vaccination ---
    p0, p23, p24 = (L.peak_with_vaccination(c) for c in (0.0, 0.23, 0.24))
    checks.append((f"town of 50000: peak is 7676 with no vaccination, 3125 at 23 percent, 2961 at 24 percent (got {p0:.0f}, {p23:.0f}, {p24:.0f})",
                   abs(p0 - 7675.7) < 0.5 and abs(p23 - 3125.2) < 0.5 and abs(p24 - 2961.2) < 0.5))
    checks.append(("worked example: smallest coverage keeping the peak under 3000 is 24 percent (efficacy 0.9)", L.min_coverage_for_peak(3000) == 0.24))
    checks.append(("with efficacy 0.6 the same line needs 36 percent coverage", L.min_coverage_for_peak(3000, efficacy=0.6) == 0.36))
    checks.append(("a line of 1000 people needs 39 percent", L.min_coverage_for_peak(1000) == 0.39))
    checks.append(("50 percent coverage (efficacy 0.9) cuts the peak to 126 people", abs(L.peak_with_vaccination(0.5) - 126.3) < 0.5))

    # --- sensitivity ---
    lo = L.solve_sir(0.36, 0.2, days=100)[:, 1].max()
    hi = L.solve_sir(0.44, 0.2, days=100)[:, 1].max()
    checks.append(("sensitivity: beta -10 percent gives peak 1184, +10 percent gives 1874 (peak changes by about 22 percent)",
                   abs(lo - 1184.3) < 0.5 and abs(hi - 1874.5) < 0.5))
    # assessment answers and numbers quoted in the text
    checks.append(("R_eff = 1.59 at 23 percent and 1.57 at 24 percent coverage (efficacy 0.9, R0 2)",
                   round(2 * (1 - 0.23 * 0.9), 2) == 1.59 and round(2 * (1 - 0.24 * 0.9), 2) == 1.57))
    checks.append(("fit on 60 days: gamma = 0.201", abs(th[1] - 0.2005) < 0.0005 + 1e-9))
    checks.append(("14-day fit: beta 0.477, gamma 0.288, standard errors 0.10 and 0.12, R0 1.66, beta - gamma 0.189",
                   round(th14[0], 3) == 0.477 and round(th14[1], 3) == 0.288 and round(sd14[0], 2) == 0.10 and round(sd14[1], 2) == 0.12
                   and round(0.477 / 0.288, 2) == 1.66 and round(0.477 - 0.288, 3) == 0.189))
    a = L.daily_incidence(0.4, 0.2, days=14)
    b = L.daily_incidence(0.48, 0.29, days=14)
    a60 = L.daily_incidence(0.4, 0.2, days=60)
    b60 = L.daily_incidence(0.48, 0.29, days=60)
    checks.append(("identifiability: (0.4, 0.2) and (0.48, 0.29) differ by 40 people^2 over 14 days (noise variance 296), but 55941 over 60",
                   round(float(((a - b) ** 2).sum())) == 40 and round(float(a.sum())) == 296 and round(float(((a60 - b60) ** 2).sum())) == 55941))
    checks.append(("design sensitivity: smallest coverage for the 3000 line is 17 percent at beta 0.36 and 31 percent at beta 0.44",
                   L.min_coverage_for_peak(3000, beta=0.36) == 0.17 and L.min_coverage_for_peak(3000, beta=0.44) == 0.31))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
