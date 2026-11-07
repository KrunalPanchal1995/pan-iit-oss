"""Checkpoint for Session 4. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    T = L.T_DATA
    k = L.synthetic(T, 0.03, 0)
    f = L.fit_two_channel(T, k)
    pt = L.param_table(f)
    true = float(L.two_channel_k(2000.0))
    mid, lo, hi = (v[0] for v in L.band(f, 2000.0))
    # ---- the roadmap checkpoint -----------------------------------------------------------------
    checks.append(("roadmap checkpoint: true k(2000 K) = 5.98e8 per s; 12 points at 3 percent noise, 500-1600 K, predict 5.70e8, within a factor 1.5",
                   abs(true / 5.984e8 - 1) < 1e-3 and abs(mid / 5.704e8 - 1) < 0.002 and 1 / 1.5 < mid / true < 1.5))
    fl = L.line_fit(T, k)
    ratio_line = true / float(L.line_k(fl, 2000.0))
    checks.append(("the straight line on the same data is 51 times too low (Session 3's 800-1600 K data: 9.2 times)", abs(ratio_line - 50.8) < 0.2))
    T3 = np.linspace(800.0, 1600.0, 9)
    k3 = L.synthetic(T3, 0.03, 2)
    checks.append(("Session 3 data (9 points, 800-1600 K): line 9.23 times too low, two-channel fit within 2 percent",
                   abs(true / float(L.line_k(L.line_fit(T3, k3), 2000.0)) - 9.23) < 0.02 and abs(L.band(L.fit_two_channel(T3, k3), 2000.0)[0][0] / true - 0.986) < 0.002))
    # ---- the fit ---------------------------------------------------------------------------------
    checks.append(("worked example: lnA1 = 16.130, E1 = 50.05, lnA2 = 32.099, E2 = 198.51 kJ/mol (truth 16.118, 50, 32.236, 200)",
                   np.allclose(f["p"], [16.1303, 50.0460, 32.0986, 198.5080], atol=0.002) and abs(L.P_TRUE[0] - 16.118) < 1e-3))
    checks.append(("worked example: s = 0.0217 on 8 degrees of freedom (true noise 0.03)", abs(f["s"] - 0.02167) < 2e-5 and f["df"] == 8))
    checks.append(("standard errors: 0.041, 0.228, 0.102 and 1.186", np.allclose(pt["se"], [0.0406, 0.2283, 0.1017, 1.1857], atol=0.0006)))
    checks.append(("noise-free data: the fit returns the true parameters", np.allclose(L.fit_two_channel(T, L.two_channel_k(T))["p"], L.P_TRUE, atol=1e-6)))
    checks.append(("crossover: truth 1119 K, fit 1118 K; the hot channel carries 50 percent there, 99.9 percent at 2000 K, nothing at 500 K",
                   abs(L.crossover_T(L.P_TRUE) - 1119.29) < 0.01 and abs(L.crossover_T(f["p"]) - 1118.21) < 0.01
                   and abs(float(L.channel_share(L.P_TRUE, 1119.29)) - 0.5) < 1e-3 and float(L.channel_share(L.P_TRUE, 2000.0)) > 0.999 and float(L.channel_share(L.P_TRUE, 500.0)) < 1e-6))
    sw = L.fit_two_channel(T, k, starts=[[32.0, 200.0, 16.0, 50.0]])
    checks.append(("channels are labelled by Ea: a start with the channels swapped still returns E1 < E2 and the same fit", sw["p"][1] < sw["p"][3] and np.allclose(sw["p"], f["p"], atol=1e-6)))
    bad = L.fit_two_channel(T, k, starts=[[20.0, 300.0, 20.0, 20.0]])
    checks.append(("a single bad start gets stuck (RSS 16.1); the three built-in starts reach RSS 0.00376", bad["rss"] > 10.0 and abs(f["rss"] - 0.003756) < 2e-6 and f["n_starts"] == 3))
    # ---- covariance ------------------------------------------------------------------------------
    checks.append(("identifiability: lnA and E of the same channel are correlated, 0.974 and 0.995", abs(pt["corr"][0, 1] - 0.974) < 0.002 and abs(pt["corr"][2, 3] - 0.9946) < 0.001))
    checks.append(("condition number of the scaled J^T J is 460 here, and far higher when the data stop at 1000 K",
                   abs(L.condition_number(f, T) - 459.5) < 1.0 and L.condition_number(L.fit_two_channel(np.linspace(500, 1000, 12), L.synthetic(np.linspace(500, 1000, 12), 0.03, 0)), np.linspace(500, 1000, 12)) > 5000))
    # ---- band ------------------------------------------------------------------------------------
    se = float(L.se_ln_k(f, [2000.0])[0])
    checks.append(("worked example: se of ln k at 2000 K = 0.0317 and the 95 percent interval is 5.30e8 to 6.14e8 (factor 1.157), true value inside",
                   abs(se - 0.03167) < 2e-5 and abs(lo / 5.3027e8 - 1) < 0.001 and abs(hi / 6.1366e8 - 1) < 0.001 and abs(hi / lo - 1.1573) < 0.001 and lo < true < hi))
    med, mlo, mhi = L.mc_predict(f, 2000.0)
    checks.append(("Monte Carlo from the covariance agrees with the delta-method band within 1.5 percent",
                   abs(med / mid - 1) < 0.005 and abs(mlo / lo - 1) < 0.015 and abs(mhi / hi - 1) < 0.015))
    checks.append(("the band is narrowest inside the data and flares outside: factor at 1000 K, 1600 K and 2000 K increases",
                   (lambda r: r[0] < r[1] < r[2])([float(L.band(f, t)[2][0] / L.band(f, t)[1][0]) for t in (1000.0, 1600.0, 2000.0)])))
    # ---- model comparison ------------------------------------------------------------------------
    cm = L.compare_models(T, k)
    checks.append(("model comparison: AICc 8.8 for the line and -83.1 for two channels (difference 92 in favour of two channels)",
                   abs(cm["aicc_line"] - 8.828) < 0.01 and abs(cm["aicc_two"] + 83.116) < 0.01 and abs(cm["delta"] - 91.94) < 0.02))
    rl = L.sign_runs(fl["res"])
    r2 = L.sign_runs(np.log(k) - L.ln_k(f["p"], T))
    checks.append(("the line's residuals come in 3 runs of one sign (a curve), the two-channel residuals in 7 (noise); s is 1.267 against 0.0217",
                   rl == 3 and r2 == 7 and abs(fl["s"] - 1.2672) < 0.001))
    # ---- validation ------------------------------------------------------------------------------
    r = L.trials(T, repeats=1000)
    checks.append((f"validation: 1000 repeated experiments, {100 * r['within15']:.0f} percent within a factor 1.5, interval holds the truth {100 * r['coverage']:.1f} percent (about 95), median factor {r['median_factor']:.2f}",
                   r["within15"] > 0.99 and abs(r["coverage"] - 0.945) < 0.001 and 0.93 < r["coverage"] < 0.97 and abs(r["median_factor"] - 1.215) < 0.005))
    r6 = L.trials(np.linspace(500.0, 1600.0, 6), repeats=150)
    r5 = L.trials(np.linspace(500.0, 1600.0, 5), repeats=150)
    checks.append((f"few points: 6 points give median factor {r6['median_factor']:.2f}, 5 points {r5['median_factor']:.1f} (1 degree of freedom), still honest",
                   abs(r6["median_factor"] - 1.51) < 0.02 and abs(r5["median_factor"] - 3.35) < 0.05 and r5["coverage"] > 0.9 and r5["within15"] > 0.95))
    r20 = L.trials(T, rel_noise=0.20, repeats=300)
    checks.append((f"noise: at 20 percent error only {100 * r20['within15']:.0f} percent of predictions are within 1.5, the band widens to {r20['median_factor']:.1f} and the coverage stays {100 * r20['coverage']:.0f} percent",
                   abs(r20["within15"] - 0.82) < 0.01 and abs(r20["median_factor"] - 3.69) < 0.05 and r20["coverage"] > 0.92))
    # ---- failures --------------------------------------------------------------------------------
    rs = {int(t): v for t, *v in L.reach_study([900, 1100, 1300], repeats=150)}
    checks.append((f"failure: data stop at 900 K: {100 * rs[900][0]:.1f} percent within 1.5, and the interval holds the truth only {100 * rs[900][1]:.0f} percent: the model cannot see a channel the data never reach",
                   rs[900][0] < 0.03 and abs(rs[900][1] - 0.22) < 0.01))
    checks.append((f"data stop at 1100 K (about the crossover): {100 * rs[1100][0]:.0f} percent within 1.5, honest but huge band (median factor {rs[1100][2]:.0f}); at 1300 K: {100 * rs[1300][0]:.0f} percent",
                   abs(rs[1100][0] - 0.287) < 0.01 and rs[1100][2] > 50 and rs[1100][1] > 0.92 and rs[1300][0] > 0.98))
    d = []
    for tm in (900, 1100):
        Tm = np.linspace(500.0, tm, 12)
        d.append(np.median([L.compare_models(Tm, L.synthetic(Tm, 0.03, 100 + i))["delta"] for i in range(40)]))
    checks.append((f"AICc as a warning: when the data stop at 900 K the line wins (median difference {d[0]:.1f}); at 1100 K the two channels win ({d[1]:.0f})",
                   d[0] < 0 and d[1] > 10))
    # ---- mini-project ----------------------------------------------------------------------------
    pm = np.array([np.log(3e6), 60.0, np.log(2e12), 170.0])
    Tm = np.linspace(600.0, 1500.0, 10)
    km = L.synthetic(Tm, 0.04, 9, pm)
    fm = L.fit_two_channel(Tm, km)
    qm = L.param_table(fm)
    mm, lm, hm = (v[0] for v in L.band(fm, 2000.0))
    tm_true = float(L.two_channel_k(2000.0, pm))
    checks.append(("mini-project data: Ea1 = 60.04 +- 0.83 and Ea2 = 167.8 +- 1.57 kJ/mol, crossover 980 K (truth 987 K)",
                   abs(fm["p"][1] - 60.04) < 0.02 and abs(qm["se"][1] - 0.83) < 0.02 and abs(fm["p"][3] - 167.80) < 0.03 and abs(qm["se"][3] - 1.57) < 0.02
                   and abs(L.crossover_T(fm["p"]) - 980.3) < 0.2 and abs(L.crossover_T(pm) - 986.6) < 0.2))
    checks.append(("mini-project: k(2000 K) = 6.75e7 per s with interval 5.95e7 to 7.67e7, true 7.27e7 inside; the line would be 13 times too low",
                   abs(mm / 6.752e7 - 1) < 0.002 and abs(lm / 5.947e7 - 1) < 0.002 and abs(hm / 7.666e7 - 1) < 0.002 and lm < tm_true < hm
                   and abs(tm_true / 7.272e7 - 1) < 0.001 and abs(tm_true / float(L.line_k(L.line_fit(Tm, km), 2000.0)) - 13.43) < 0.1))
    ws = L.trials(np.linspace(600.0, 1000.0, 10), rel_noise=0.04, repeats=150, p=pm)
    checks.append((f"mini-project lever: stop at 1000 K and only {100 * ws['within15']:.0f} percent of predictions are within 1.5 (full window: 100 percent)",
                   ws["within15"] < 0.4 and L.trials(Tm, rel_noise=0.04, repeats=150, p=pm)["within15"] > 0.99))
    # ---- edge cases ------------------------------------------------------------------------------
    raised = []
    for fn in (lambda: L.fit_two_channel(T[:4], k[:4]), lambda: L.compare_models(T[:5], k[:5])):
        try:
            fn()
            raised.append(False)
        except ValueError:
            raised.append(True)
    checks.append(("edge cases: 4 points cannot fit 4 parameters with an error estimate, and 5 points cannot be compared by AICc: both refused", all(raised)))
    five = L.fit_two_channel(T[::3].tolist() + [1550.0], L.synthetic(T[::3].tolist() + [1550.0], 0.03, 3))
    checks.append(("edge case: 5 points give 1 degree of freedom and t = 12.706", five["df"] == 1 and abs(L.t95(five["df"]) - 12.706) < 1e-9))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
