"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # standard error of the mean
    checks.append(("SEM formula: s = 0.2, n = 5 gives 0.0894", abs(L.sem(0.2, 5) - 0.0894) < 1e-4))
    sim5, sim20 = L.simulate_sem(0.2, 5), L.simulate_sem(0.2, 20)
    checks.append(("simulation agrees with s/sqrt(n) within 3 percent (n = 5 and n = 20)",
                   abs(sim5 / L.sem(0.2, 5) - 1) < 0.03 and abs(sim20 / L.sem(0.2, 20) - 1) < 0.03))
    checks.append(("quadrupling n halves the standard error", abs(L.sem(0.2, 20) / L.sem(0.2, 5) - 0.5) < 1e-12))
    # worked example: pendulum
    g, s, rel, sh = L.pendulum_budget(1.000, 0.005, 2.007, 0.010)
    checks.append(("worked example: g = 9.801 m/s^2 and sigma_g = 0.109 m/s^2", abs(g - 9.801) < 5e-4 and abs(s - 0.109) < 5e-4))
    checks.append(("worked example: relative uncertainty of g is 1.1 percent", abs(100 * rel - 1.115) < 5e-3))
    checks.append(("worked example: variance share of L is 20 percent and of T is 80 percent",
                   abs(sh[0] - 0.20) < 0.005 and abs(sh[1] - 0.80) < 0.005))
    hand = 9.801 * np.sqrt(0.005 ** 2 + (2 * 0.010 / 2.007) ** 2)
    checks.append(("hand calculation sqrt((dL/L)^2 + (2 dT/T)^2) * g equals the code", abs(hand - s) < 5e-4))
    checks.append(("reporting rule: 9.801 +- 0.109 is written 9.8 +- 0.1", L.round_report(9.801, 0.109)[:2] == (9.8, 0.1)))
    checks.append(("reporting rule: 1234.5 +- 96 is written 1200 +- 100", L.round_report(1234.5, 96)[:2] == (1200, 100)))
    # linear formula against Monte Carlo
    mc = L.mc_sigma(L.pendulum_g, [1.0, 2.007], [0.005, 0.010])
    checks.append(("pendulum: Monte Carlo sigma agrees with the formula within 1 percent", abs(mc / s - 1) < 0.01))
    a_lin = L.linear_sigma(L.area_grads(12.3, 8.4), [0.1, 0.1])
    a_mc = L.mc_sigma(L.area, [12.3, 8.4], [0.1, 0.1])
    checks.append(("rectangle: formula 1.49 cm^2 agrees with Monte Carlo within 1 percent", abs(a_lin - 1.489) < 1e-3 and abs(a_mc / a_lin - 1) < 0.01))
    m, r, h, sg = 17.10, 0.635, 5.0, [0.01, 0.0005, 0.01]
    d_lin = L.linear_sigma(L.density_grads(m, r, h), sg)
    d_mc = L.mc_sigma(L.density, [m, r, h], sg)
    checks.append(("cylinder: density 2.700 g/cm^3, sigma 0.0071, Monte Carlo within 1 percent",
                   abs(L.density(m, r, h) - 2.700) < 5e-4 and abs(d_lin - 0.0071) < 5e-5 and abs(d_mc / d_lin - 1) < 0.01))
    shd = L.variance_shares(L.density_grads(m, r, h), sg)
    checks.append(("cylinder error budget: shares of mass, radius, height are 5, 36, 59 percent",
                   np.allclose(shd, [0.050, 0.364, 0.586], atol=0.002) and abs(shd.sum() - 1) < 1e-12))
    # special cases
    rng = np.random.default_rng(5)
    x = rng.normal(20, 0.5, 10 ** 6)
    y = rng.normal(30, 0.9, 10 ** 6)
    checks.append(("sums: errors add in quadrature (sqrt(0.5^2 + 0.9^2) = 1.03)",
                   abs((x + y).std() / np.hypot(0.5, 0.9) - 1) < 0.01))
    checks.append(("products: relative errors add in quadrature (2.5 % and 3 % give 3.9 %)",
                   abs((x * y).std() / 600 / np.hypot(0.5 / 20, 0.9 / 30) - 1) < 0.01 and abs(100 * np.hypot(0.025, 0.03) - 3.9) < 0.05))
    z = rng.normal(10, 0.2, 10 ** 6)
    checks.append(("powers: z^3 has 3 times the relative error of z (6 percent for 2 percent)",
                   abs((z ** 3).std() / (z ** 3).mean() / 0.06 - 1) < 0.02))
    # correlation
    d0 = L.linear_sigma([1, -1], [0.1, 0.1], 0.0)
    d9 = L.linear_sigma([1, -1], [0.1, 0.1], 0.9)
    d1 = L.linear_sigma([1, -1], [0.1, 0.1], 1.0)
    checks.append(("difference of two lengths: 0.141 cm if independent, 0.045 if rho = 0.9, 0 if rho = 1",
                   abs(d0 - 0.1414) < 5e-5 and abs(d9 - 0.0447) < 5e-5 and d1 < 1e-9))
    checks.append(("sum of two lengths grows with rho: 0.195 cm at rho = 0.9, 0.2 at rho = 1",
                   abs(L.linear_sigma([1, 1], [0.1, 0.1], 0.9) - 0.1949) < 5e-5 and abs(L.linear_sigma([1, 1], [0.1, 0.1], 1.0) - 0.2) < 1e-12))
    mc9 = L.mc_sigma(lambda a, b: a - b, [50.0, 30.0], [0.1, 0.1], rho=0.9)
    checks.append(("correlated Monte Carlo agrees: x - y with rho = 0.9 gives 0.045 cm", abs(mc9 / d9 - 1) < 0.02))
    # design problem
    b = {k: L.pendulum_budget(1.0, sl, 2.007, st)[2] * 100 for k, (sl, st) in
         {"now": (0.005, 0.010), "L": (0.0025, 0.010), "T": (0.005, 0.005), "both": (0.0025, 0.005), "perfectL": (0.0, 0.010)}.items()}
    checks.append(("design: halving the error of L gives 1.03 %, halving T gives 0.71 %, halving both gives 0.56 %",
                   abs(b["L"] - 1.027) < 5e-3 and abs(b["T"] - 0.706) < 5e-3 and abs(b["both"] - 0.557) < 5e-3))
    checks.append(("design: even a perfect length leaves 1.00 % because T dominates; only 'both' meets 0.6 %",
                   abs(b["perfectL"] - 0.997) < 5e-3 and b["both"] < 0.6 <= min(b["now"], b["L"], b["T"])))
    gB, sB, rB, shB = L.pendulum_budget(0.500, 0.002, 1.419, 0.005)
    checks.append(("question B: g = 9.803, u_g = 0.079, 0.81 percent, shares 24 and 76 percent, reported 9.80 +- 0.08",
                   abs(gB - 9.803) < 5e-4 and abs(sB - 0.0794) < 5e-4 and abs(100 * rB - 0.81) < 5e-3
                   and abs(shB[0] - 0.244) < 0.002 and L.round_report(gB, sB)[:2] == (9.8, 0.08)))
    checks.append(("question D: u_T = 0.1 / n gives 0.010 s for n = 10 and 0.005 s for n = 20; 20 swings alone give 0.71 %",
                   abs(0.1 / 10 - 0.010) < 1e-12 and abs(0.1 / 20 - 0.005) < 1e-12 and abs(b["T"] - 0.706) < 5e-3))
    checks.append(("difference u at rho = 0.9 is 0.045, sum 0.195 (question C), independent sum of two 0.1 errors is 0.141",
                   abs(d9 - 0.0447) < 5e-5 and abs(L.linear_sigma([1, 1], [0.1, 0.1]) - 0.1414) < 5e-5))
    checks.append(("edge: a zero-error input gives it a zero variance share", L.variance_shares([2.0, 3.0], [0.0, 0.1])[0] == 0.0))
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
