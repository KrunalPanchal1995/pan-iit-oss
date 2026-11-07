"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    tr, te = L.degree_curve()
    checks.append(("training error never rises with degree", bool(np.all(np.diff(tr) <= 1e-9))))
    best = int(np.argmin(te))
    checks.append((f"test error is U-shaped: best degree is 3 (got {best}), RMSE 0.365", best == 3 and abs(te[best] - 0.365) < 5e-3))
    checks.append(("degree 12 test error (5.1 t/ha) is more than 10 times the best; training error is 0.22",
                   te[12] > 10 * te[best] and abs(tr[12] - 0.22) < 0.01))
    checks.append(("degree 0 and 12 are both worse than degree 3", te[0] > te[best] and te[12] > te[best]))

    # worked example: ridge by hand on three points
    F = np.array([[-1.0], [0.0], [1.0]])
    y = np.array([0.0, 1.0, 5.0])
    sd = np.sqrt(2.0 / 3.0)
    m0, m3 = L.ridge_fit(F, y, 0.0), L.ridge_fit(F, y, 3.0)
    checks.append(("worked example: ridge by hand, lambda 0 gives standardised slope 6.1237/3 = 2.0412, raw slope 2.5",
                   abs(m0["beta"][0] - 6.1237 / 3) < 1e-3 and abs(m0["beta"][0] / sd - 2.5) < 1e-9))
    checks.append(("worked example: lambda = 3 halves the slope (factor 3/(3+3)): raw slope 1.25",
                   abs(m3["beta"][0] / sd - 1.25) < 1e-9))

    zt, yt = L.make_response(20, 1)
    zs, ys = L.make_response(500, 1001)
    mr = L.ridge_fit(L.poly_features(zt, 9), yt, 0.0)
    ls = L.poly_design(zs, 9) @ L.fit_poly(zt, yt, 9)
    checks.append(("lambda = 0 recovers least squares (same predictions as lstsq)", np.allclose(L.ridge_predict(mr, L.poly_features(zs, 9)), ls, atol=1e-5)))
    Fs, _, _ = L.standardise(L.poly_features(zt, 9))
    mm = L.ridge_fit(L.poly_features(zt, 9), yt, 2.0)
    aug = np.linalg.lstsq(np.vstack([Fs, np.sqrt(2.0) * np.eye(9)]), np.r_[yt - yt.mean(), np.zeros(9)], rcond=None)[0]
    checks.append(("closed form agrees with least squares on data augmented by sqrt(lambda) I", np.allclose(mm["beta"], aug, atol=1e-8)))
    lams = np.array([0, 0.01, 0.1, 1, 10, 100, 1000])
    big, tte = L.ridge_path(lams)
    checks.append(("ridge shrinks coefficients: largest |coef| falls from 26.0 to 0.02 as lambda grows", bool(np.all(np.diff(big) < 0)) and abs(big[0] - 26.0) < 0.1 and abs(big[-1] - 0.02) < 0.01))
    checks.append(("ridge test RMSE: 0.596 at lambda 0, best 0.371 at lambda 0.1, 1.16 at lambda 1000",
                   int(np.argmin(tte)) == 2 and abs(tte[0] - 0.596) < 5e-3 and abs(tte[2] - 0.371) < 5e-3 and abs(tte[-1] - 1.16) < 0.02))

    folds = L.kfold_indices(23, 5, seed=3)
    allidx = np.sort(np.concatenate(folds))
    checks.append(("edge: k-fold folds cover every index exactly once (n = 23, k = 5)", np.array_equal(allidx, np.arange(23)) and max(map(len, folds)) - min(map(len, folds)) <= 1))
    lam, _ = L.cv_choose_lambda(zt, yt, np.array([1e-3, 1e-2, 1e-1, 1, 10, 100]))
    deg, _ = L.cv_choose_degree(zt, yt)
    checks.append((f"cross-validation picks lambda 0.1 (got {lam}) and degree 6 (got {deg}) on these 20 seasons", lam == 0.1 and deg == 6))

    bv = {d: L.bias_variance(d) for d in (1, 3, 9)}
    checks.append(("variance at z0 = 0.9 grows with flexibility: degrees 1, 3, 9 give 0.057, 0.066, about 28000",
                   bv[1][1] < bv[3][1] < bv[9][1] and abs(bv[1][1] - 0.057) < 5e-3 and abs(bv[3][1] - 0.066) < 5e-3 and bv[9][1] > 1e4))
    checks.append(("bias: degree 1 is biased (0.54), degree 3 is nearly unbiased (-0.003)", abs(bv[1][0] - 0.537) < 0.01 and abs(bv[3][0]) < 0.02))

    x, yo = L.with_outliers()
    truth = np.array([1.0, 0.35])
    eo, et, eh = (np.abs(np.array(f(x, yo)) - truth)[1] for f in (L.ols_line, L.theil_sen_line, L.huber_line))
    checks.append(("outliers: slope 0.009 by least squares, 0.215 Theil-Sen, 0.290 Huber (true 0.35)",
                   abs(L.ols_line(x, yo)[1] - 0.009) < 2e-3 and abs(L.theil_sen_line(x, yo)[1] - 0.215) < 2e-3 and abs(L.huber_line(x, yo)[1] - 0.290) < 2e-3 and et < eo and eh < eo))
    xc = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    checks.append(("robust lines reproduce a perfect line y = 2 + 3x exactly",
                   np.allclose(L.theil_sen_line(xc, 2 + 3 * xc), [2, 3]) and np.allclose(L.huber_line(xc, 2 + 3 * xc), [2, 3], atol=1e-8)))

    t, ice, dr = L.make_confounded()
    raw = np.corrcoef(ice, dr)[0, 1]
    part = L.partial_corr(ice, dr, t)
    checks.append((f"confounder: ice cream and drowning correlate {raw:.2f} but partial correlation given temperature is {part:.2f}", abs(raw - 0.596) < 5e-3 and abs(part) < 0.1))

    ce = L.collinear_experiment()
    checks.append(("multicollinearity: coefficient sd 0.50 but sd of the sum 0.028 and of the prediction 0.049; condition number about 17000",
                   abs(ce["sd_b1"] - 0.502) < 0.01 and ce["sd_pred"] < 0.06 and ce["sd_b1"] > 8 * ce["sd_pred"] and 1e4 < ce["cond"] < 3e4))

    c25, se25, sd25 = L.slope_stats(25, 0.3)
    c100, se100, _ = L.slope_stats(100, 0.3)
    _, se_noisy, _ = L.slope_stats(25, 0.6)
    checks.append((f"recovery: slope +- 1.96 SE holds the true 0.35 in {c25:.3f} of 2000 repeats (about 95 percent)", 0.935 <= c25 <= 0.965 and abs(se25 - sd25) / sd25 < 0.05))
    checks.append(("sample size: n 25 -> 100 halves the SE (0.0356 -> 0.0174); doubling the noise doubles it (0.0713)",
                   abs(se25 - 0.0356) < 5e-4 and abs(se100 - 0.0174) < 5e-4 and abs(se_noisy / se25 - 2.0) < 0.05))

    X, yy = L.farm_dataset()
    beta = np.linalg.lstsq(X, yy, rcond=None)[0]
    checks.append(("mini-project: coefficients 0.965, 0.300, 0.093, -0.061", np.allclose(beta, [0.965, 0.300, 0.093, -0.061], atol=2e-3)))
    aud = L.farm_audit(X, yy)
    checks.append(("audit (6-fold RMSE t/ha): mean 0.724, rain only 0.440, three inputs 0.343, too flexible 0.381",
                   abs(aud["mean only"] - 0.724) < 2e-3 and abs(aud["rain only"] - 0.440) < 2e-3 and abs(aud["three inputs"] - 0.343) < 2e-3 and abs(aud["too flexible"] - 0.381) < 2e-3))
    yh, lo, hi = L.prediction_interval_multi(X, yy, np.array([1.0, 5.5, 6.0, 25.0]))
    checks.append(("next season (550 mm, 60 kg/ha, 25 C): 1.64 t/ha, 95 percent interval 0.95 to 2.32", abs(yh - 1.64) < 0.01 and abs(lo - 0.95) < 0.01 and abs(hi - 2.32) < 0.01))
    checks.append(("training RMSE is about 0.32 at degree 3 and test RMSE at degree 12 is 5.1", abs(tr[3] - 0.32) < 0.01 and abs(te[12] - 5.1) < 0.05))
    sd = np.sqrt(2.0 / 3.0)
    m6 = L.ridge_fit(F, y, 6.0)
    checks.append(("question B: lambda = 6 gives raw slope 2.5 / 3 = 0.833", abs(m6["beta"][0] / sd - 0.8333) < 1e-3))
    zr, yr = np.round(zt, 4), np.round(yt, 4)

    def app_numbers(d, ll):
        m = L.ridge_fit(L.poly_features(zr, d), yr, 10.0 ** ll)
        f = lambda t: L.ridge_predict(m, L.poly_features(t, d))
        return L.rmse(yr, f(zr)), L.expected_test_rmse(f)
    o, t9 = app_numbers(9, -4), app_numbers(9, -1)
    checks.append(("app: degree 9 gives train 0.250 and expected test 0.832 at log10 lambda -4, train 0.291 and test 0.357 at -1",
                   abs(o[0] - 0.250) < 2e-3 and abs(o[1] - 0.832) < 3e-3 and abs(t9[0] - 0.291) < 2e-3 and abs(t9[1] - 0.357) < 2e-3))
    checks.append(("app challenge range: degree 9 with log10 lambda -1 and -0.5 keeps expected test below 0.4",
                   app_numbers(9, -1)[1] < 0.4 and app_numbers(9, -0.5)[1] < 0.4))
    checks.append(("ridge never sets a coefficient exactly to zero (milestone baseline)", np.count_nonzero(L.ridge_fit(L.poly_features(zt, 9), yt, 0.1)["beta"] == 0) == 0))
    checks.append(("mini-project R squared is 0.797", abs(1 - np.sum((yy - X @ beta) ** 2) / np.sum((yy - yy.mean()) ** 2) - 0.797) < 5e-4))
    rng = np.random.default_rng(3)
    xs = rng.uniform(3, 9, 200)
    ys = 1 + 0.35 * xs + rng.normal(0, 0.3, 200)
    a_, b_ = L.ols_line(xs, ys)
    xn = rng.uniform(3, 9, 20000)
    yn = 1 + 0.35 * xn + rng.normal(0, 0.3, 20000)
    frac = float(np.mean(yn < a_ + b_ * xn))
    checks.append((f"milestone baseline: the least-squares line has {frac:.2f} of fresh seasons below it", abs(frac - 0.51) < 0.01))
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
