"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    T = L.T_DATA
    x = 1000.0 / T
    xb = x.mean()
    sxx = float(np.sum((x - xb) ** 2))
    k = L.synthetic(T, 0.05, 4)
    f = L.fit_with_cov(T, k)
    q = L.lnA_Ea(f)
    checks.append(("worked example: Sxx = 0.4113 and mean of 1000/T = 1.2841 (T = 778.7 K)", abs(sxx - 0.4113) < 1e-3 and abs(xb - 1.2841) < 1e-4))
    checks.append(("worked example: s = 0.0535 on 7 degrees of freedom", abs(f["s"] - 0.0535) < 1e-4 and f["df"] == 7))
    checks.append(("worked example: Ea = 149.43 +- 0.69 kJ/mol, ln A = 29.833 +- 0.109", abs(q["Ea"] - 149.43) < 0.01 and abs(q["se_Ea"] - 0.69) < 0.01 and abs(q["lnA"] - 29.833) < 0.001 and abs(q["se_lnA"] - 0.109) < 0.001))
    checks.append(("worked example: ln A and Ea are correlated, r = 0.986", abs(q["corr"] - 0.986) < 0.001))
    se = f["s"] * np.sqrt(1 / 9 + (0.5 - xb) ** 2 / sxx)
    checks.append(("worked example: se of ln k at 2000 K by hand = 0.0678", abs(se - 0.0678) < 1e-4 and abs(float(L.se_ln_k(f, [2000.0])[0]) - se) < 1e-12))
    mid, lo, hi = L.band(f, 2000.0)
    checks.append(("worked example: k(2000 K) = 1.13e9 per s, 95 percent interval 9.6e8 to 1.33e9", abs(mid[0] / 1.1315e9 - 1) < 0.001 and abs(lo[0] / 9.64e8 - 1) < 0.002 and abs(hi[0] / 1.328e9 - 1) < 0.002))
    checks.append(("the true k(2000 K) = 1.209e9 lies inside that interval", lo[0] < float(L.arrhenius_k(2000.0)) < hi[0] and abs(float(L.arrhenius_k(2000.0)) / 1.2091e9 - 1) < 1e-3))
    checks.append(("the band is narrowest at the mean of 1000/T: se = s/3 = 0.0178", abs(float(L.se_ln_k(f, [1000.0 / xb])[0]) - f["s"] / 3) < 1e-12))
    ratios = [float(L.band(f, t)[2][0] / L.band(f, t)[1][0]) for t in (800.0, 1500.0, 2000.0)]
    checks.append(("band width (upper/lower) flares: 1.09 at 800 K, 1.29 at 1500 K, 1.38 at 2000 K", abs(ratios[0] - 1.089) < 0.002 and abs(ratios[1] - 1.294) < 0.002 and abs(ratios[2] - 1.378) < 0.002))
    med, mlo, mhi = L.mc_predict(f, 2000.0)
    z = 1.96 * float(L.se_ln_k(f, [2000.0])[0])
    checks.append(("Monte Carlo median and the 1.96-sigma formula agree within 0.5 percent", abs(med / mid[0] - 1) < 0.005 and abs(mlo / (mid[0] * np.exp(-z)) - 1) < 0.015 and abs(mhi / (mid[0] * np.exp(z)) - 1) < 0.015))
    checks.append(("t factor for 3 degrees of freedom is 3.182 and for 7 is 2.365", abs(L.t95(3) - 3.182) < 1e-9 and abs(L.t95(7) - 2.365) < 1e-9))
    cov_p, ea_mean = L.coverage(T, 2000.0, repeats=2000)
    checks.append(("validation: 95 percent interval at 2000 K covers the truth 94.8 percent of 2000 repeats", abs(cov_p - 0.9475) < 0.001 and 0.93 < cov_p < 0.97))
    checks.append(("validation: fitted Ea averages 150.00 kJ/mol over repeats (unbiased)", abs(ea_mean - 150.0) < 0.01))
    cov_in, _ = L.coverage(T, 800.0, repeats=2000)
    checks.append(("validation: coverage inside the data (800 K) is also close to 95 percent", 0.93 < cov_in < 0.97))
    # narrow range failure
    Tn = np.linspace(900.0, 1000.0, 9)
    fn = L.fit_with_cov(Tn, L.synthetic(Tn, 0.05, 4))
    qn = L.lnA_Ea(fn)
    mn, ln_, hn = L.band(fn, 2000.0)
    checks.append(("failure: 900-1000 K only gives se(Ea) = 4.07 kJ/mol (5.9 times the 0.69 of the wide range)", abs(qn["se_Ea"] - 4.07) < 0.01 and abs(qn["se_Ea"] / q["se_Ea"] - 5.87) < 0.05))
    checks.append(("failure: the 2000 K interval spans a factor 3.6 (against 1.38)", abs(hn[0] / ln_[0] - 3.62) < 0.02 and qn["corr"] > 0.999))
    covn, _ = L.coverage(Tn, 2000.0, repeats=2000)
    checks.append(("narrow data are wide but honest: coverage is still about 95 percent (94.2)", abs(covn - 0.9415) < 0.001))
    # weights
    ps, ws = L.ea_scatter_weighted_vs_plain(np.linspace(600.0, 1000.0, 9))
    checks.append(("weights: uneven errors give Ea scatter 2.92 plain and 1.97 weighted kJ/mol", abs(ps - 2.92) < 0.03 and abs(ws - 1.97) < 0.03 and ws < ps))
    fw = L.fit_with_cov(T, k, sigma_ln=np.full(9, 0.05))
    checks.append(("weights: equal sigma gives the same Ea and se(Ea) = R sigma / sqrt(Sxx) = 0.648", abs(L.lnA_Ea(fw)["Ea"] - q["Ea"]) < 1e-9 and abs(L.lnA_Ea(fw)["se_Ea"] - 0.648) < 0.001))
    # curved plot
    Tc = np.linspace(800.0, 1600.0, 9)
    fc = L.straight_line_on_curved(Tc)
    mc, lc, hc = L.band(fc, 2000.0)
    true2 = float(L.two_channel_k(2000.0))
    checks.append(("failure: two-channel truth at 2000 K is 5.98e8 per s, the line predicts 6.5e7 (9.2 times too low)", abs(true2 / 5.984e8 - 1) < 1e-3 and abs(true2 / mc[0] - 9.23) < 0.05))
    checks.append(("failure: the true value is outside the 95 percent band", not (lc[0] <= true2 <= hc[0])))
    fs = L.fit_with_cov(Tc, L.synthetic(Tc, 0.03, 2))
    checks.append(("warning sign: the residual error s is 0.86 for the curved data, 0.037 for a true single channel", abs(fc["s"] - 0.856) < 0.005 and abs(fs["s"] - 0.0374) < 0.001))
    try:
        L.fit_with_cov([600.0, 1000.0], L.arrhenius_k([600.0, 1000.0]))
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge case: 2 points leave no degrees of freedom, so the fit refuses to give an error", raised))
    three = L.fit_with_cov([600.0, 800.0, 1000.0], L.synthetic([600.0, 800.0, 1000.0], 0.05, 1))
    checks.append(("edge case: 3 points give 1 degree of freedom and t = 12.706", three["df"] == 1 and abs(L.t95(1) - 12.706) < 1e-9))
    Tp = np.linspace(700.0, 1100.0, 7)
    fp = L.fit_with_cov(Tp, L.synthetic(Tp, 0.06, 21, 3e11, 120.0))
    qp = L.lnA_Ea(fp)
    mp, lp, hp = L.band(fp, 2000.0)
    tp = float(L.arrhenius_k(2000.0, 3e11, 120.0))
    checks.append(("mini-project data: Ea = 118.75 +- 1.42 kJ/mol", abs(qp["Ea"] - 118.75) < 0.01 and abs(qp["se_Ea"] - 1.42) < 0.01))
    checks.append(("mini-project: k(2000 K) = 2.0e8 per s with interval 1.5e8 to 2.67e8, true 2.2e8 inside", abs(mp[0] / 2.0e8 - 1) < 0.01 and abs(lp[0] / 1.5e8 - 1) < 0.01 and abs(hp[0] / 2.67e8 - 1) < 0.01 and lp[0] < tp < hp[0] and abs(tp / 2.2e8 - 1) < 0.01))
    checks.append(("mini-project: interval factor upper/lower is 1.78 for 700-1100 K", abs(hp[0] / lp[0] - 1.78) < 0.01))
    Tq = np.linspace(900.0, 1100.0, 7)
    fq = L.fit_with_cov(Tq, L.synthetic(Tq, 0.06, 21, 3e11, 120.0))
    mq, lq, hq = L.band(fq, 2000.0)
    checks.append(("mini-project lever: window 900-1100 K gives factor 3.12, above the limit 2", abs(hq[0] / lq[0] - 3.12) < 0.01))
    ends = np.array([700.0, 700.0, 700.0, 700.0, 1100.0, 1100.0, 1100.0])
    se_of = lambda Tt: 0.06 * np.sqrt(np.array([1.0, 0.5]) @ np.linalg.inv(np.column_stack([np.ones(7), 1000.0 / Tt]).T @ np.column_stack([np.ones(7), 1000.0 / Tt])) @ np.array([1.0, 0.5]))
    checks.append(("design for prediction: expected se of ln k(2000 K) with sigma 0.06 is 0.0866 for even spacing, 0.0663 with points at the ends",
                   abs(se_of(Tp) - 0.0866) < 0.0002 and abs(se_of(ends) - 0.0663) < 0.0002))
    checks.append(("design: 6 points from 800 K, 5 percent error: factor 1.52 on k(2000 K); 12 points from 500 K: 1.11",
                   abs(L.expected_factor(0.05, 6, 800.0) - 1.52) < 0.005 and abs(L.expected_factor(0.05, 12, 500.0) - 1.113) < 0.002))
    checks.append(("app challenge: 12 points from 500 K meets the 1.15 limit, the default (6 points from 800 K) does not",
                   L.expected_factor(0.05, 12, 500.0) <= 1.15 < L.expected_factor(0.05, 6, 800.0)))
    # ---- bootstrap ------------------------------------------------------------------------------
    import time
    Tm = np.linspace(700.0, 1100.0, 7)
    km = L.synthetic(Tm, 0.06, 21, 3e11, 120.0)
    fm = L.fit_with_cov(Tm, km)
    bm, blo, bhi = (v[0] for v in L.band(fm, 2000.0))
    t0 = time.time()
    r_med, r_lo, r_hi = L.bootstrap_predict(Tm, km, 2000.0)
    p_med, p_lo, p_hi = L.bootstrap_predict(Tm, km, 2000.0, method="pairs")
    dt = time.time() - t0
    true_m = float(L.arrhenius_k(2000.0, 3e11, 120.0))
    checks.append((f"bootstrap on the mini-project data: formula factor {bhi / blo:.2f}, residual bootstrap {r_hi / r_lo:.2f}, pairs bootstrap {p_hi / p_lo:.2f}; both bootstraps hold the true k, in {dt:.2f} s (under 20 s)",
                   abs(bhi / blo - 1.78) < 0.01 and r_lo <= true_m <= r_hi and p_lo <= true_m <= p_hi and 1.3 < r_hi / r_lo < bhi / blo and 1.3 < p_hi / p_lo < bhi / blo and dt < 20.0))
    checks.append(("bootstrap median agrees with the fitted line's prediction at 2000 K to 1%",
                   abs(r_med - bm) / bm < 0.01))
    ex = L.bootstrap_predict(Tm, L.arrhenius_k(Tm, 3e11, 120.0), 2000.0)
    checks.append(("noise-free data: the bootstrap interval collapses onto the true k", abs(ex[1] / true_m - 1) < 1e-9 and abs(ex[2] / true_m - 1) < 1e-9))
    c_band, _ = L.interval_coverage(Tm, 2000.0, "band", rel_noise=0.06)
    c_res, f_res = L.interval_coverage(Tm, 2000.0, "bootstrap-residual", rel_noise=0.06)
    checks.append((f"7 points, 1000 repeated experiments: t band covers {100 * c_band:.1f}% (about 95), residual bootstrap only {100 * c_res:.1f}% (too narrow)",
                   0.93 < c_band < 0.96 and 0.85 < c_res < 0.92))
    T40 = np.linspace(600.0, 1000.0, 40)
    c40, _ = L.interval_coverage(T40, 2000.0, "bootstrap-residual", rel_noise=0.06)
    checks.append((f"40 points: the residual bootstrap catches up ({100 * c40:.1f}% coverage)", 0.92 < c40 < 0.96))
    bad_method = bad_n = False
    try:
        L.bootstrap_predict(Tm, km, 2000.0, method="nope")
    except ValueError:
        bad_method = True
    try:
        L.bootstrap_predict(Tm[:2], km[:2], 2000.0)
    except ValueError:
        bad_n = True
    checks.append(("an unknown method name and fewer than 3 points are refused", bad_method and bad_n))
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
