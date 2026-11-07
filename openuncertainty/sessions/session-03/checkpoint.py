"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # small errors: linear and Monte Carlo agree
    o1 = L.mc_samples(L.ratio, [10.0, 5.0], [0.5, 0.05])
    lin1 = L.numeric_linear_sigma(L.ratio, [10.0, 5.0], [0.5, 0.05])
    lo1, hi1 = L.percentile_interval(o1)
    checks.append(("1 % error in the denominator: linear and Monte Carlo intervals both 1.80 to 2.20",
                   abs(2 - 1.96 * lin1 - 1.80) < 5e-3 and abs(lo1 - 1.80) < 5e-3 and abs(hi1 - 2.20) < 5e-3))
    # worked example: large error
    o = L.mc_samples(L.ratio, [10.0, 5.0], [0.5, 1.5])
    lin = L.numeric_linear_sigma(L.ratio, [10.0, 5.0], [0.5, 1.5])
    lo, hi = L.percentile_interval(o)
    checks.append(("worked example: linear sigma 0.61, linear interval 0.81 to 3.19",
                   abs(lin - 0.608) < 5e-3 and abs(2 - 1.96 * lin - 0.81) < 5e-3 and abs(2 + 1.96 * lin - 3.19) < 5e-3))
    hand = 2.0 * np.hypot(0.5 / 10.0, 1.5 / 5.0)
    checks.append(("hand calculation: ratio relative errors 5 % and 30 % give sigma 2 * 0.304 = 0.61", abs(hand - lin) < 1e-4))
    checks.append(("worked example: Monte Carlo 95 % interval is 1.24 to 4.85 (asymmetric)",
                   abs(lo - 1.24) < 0.03 and abs(hi - 4.85) < 0.06 and (hi - 2.0) > 2 * (2.0 - lo)))
    cover = float(np.mean((o > 2 - 1.96 * lin) & (o < 2 + 1.96 * lin)))
    checks.append(("the linear 95 % interval holds only about 89 % of the Monte Carlo outcomes", abs(cover - 0.894) < 0.006))
    checks.append(("the Monte Carlo mean of x/y is above 2 (about 2.18), the linear value", 2.12 < o.mean() < 2.24))
    checks.append(("seeded Monte Carlo is repeatable", np.array_equal(L.mc_samples(L.ratio, [10.0, 5.0], [0.5, 1.5], n=50),
                                                                   L.mc_samples(L.ratio, [10.0, 5.0], [0.5, 1.5], n=50))))
    # central differences
    f = lambda t: 4 * np.pi ** 2 / t ** 2
    exact = -8 * np.pi ** 2 / 2.007 ** 3
    err = lambda h: abs(L.central_diff(f, 2.007, h * 2.007) / exact - 1)
    checks.append(("central difference: analytic slope is -9.77 and a step of 1e-6 is right to 1e-11",
                   abs(exact + 9.767) < 5e-3 and err(1e-6) < 1e-11))
    checks.append(("step size: error 2e-2 at h = 0.1, 2e-6 at 1e-3, and round-off makes 1e-13 worse than 1e-6",
                   abs(err(0.1) - 0.0203) < 5e-4 and abs(err(1e-3) - 2.0e-6) < 1e-7 and err(1e-13) > 1e3 * err(1e-6)))
    # non-normal inputs, GUM
    checks.append(("digital ruler: LSB 0.01 mm gives standard uncertainty 0.0029 mm", abs(L.uniform_sigma(0.01) - 0.00289) < 5e-6))
    u = np.random.default_rng(1).uniform(-0.005, 0.005, 10 ** 6)
    checks.append(("simulation of a uniform band of width LSB agrees with LSB / sqrt(12)", abs(u.std() / L.uniform_sigma(0.01) - 1) < 0.01))
    z = np.random.default_rng(3).standard_normal(10 ** 6)
    checks.append(("coverage factor k = 2 covers 95.45 % of a normal distribution", abs(np.mean(np.abs(z) < 2) - 0.9545) < 0.002 and L.expanded(0.5) == 1.0))
    checks.append(("combined uncertainty of 3 and 4 (sensitivity 1) is 5", abs(L.combined_uncertainty([1, 1], [3, 4]) - 5.0) < 1e-12))
    # failure case: maximum
    s = 0.1
    sm = L.mc_samples(np.sin, [np.pi / 2], [s])
    lin_top = L.numeric_linear_sigma(np.sin, [np.pi / 2], [s])
    checks.append(("failure: at the top of sin the first-order sigma is 0 but the true spread is 0.0070",
                   lin_top < 1e-9 and abs(sm.std() - 0.0070) < 2e-4))
    checks.append(("second-order formula |f''| s^2 / sqrt(2) = 0.0071 matches, and the mean drops to 0.995",
                   abs(L.second_order_sigma(-1.0, s) - 0.0071) < 5e-5 and abs(sm.std() / L.second_order_sigma(-1.0, s) - 1) < 0.02
                   and abs(sm.mean() - 0.995) < 5e-4))
    sm1 = L.mc_samples(np.sin, [1.0], [s])
    checks.append(("away from the top (x = 1 rad) the first-order formula works: 0.054",
                   abs(sm1.std() - np.cos(1.0) * s) < 5e-4 and abs(np.cos(1.0) * s - 0.054) < 5e-4))
    # mini-project: density of a cylinder from calipers and a scale
    dr = np.array([12.71, 12.69, 12.70, 12.72, 12.68])
    hr = np.array([50.02, 49.98, 50.01, 50.03, 49.96])
    m = 17.10
    ud = np.hypot(dr.std(ddof=1) / np.sqrt(5), L.uniform_sigma(0.01))
    uh = np.hypot(hr.std(ddof=1) / np.sqrt(5), L.uniform_sigma(0.01))
    um = np.hypot(L.uniform_sigma(0.01), 0.01)
    rho = lambda mm, d, h: mm / (np.pi * (d / 20.0) ** 2 * (h / 10.0))
    d, h = dr.mean(), hr.mean()
    v = rho(m, d, h)
    uc = L.numeric_linear_sigma(rho, [m, d, h], [um, ud, uh])
    checks.append(("mini-project: standard uncertainties of d, h, m are 0.0076 mm, 0.0134 mm, 0.0104 g",
                   abs(ud - 0.00764) < 5e-5 and abs(uh - 0.01335) < 5e-5 and abs(um - 0.01041) < 5e-5))
    checks.append(("mini-project: density 2.6998 g/cm^3, combined uncertainty 0.0037, expanded (k = 2) 0.0074",
                   abs(v - 2.6998) < 5e-4 and abs(uc - 0.00371) < 5e-5 and abs(L.expanded(uc) - 0.00742) < 1e-4))
    shares = np.array([um / m, 2 * ud / d, uh / h]) ** 2
    shares = shares / shares.sum()
    checks.append(("mini-project: variance shares mass 20 %, diameter 77 %, height 4 %; diameter dominates",
                   np.allclose(shares, [0.196, 0.766, 0.038], atol=0.002) and int(np.argmax(shares)) == 1))
    mc = L.mc_samples(rho, [m, d, h], [um, ud, uh])
    mlo, mhi = L.percentile_interval(mc)
    checks.append(("mini-project: Monte Carlo agrees: sigma 0.0037, 95 % interval 2.693 to 2.707",
                   abs(mc.std() / uc - 1) < 0.02 and abs(mlo - 2.6925) < 5e-4 and abs(mhi - 2.7070) < 5e-4))
    checks.append(("mini-project: the final report is 2.700 +- 0.007 g/cm^3 (k = 2)",
                   (round(v, 3), round(2 * uc, 3)) == (2.700, 0.007)))
    # assessment numbers
    checks.append(("question B: 0.1 mm step gives 0.0289 mm and U = 0.0577 mm",
                   abs(L.uniform_sigma(0.1) - 0.0289) < 5e-5 and abs(L.expanded(L.uniform_sigma(0.1)) - 0.0577) < 5e-5))
    o10b = L.mc_samples(L.ratio, [10.0, 5.0], [0.5, 0.5])
    l10 = L.numeric_linear_sigma(L.ratio, [10.0, 5.0], [0.5, 0.5])
    m10 = L.percentile_interval(o10b)
    d10 = (m10[1] - (2 + 1.96 * l10)) / m10[1]
    d30 = (hi - (2 + 1.96 * lin)) / hi
    checks.append(("question D: at 10 % linear is 1.56 to 2.44, Monte Carlo 1.62 to 2.53, upper ends differ 3.6 %; at 30 % they differ 34 %",
                   abs(2 - 1.96 * l10 - 1.56) < 5e-3 and abs(2 + 1.96 * l10 - 2.44) < 5e-3 and abs(m10[0] - 1.62) < 5e-3
                   and abs(m10[1] - 2.53) < 5e-3 and abs(d10 - 0.036) < 0.003 and abs(d30 - 0.34) < 0.01))
    checks.append(("app challenge: (1.96 r)^2 < 0.05 holds at 10 % (0.038) and fails at 12 % (0.055) and 25 %",
                   (1.96 * 0.10) ** 2 < 0.05 < (1.96 * 0.12) ** 2 and abs((1.96 * 0.10) ** 2 - 0.038) < 5e-4))
    checks.append(("misconception: central-difference error is 4e-12 at 1e-6 and 2e-5 at 1e-13",
                   abs(np.log10(err(1e-6)) - np.log10(4.3e-12)) < 0.2 and abs(np.log10(err(1e-13)) - np.log10(1.7e-5)) < 0.3))
    # milestone data quoted in the roadmap
    gf = lambda a, b: 4 * np.pi ** 2 * a / b ** 2
    ref = L.mc_samples(gf, [1.0, 2.007], [0.005, 0.010], n=10 ** 6).std()
    e200 = np.mean([abs(L.mc_samples(gf, [1.0, 2.007], [0.005, 0.010], n=200, seed=k).std() / ref - 1) for k in range(200)])
    checks.append(("roadmap fact: plain Monte Carlo with N = 200 misses the spread of g by about 4 percent",
                   abs(ref - 0.109) < 1e-3 and 0.035 < e200 < 0.047))
    o10 = L.mc_samples(L.ratio, [10.0, 5.0], [0.5, 0.5])
    checks.append(("roadmap fact: for a 10 % denominator error the mean of x/y is 2.02 while the linear value is 2",
                   abs(o10.mean() - 2.02) < 0.004))
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
