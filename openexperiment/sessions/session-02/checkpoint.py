"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    xb = float(L.REF.mean())
    sxx = float(np.sum((L.REF - xb) ** 2))
    checks.append(("reference grid: n = 11, xbar = 50, Sxx = 11000", len(L.REF) == 11 and xb == 50.0 and sxx == 11000.0))

    # fit agrees with np.polyfit on one noisy dataset
    rng = np.random.default_rng(2)
    y = L.sensor(L.REF, rng)
    f = L.fit_calibration(L.REF, y)
    pf = np.polyfit(L.REF, y, 1)
    checks.append(("fit_calibration slope and intercept equal np.polyfit",
                   abs(f["slope"] - pf[0]) < 1e-9 and abs(f["intercept"] - pf[1]) < 1e-9))
    # exact line: zero residual
    fx = L.fit_calibration(L.REF, 2.0 * L.REF + 3.0)
    checks.append(("edge case: noise-free data gives the exact line and s = 0",
                   abs(fx["slope"] - 2.0) < 1e-9 and abs(fx["intercept"] - 3.0) < 1e-9 and fx["s"] < 1e-9))

    # Monte Carlo of the whole calibration experiment, 20000 repeats, vectorised
    rng = np.random.default_rng(1)
    R = 20000
    Y = L.GAIN * L.REF + L.OFFSET + rng.normal(0, L.NOISE_SD, (R, 11))
    m = ((L.REF - xb) * (Y - Y.mean(1, keepdims=True))).sum(1) / sxx
    c = Y.mean(1) - m * xb
    se_m = L.NOISE_SD / math.sqrt(sxx)
    se_c = L.NOISE_SD * math.sqrt(1 / 11 + xb ** 2 / sxx)
    checks.append(("hand calculation: SE(slope) = 0.3 / sqrt(11000) = 0.00286", abs(se_m - 0.00286) < 0.00001))
    checks.append(("simulated scatter of the slope matches the formula (within 3 percent)",
                   abs(m.std(ddof=1) / se_m - 1) < 0.03))
    checks.append(("simulated scatter of the intercept (0.169) matches the formula (within 3 percent)",
                   abs(c.std(ddof=1) / se_c - 1) < 0.03 and abs(se_c - 0.169) < 0.001))
    checks.append(("the fitted slope and intercept are unbiased: means 1.020 and -0.800",
                   abs(m.mean() - L.GAIN) < 0.0001 and abs(c.mean() - L.OFFSET) < 0.005))

    # bootstrap check on the single dataset
    bm, bc = L.bootstrap_se(L.REF, y, 2000, 5)
    checks.append(("bootstrap standard errors agree with the formulas within 15 percent",
                   abs(bm / f["se_slope"] - 1) < 0.15 and abs(bc / f["se_intercept"] - 1) < 0.15))

    # worked example: inverse prediction with the nominal line
    nominal = {"slope": 1.02, "intercept": -0.8, "s": 0.3, "n": 11, "xbar": 50.0, "sxx": 11000.0}
    x0, u = L.invert(nominal, 30.4, 1)
    checks.append(("worked example: reading 30.4 -> 30.59 degrees C, uncertainty 0.31",
                   abs(x0 - 30.588) < 0.001 and abs(u - 0.312) < 0.001))
    x4, u4 = L.invert(nominal, 30.4, 4)
    checks.append(("averaging k = 4 new readings cuts the uncertainty to 0.18", abs(u4 - 0.180) < 0.001))
    # simulated inverse prediction at true 30 degrees C
    ynew = L.GAIN * 30.0 + L.OFFSET + rng.normal(0, L.NOISE_SD, R)
    xh = (ynew - c) / m
    th = L.NOISE_SD / L.GAIN * math.sqrt(1 + 1 / 11 + (30.0 - xb) ** 2 / sxx)
    checks.append(("simulated inverse-prediction scatter at 30 degrees C matches the formula (within 3 percent)",
                   abs(xh.std(ddof=1) / th - 1) < 0.03))
    checks.append(("uncertainty is smallest at the middle of the range (50) and larger at 0",
                   L.invert(nominal, 1.02 * 50 - 0.8)[1] < L.invert(nominal, -0.8)[1]))

    # repeatability / reproducibility
    rep, repro = L.repeat_and_reproduce(L.day_data(2000, 10, 3))
    checks.append(("repeatability is about 0.30 degrees C", abs(rep - 0.30) < 0.01))
    checks.append(("reproducibility is about sqrt(0.30^2 + 0.50^2) = 0.58 degrees C",
                   abs(repro - math.sqrt(0.09 + 0.25)) < 0.02 and repro > rep))

    # quantisation
    checks.append(("8 bits over 0..100: LSB = 0.390625 degrees C", abs(L.lsb(0, 100, 8) - 0.390625) < 1e-12))
    checks.append(("8 bits: LSB / sqrt(12) = 0.113 degrees C", abs(L.lsb(0, 100, 8) / math.sqrt(12) - 0.1128) < 0.0001))
    ok = True
    for bits in (6, 8, 10, 12):
        pred = L.lsb(0, 100, bits) / math.sqrt(12)
        ok &= abs(L.quantisation_rms(0, 100, bits, 200000, 4) / pred - 1) < 0.01
    checks.append(("measured rounding error equals LSB / sqrt(12) within 1 percent for 6, 8, 10, 12 bits", ok))
    checks.append(("each extra bit halves the step: 10 bits has LSB 0.0977", abs(L.lsb(0, 100, 10) - 0.09765625) < 1e-12))
    q = L.quantise(np.array([-5.0, 105.0]), 0, 100, 8)
    checks.append(("edge case: values outside the range are clipped to the first and last step",
                   abs(q[0] - 0.5 * 0.390625) < 1e-12 and abs(q[1] - (100 - 0.5 * 0.390625)) < 1e-12))
    quiet = L.mean_of_quantised(20.25, 0.0, 1000, 0, 100, 8, 1)
    noisy = L.mean_of_quantised(20.25, 0.4, 200000, 0, 100, 8, 1)
    checks.append(("no noise: averaging quantised readings of 20.25 keeps an error of 0.13 (no help from averaging)",
                   abs((quiet - 20.25) - (-0.1328)) < 0.001))
    checks.append(("noise about one step wide (0.4) lets averaging remove the rounding error (error below 0.01)",
                   abs(noisy - 20.25) < 0.01))

    # bias vs random
    ok_b, ok_r = True, True
    for N in (1, 4, 16, 64, 256):
        mm, ss = L.average_error_stats(0.5, L.NOISE_SD, N, 4000, 8)
        ok_b &= abs(mm - 0.5) < 0.01
        ok_r &= abs(ss / (L.NOISE_SD / math.sqrt(N)) - 1) < 0.06
    checks.append(("averaging N = 1..256 readings leaves the bias at 0.50 (within 0.01)", ok_b))
    checks.append(("scatter of the average follows 0.30 / sqrt(N) (within 6 percent)", ok_r))

    # design
    checks.append(("worked example: 0.1 degrees at 95 percent with sd 0.30 needs N = 35 readings",
                   L.repeats_needed(0.30, 0.1) == 35))
    checks.append(("hand calculation: (1.96 * 0.30 / 0.1)^2 = 34.57, rounded up to 35",
                   abs((1.96 * 0.30 / 0.1) ** 2 - 34.57) < 0.01))
    checks.append(("N = 35 reaches 95 percent (0.9514), N = 34 does not (0.9481)",
                   L.coverage(0.30, 35, 0.1) >= 0.95 > L.coverage(0.30, 34, 0.1)
                   and abs(L.coverage(0.30, 35, 0.1) - 0.9514) < 0.0001))
    rng = np.random.default_rng(9)
    hit = np.mean(np.abs(rng.normal(0, 0.30, (40000, 35)).mean(1)) <= 0.1)
    checks.append(("simulation: the mean of 35 readings is within 0.1 of the truth about 95 percent of the time",
                   abs(hit - 0.9514) < 0.005))
    checks.append(("halving the target half-width needs 4 times the readings (sd 1: 385 for 0.1, 97 for 0.2)",
                   L.repeats_needed(1.0, 0.1) == 385 and L.repeats_needed(1.0, 0.2) == 97))
    checks.append(("edge case: a loose target needs only 1 reading (sd 0.3, half-width 0.9 -> 1)",
                   L.repeats_needed(0.3, 0.9) == 1))
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
