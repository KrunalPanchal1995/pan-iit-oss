"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # ---- N equal-weight assets, common correlation
    s = 0.20
    ok = all(abs(L.equal_weight_var(n, s, q) - L.equal_weight_var_matrix(n, s, q)) < 1e-12
             for n in (1, 2, 4, 10, 50) for q in (0.0, 0.3, 0.8, 1.0))
    checks.append(("N equal weights: the formula s^2 (1/N + (1 - 1/N) rho) equals w' Sigma w from a matrix", ok))
    sim_ok = all(abs(L.simulate_equal_weight_std(n, s, 0.3) - np.sqrt(L.equal_weight_var(n, s, 0.3))) < 0.001 for n in (1, 2, 4, 10))
    checks.append(("a seeded simulation (200000 years) agrees with the formula within 0.001 for N = 1, 2, 4, 10", sim_ok))
    checks.append(("the simulated N = 4 portfolio (seed 5, 200000 years) has risk 0.1380",
                   abs(L.simulate_equal_weight_std(4, s, 0.3) - 0.1380) < 5e-5))
    # worked example: N = 4, s = 0.2, rho = 0.3: variance 0.019, std 0.1378
    checks.append(("worked example: N = 4, s = 0.20, rho = 0.3 gives variance 0.0190 and std 0.1378 (31% below one asset)",
                   abs(L.equal_weight_var(4, 0.2, 0.3) - 0.04 * (0.25 + 0.75 * 0.3)) < 1e-15
                   and abs(L.equal_weight_var(4, 0.2, 0.3) - 0.019) < 1e-12
                   and abs(np.sqrt(L.equal_weight_var(4, 0.2, 0.3)) - 0.1378) < 5e-5
                   and abs(1 - np.sqrt(L.equal_weight_var(4, 0.2, 0.3)) / 0.2 - 0.31) < 0.005))
    checks.append(("the risk falls with N: 0.2000 (N=1), 0.1612 (2), 0.1217 (10), 0.1108 (100) at rho = 0.3",
                   all(abs(np.sqrt(L.equal_weight_var(n, s, 0.3)) - v) < 5e-5 for n, v in ((1, 0.2), (2, 0.1612), (10, 0.1217), (100, 0.1108)))))
    floor = L.market_floor(s, 0.3)
    checks.append(("the market floor s sqrt(rho) is 0.1095, and a million assets get within 1e-4 of it, never below",
                   abs(floor - 0.1095) < 5e-5 and 0 <= np.sqrt(L.equal_weight_var(10 ** 6, s, 0.3)) - floor < 1e-4
                   and all(np.sqrt(L.equal_weight_var(n, s, 0.3)) > floor for n in (1, 10, 100, 1000))))
    checks.append(("edge: rho = 0 gives s^2/N (risk vanishes as 1/sqrt(N)); rho = 1 gives s^2 for every N (no benefit)",
                   all(abs(L.equal_weight_var(n, s, 0.0) - s * s / n) < 1e-15 and abs(L.equal_weight_var(n, s, 1.0) - s * s) < 1e-15 for n in (1, 5, 50))))
    r3, r8 = np.sqrt(L.equal_weight_var(10, s, 0.3)), np.sqrt(L.equal_weight_var(10, s, 0.8))
    checks.append(("failure case: with N = 10, raising rho from 0.3 to 0.8 raises the risk from 0.1217 to 0.1811 and cuts the benefit from 39% to 9%",
                   abs(r3 - 0.1217) < 5e-5 and abs(r8 - 0.1811) < 5e-5
                   and abs((1 - r3 / s) - 0.39) < 0.005 and abs((1 - r8 / s) - 0.09) < 0.005))

    checks.append(("hand calculation: N = 10, s = 0.20, rho = 0.3 gives variance 0.0148 (0.04 * 0.37)",
                   abs(L.equal_weight_var(10, 0.2, 0.3) - 0.0148) < 1e-12))
    n_need = next(n for n in range(1, 200) if np.sqrt(L.equal_weight_var(n, 0.2, 0.3)) <= 0.12)
    checks.append(("design: risk <= 12% at rho = 0.3 needs N = 12 (0.1197; N = 11 gives 0.1206), and rho = 0.5 is impossible (floor 0.1414)",
                   n_need == 12 and abs(np.sqrt(L.equal_weight_var(12, 0.2, 0.3)) - 0.1197) < 5e-5
                   and abs(np.sqrt(L.equal_weight_var(11, 0.2, 0.3)) - 0.1206) < 5e-5 and abs(L.market_floor(0.2, 0.5) - 0.1414) < 5e-5))

    # ---- covariance matrix
    sig = L.SIGMA
    ev = np.linalg.eigvalsh(sig)
    checks.append(("Sigma is symmetric and positive definite (smallest eigenvalue 0.00851)",
                   np.allclose(sig, sig.T) and L.is_positive_definite(sig) and abs(ev.min() - 0.00851) < 5e-6))
    np.linalg.cholesky(sig)
    bad = np.array([[1, 0.9, -0.9], [0.9, 1, 0.9], [-0.9, 0.9, 1.0]])
    checks.append(("edge: an impossible correlation table (0.9, 0.9, -0.9) is rejected as not positive definite",
                   not L.is_positive_definite(bad) and L.is_positive_definite(np.eye(3))))
    checks.append(("Sigma diagonal equals sd^2 and the correlations are recovered",
                   np.allclose(np.diag(sig), L.SD ** 2) and np.allclose(sig / np.outer(L.SD, L.SD), L.CORR)))

    # ---- frontier
    wmv = L.min_variance_weights(sig)
    rmv, smv = L.port_stats(wmv, L.MU, sig)
    checks.append(("minimum-variance portfolio: weights 0.7232, 0.1723, 0.0515, 0.0530; return 0.0687; risk 0.0914; weights sum to 1",
                   np.allclose(wmv, [0.7232, 0.1723, 0.0515, 0.0530], atol=5e-5) and abs(wmv.sum() - 1) < 1e-12
                   and abs(rmv - 0.0687) < 5e-5 and abs(smv - 0.0914) < 5e-5))
    ok = True
    for m in (0.07, 0.08, 0.10, 0.12):
        w = L.frontier_weights(m, L.MU, sig)
        ok &= abs(w.sum() - 1) < 1e-12 and abs(w @ L.MU - m) < 1e-12 and abs(w @ sig @ w - L.frontier_var(m, L.MU, sig)) < 1e-12
    checks.append(("frontier weights sum to 1, hit the target return, and have the variance given by the closed form", ok))
    w8 = L.frontier_weights(0.08, L.MU, sig)
    w10 = L.frontier_weights(0.10, L.MU, sig)
    checks.append(("frontier at 8% return: weights 0.4832, 0.2087, 0.1329, 0.1752 and risk 0.1022; at 10%: risk 0.1561",
                   np.allclose(w8, [0.4832, 0.2087, 0.1329, 0.1752], atol=5e-5)
                   and abs(np.sqrt(L.frontier_var(0.08, L.MU, sig)) - 0.1022) < 5e-5
                   and abs(np.sqrt(L.frontier_var(0.10, L.MU, sig)) - 0.1561) < 5e-5 and w10.min() > 0))
    b = (np.ones(4) @ np.linalg.solve(sig, L.MU)) / (np.ones(4) @ np.linalg.solve(sig, np.ones(4)))
    checks.append(("the frontier at the minimum-variance return B/A is the minimum-variance portfolio",
                   np.allclose(L.frontier_weights(b, L.MU, sig), wmv, atol=1e-10)))
    rp = L.random_portfolios(5000)
    rr = rp @ L.MU
    rs = np.sqrt(np.einsum("ij,jk,ik->i", rp, sig, rp))
    gap = rs - np.sqrt(L.frontier_var(rr, L.MU, sig))
    checks.append(("5000 random long-only portfolios: none has less risk than the frontier at its own return",
                   bool(np.all(rp >= 0)) and np.allclose(rp.sum(axis=1), 1) and gap.min() > -1e-12))
    rng = np.random.default_rng(0)
    ok = True
    for _ in range(200):
        d = rng.standard_normal(4)
        d -= np.ones(4) * d.mean()                          # keep the weights summing to 1
        w = w8 + 0.05 * d
        ok &= w @ sig @ w >= L.frontier_var(w @ L.MU, L.MU, sig) - 1e-12
    checks.append(("random nudges of the frontier weights (weights summing to 1, any shorts) never beat the frontier at their own return", ok))

    # ---- Sharpe and tangency
    wt = L.tangency_weights(L.MU, sig)
    checks.append(("tangency portfolio: weights 0.5006, 0.2061, 0.1270, 0.1664; return 0.0792; risk 0.1007; Sharpe 0.5876",
                   np.allclose(wt, [0.5006, 0.2061, 0.1270, 0.1664], atol=5e-5) and abs(wt.sum() - 1) < 1e-12
                   and abs(L.port_stats(wt, L.MU, sig)[0] - 0.0792) < 5e-5 and abs(L.port_stats(wt, L.MU, sig)[1] - 0.1007) < 5e-5
                   and abs(L.sharpe(wt, L.MU, sig) - 0.5876) < 5e-5))
    checks.append(("the closed-form maximum Sharpe ratio sqrt((mu-rf)' inv (mu-rf)) equals the tangency portfolio's Sharpe",
                   abs(L.max_sharpe(L.MU, sig) - L.sharpe(wt, L.MU, sig)) < 1e-12))
    best_random = float(((rr - L.RF) / rs).max())
    checks.append(("no random portfolio beats the tangency Sharpe ratio (best random 0.5875 against 0.5876)",
                   best_random <= L.max_sharpe(L.MU, sig) + 1e-12 and abs(best_random - 0.5875) < 5e-5))
    checks.append(("each single asset has Sharpe ratio 0.4000, lower than the tangency mix (0.5876)",
                   all(abs(L.sharpe(np.eye(4)[i], L.MU, sig) - 0.4) < 1e-12 for i in range(4))
                   and 0.4 < L.max_sharpe(L.MU, sig)))

    stress = L.covariance(L.SD, np.where(np.eye(4) == 1, 1.0, 0.8))
    checks.append(("stress test (all correlations 0.8): the minimum-variance portfolio has risk 0.1144 (from 0.0914), the tangency portfolio 0.1367 (from 0.1007)",
                   abs(np.sqrt(wmv @ stress @ wmv) - 0.1144) < 5e-5 and abs(np.sqrt(wt @ stress @ wt) - 0.1367) < 5e-5
                   and L.is_positive_definite(stress)))
    contrib = wmv * (sig @ wmv) / (wmv @ sig @ wmv)
    checks.append(("risk contributions of the minimum-variance portfolio equal its weights: asset A carries 72% of the risk",
                   np.allclose(contrib, wmv, atol=1e-12) and abs(contrib[0] - 0.72) < 0.005))

    # ---- estimation error
    res = {t: L.estimation_experiment(t, 1000) for t in (12, 24, 60, 240)}
    checks.append(("estimation error T = 24: predicted risk 0.0847, true risk 0.0982, best possible 0.0914",
                   abs(res[24]["pred_risk"] - 0.0847) < 1e-4 and abs(res[24]["true_risk"] - 0.0982) < 1e-4 and abs(smv - 0.0914) < 5e-5))
    checks.append(("estimation error T = 12: predicted 0.0753 against true 0.1080; T = 60: 0.0887 against 0.0938; T = 240: 0.0906 against 0.0919",
                   abs(res[12]["pred_risk"] - 0.0753) < 1e-4 and abs(res[12]["true_risk"] - 0.1080) < 1e-4
                   and abs(res[60]["pred_risk"] - 0.0887) < 1e-4 and abs(res[60]["true_risk"] - 0.0938) < 1e-4
                   and abs(res[240]["pred_risk"] - 0.0906) < 1e-4 and abs(res[240]["true_risk"] - 0.0919) < 1e-4))
    checks.append(("out-of-sample risk is above the predicted risk and above the true minimum at every T, and the gaps shrink as T grows",
                   all(res[t]["true_risk"] > res[t]["pred_risk"] and res[t]["true_risk"] > smv for t in res)
                   and res[12]["true_risk"] - res[12]["pred_risk"] > res[24]["true_risk"] - res[24]["pred_risk"]
                   > res[60]["true_risk"] - res[60]["pred_risk"] > res[240]["true_risk"] - res[240]["pred_risk"]))
    checks.append(("Sharpe-best portfolio from T = 24: the estimate promises 0.760, the truth is 0.459, the best possible is 0.588",
                   abs(res[24]["pred_sharpe"] - 0.760) < 1e-3 and abs(res[24]["true_sharpe"] - 0.459) < 1e-3
                   and abs(L.max_sharpe(L.MU, sig) - 0.588) < 5e-4))
    x = L.draw_sample(200000, L.MU, sig, 1)
    checks.append(("draw_sample reproduces the target means and covariance (200000 periods, within 0.002)",
                   np.allclose(x.mean(axis=0), L.MU, atol=0.002) and np.allclose(np.cov(x.T), sig, atol=0.002)
                   and np.array_equal(L.draw_sample(10, L.MU, sig, 3), L.draw_sample(10, L.MU, sig, 3))))

    # ---- failure case: near-singular covariance
    s1, s2 = L.near_clone_sigma(0.1), L.near_clone_sigma(0.01)
    w1, w2 = L.tangency_weights(L.nudged_mu(), s1), L.tangency_weights(L.nudged_mu(), s2)
    checks.append(("near-clone assets stay positive definite, but the condition number grows from 31 (eps = 0.1) to 2756 (eps = 0.01)",
                   L.is_positive_definite(s1) and L.is_positive_definite(s2)
                   and abs(L.condition_number(s1) - 31.3) < 0.1 and abs(L.condition_number(s2) - 2756) < 5))
    checks.append(("failure case: nudging D's mean by 0.5 points moves the tangency weights of C and D from 0.12, 0.09 (eps = 0.1) to 8.81, -7.19 (eps = 0.01)",
                   np.allclose(w1[2:], [0.12, 0.09], atol=0.005) and np.allclose(w2[2:], [8.81, -7.19], atol=0.01)
                   and abs(w2.sum() - 1) < 1e-9 and abs(w2).max() > 5))
    checks.append(("without the nudge the tangency weights barely move with eps: 0.51, 0.25, 0.23, 0.00",
                   np.allclose(L.tangency_weights(L.MU, s2), [0.51, 0.25, 0.23, 0.0], atol=0.005)))

    # ---- mini-project data (the numbers printed in the README)
    mu = np.array([0.04, 0.07, 0.09, 0.13])
    sd = np.array([0.08, 0.12, 0.18, 0.30])
    corr = np.array([[1, 0.2, 0.1, 0.0], [0.2, 1, 0.3, 0.2], [0.1, 0.3, 1, 0.6], [0.0, 0.2, 0.6, 1.0]])
    sg = L.covariance(sd, corr)
    wb = L.min_variance_weights(sg)
    vb = L.tangency_weights(mu, sg)
    e = L.estimation_experiment(36, 1000, mu, sg, 21)
    checks.append(("mini-project (made-up set B): positive definite; minimum-variance weights 0.7027, 0.2174, 0.0650, 0.0148 with risk 0.0708",
                   L.is_positive_definite(sg) and np.allclose(wb, [0.7027, 0.2174, 0.0650, 0.0148], atol=5e-5)
                   and abs(L.port_stats(wb, mu, sg)[1] - 0.0708) < 5e-5))
    checks.append(("mini-project: Sharpe-best weights 0.3545, 0.3918, 0.1379, 0.1158 with Sharpe 0.5521",
                   np.allclose(vb, [0.3545, 0.3918, 0.1379, 0.1158], atol=5e-5) and abs(L.sharpe(vb, mu, sg) - 0.5521) < 5e-5))
    checks.append(("mini-project: with T = 36, 1000 samples (seed 21) the predicted risk averages 0.0669 and the true risk 0.0742",
                   abs(e["pred_risk"] - 0.0669) < 1e-4 and abs(e["true_risk"] - 0.0742) < 1e-4 and e["true_risk"] > e["pred_risk"]))
    xs = L.draw_sample(36, mu, sg, 21)
    wh = L.min_variance_weights(np.cov(xs.T))
    checks.append(("mini-project: the single sample with seed 21 gives weights 0.8165, 0.0106, 0.1897, -0.0168 (a short position in D)",
                   np.allclose(wh, [0.8165, 0.0106, 0.1897, -0.0168], atol=5e-4) and wh[3] < 0))
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
