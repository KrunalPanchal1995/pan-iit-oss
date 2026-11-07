"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    rng = np.random.default_rng(0)

    # --- run orders ---
    for kind in ("naive", "alternating", "abba", "random", "blocked"):
        o = L.make_order(kind, rng)
        if len(o) != 20 or o.sum() != 10:
            checks.append(("every run order has 20 runs, 10 of each treatment (%s)" % kind, False))
            break
    else:
        checks.append(("every run order has 20 runs, 10 of each treatment", True))
    checks.append(("worked example: all-A-then-all-B adds a drift bias of 0.05 * 10 = 0.50 degrees C",
                   abs(L.drift_bias(L.make_order("naive", rng)) - 0.50) < 1e-12))
    checks.append(("alternating ABAB adds 0.05 and ABBA adds exactly 0",
                   abs(L.drift_bias(L.make_order("alternating", rng)) - 0.05) < 1e-12
                   and abs(L.drift_bias(L.make_order("abba", rng))) < 1e-12))
    res = {k: L.order_study(k, 4000, 3) for k in ("naive", "alternating", "abba", "random", "blocked")}
    checks.append(("simulation: naive order estimates the effect 0.50 too high (bias 0.50 +- 0.02)",
                   abs(res["naive"][0] - 0.50) < 0.02))
    checks.append(("simulation: ABBA, random and blocked orders have bias below 0.02 in size",
                   all(abs(res[k][0]) < 0.02 for k in ("abba", "random", "blocked"))))
    checks.append(("simulation: alternating order has a small bias, about 0.05",
                   abs(res["alternating"][0] - 0.05) < 0.02))
    noise_only = 0.5 * math.sqrt(2.0 / 10.0)
    checks.append(("hand calculation: noise alone gives scatter 0.5 * sqrt(2/10) = 0.2236",
                   abs(noise_only - 0.2236) < 0.0001 and abs(res["abba"][1] / noise_only - 1) < 0.05))
    rand_pred = math.sqrt(noise_only ** 2 + 0.05 ** 2 * 7.0)
    checks.append(("hand calculation: full randomisation adds drift scatter 0.05 * sqrt(7): total 0.260",
                   abs(rand_pred - 0.2598) < 0.0005 and abs(res["random"][1] / rand_pred - 1) < 0.05))
    checks.append(("randomised blocks keep the scatter near the noise-only value (below 0.235) and below full randomisation",
                   res["blocked"][1] < 0.235 and res["blocked"][1] < res["random"][1]))
    z = np.mean([L.effect_estimate(L.make_order("naive", rng), rng, drift=0.0) for _ in range(4000)])
    checks.append(("without drift, even the naive order finds the true effect 0.30 (mean 0.29 to 0.31)",
                   abs(z - 0.30) < 0.015))

    # --- power ---
    checks.append(("worked example: d = 0.5, sigma = 1, 5 percent, 80 percent power needs n = 63 per group",
                   L.sample_size(0.5, 1.0) == 63))
    checks.append(("hand calculation: 2 * (1.96 + 0.8416)^2 / 0.25 = 62.79, rounded up to 63",
                   abs(2 * (1.96 + 0.8416) ** 2 / 0.25 - 62.79) < 0.02))
    checks.append(("halving d quadruples n: d = 0.25 needs 252", L.sample_size(0.25, 1.0) == 252))
    checks.append(("n = 63 has power 0.801, n = 62 has 0.795 (formula)",
                   abs(L.power_formula(63, 0.5, 1.0) - 0.8013) < 0.0005 and abs(L.power_formula(62, 0.5, 1.0) - 0.7950) < 0.0005))
    checks.append(("seeded Monte Carlo power at n = 63 is 0.80 (within 0.015 of the formula)",
                   abs(L.simulate_power(63, 0.5, 1.0, 20000, 1) - L.power_formula(63, 0.5, 1.0)) < 0.015))
    checks.append(("only 16 runs per group give power 0.29, so most real differences would be missed",
                   abs(L.power_formula(16, 0.5, 1.0) - 0.293) < 0.001 and abs(L.simulate_power(16, 0.5, 1.0, 20000, 1) - 0.293) < 0.015))
    checks.append(("edge case: with no true difference the test fires 5 percent of the time (0.05 +- 0.01)",
                   abs(L.simulate_power(63, 0.0, 1.0, 20000, 1) - 0.05) < 0.01))

    # --- factorial ---
    y = [L.system(a, b) for a, b in L.RUNS]
    checks.append(("worked example: the four runs give 54, 44, 44, 58", y == [54.0, 44.0, 44.0, 58.0]))
    checks.append(("effects from the four runs: A = 2, B = 2, AB = 12", L.factorial_effects(y) == (2.0, 2.0, 12.0)))
    checks.append(("one-factor-at-a-time stops at (-1, -1) with response 54", L.one_factor_at_a_time() == (-1, -1, 54.0)))
    checks.append(("the best setting is (+1, +1) with response 58, which one-factor-at-a-time misses",
                   max(y) == L.system(1, 1) == 58.0))
    checks.append(("without an interaction one-factor-at-a-time finds the best setting",
                   L.one_factor_at_a_time(lambda a, b: 50.0 + a + b) == (1, 1, 52.0)))
    r2 = np.random.default_rng(2)
    e = np.array([L.factorial_effects([L.system(a, b) + r2.normal(0, 1) for a, b in L.RUNS]) for _ in range(20000)])
    checks.append(("simulated: with noise sd 1 the effect estimates are unbiased and each has sd about 1",
                   np.allclose(e.mean(0), [2, 2, 12], atol=0.03) and np.allclose(e.std(0), 1.0, atol=0.03)))

    # --- drift and re-calibration ---
    checks.append(("worked example: re-calibrate every 15 days (1.96 * 0.10 + 0.02 * t <= 0.50)", L.recal_days() == 15))
    checks.append(("hand calculation: (0.50 - 0.196) / 0.02 = 15.2 days", abs((0.50 - 0.196) / 0.02 - 15.2) < 0.001))
    checks.append(("after 15 days the chance of being above +0.50 is 0.0228",
                   abs(L.p_exceed(15) - 0.0228) < 0.0001 and abs(L.simulate_exceed(15, 400000, 3) - 0.0228) < 0.002))
    checks.append(("after 20 days that chance has grown to 0.159", abs(L.p_exceed(20) - 0.1587) < 0.0005))
    checks.append(("edge case: an impossible tolerance (0.10) gives 0 days", L.recal_days(0.10, 0.10, 0.02) == 0))

    # --- extrapolation ---
    m, c, inside, err100 = L.extrapolation_demo()
    checks.append(("line fitted on 0..50 of the curved sensor: slope 1.10, intercept -0.75",
                   abs(m - 1.10) < 1e-9 and abs(c + 0.75) < 1e-9))
    checks.append(("inside 0..50 the largest residual is only 0.75 degrees C", abs(inside - 0.75) < 1e-9))
    checks.append(("at 100 degrees C the extrapolated line is wrong by 10.75 degrees C", abs(err100 - 10.75) < 1e-9))
    checks.append(("a straight sensor has no extrapolation problem (curvature 0 gives error 0)",
                   abs(np.polyfit([0, 25, 50], [0, 25, 50], 1)[0] * 100 - 100) < 1e-9))

    # --- mini-project ---
    T, V, yy = L.run_experiment(5, 1)
    checks.append(("mini-project design: 20 runs, each corner 5 times",
                   len(T) == 20 and all(np.sum((T == t) & (V == v)) == 5 for t in L.TS for v in L.VS)))
    eT, eV, eTV = L.two_factor_effects(T, V, yy)
    se = L.SENSOR_NOISE / math.sqrt(5)
    checks.append(("worked example: effects near the true 58.8 (T), 1.0 (V), 0.12 (T x V), each within 3 standard errors (0.13)",
                   abs(eT - 58.8) < 3 * se and abs(eV - 1.0) < 3 * se and abs(eTV - 0.12) < 3 * se))
    checks.append(("hand calculation: true T effect = 0.98 * 60 = 58.8; V effect = 0.8 + 0.004 * 50 = 1.0",
                   abs(0.98 * 60 - 58.8) < 1e-9 and abs(0.8 + 0.004 * 50 - 1.0) < 1e-9))
    b, s = L.fit_two_factor(T, V, yy)
    checks.append(("fitted coefficients near the truth (b1 = 0.98 within 0.01, b2 = 0.80 within 0.3); residual sd near 0.30",
                   abs(b[1] - 0.98) < 0.01 and abs(b[2] - 0.80) < 0.3 and abs(s - 0.30) < 0.08))
    check_x = L.estimate_T(np.array([0.5, 0.98, 0.8, 0.004]), 0.98 * 50 + 0.5 + 0.4 * (0.8 + 0.2), 5.4)
    checks.append(("inverting the exact model returns the temperature (50)", abs(check_x - 50.0) < 1e-9))
    sd_aware, naive_err = L.mini_project_stats(5, 400, 7)
    checks.append(("mini-project: with the voltage in the model, the error of one reading at 50 C, 5.4 V has sd 0.29 degrees C",
                   abs(sd_aware - 0.29) < 0.03))
    checks.append(("mini-project: ignoring the voltage gives a temperature error of 0.74 degrees C at 5.4 V",
                   abs(naive_err - 0.74) < 0.02))
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
