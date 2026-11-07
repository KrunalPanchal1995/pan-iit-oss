"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    indep = L.loss_probability(0.0)
    # --- reproduces Session 3
    s0 = L.summarize(L.simulate_profit_corr(0.0))
    checks.append(("rho = 0 reproduces Session 3: loss 9.5 percent, mean $476.4, standard deviation $374.9",
                   abs(s0["loss"] - 0.095) < 1e-9 and abs(s0["mean"] - 476.4) < 0.1 and abs(s0["std"] - 374.9) < 0.1))
    checks.append(("seeded run: the same numbers every time", L.summarize(L.simulate_profit_corr(-0.5)) == L.summarize(L.simulate_profit_corr(-0.5))))
    # --- roadmap checkpoint
    neg = L.loss_probability(-0.5)
    checks.append((f"roadmap check: with correlation -0.5 the loss probability is {100 * neg:.1f} percent against {100 * indep:.1f} percent independent, at least 2 points lower",
                   indep - neg >= 0.02 and abs(neg - 0.0559) < 0.001))
    ok_seeds = all(L.loss_probability(0.0, seed=s) - L.loss_probability(-0.5, seed=s) >= 0.02 for s in range(1, 8))
    checks.append(("the 2-point difference is not a lucky seed: it holds for seeds 1 to 7", ok_seeds))
    pos = L.loss_probability(0.5)
    checks.append((f"positive correlation raises the risk: +0.5 gives {100 * pos:.1f} percent, more than the independent {100 * indep:.1f}",
                   pos - indep >= 0.02 and abs(pos - 0.124) < 0.001))
    ls = [x for _, x in L.loss_vs_rho()]
    checks.append(("the loss probability rises step by step with the correlation from -0.9 (2.6 percent) to +0.9 (14.4 percent)",
                   all(b > a for a, b in zip(ls, ls[1:])) and abs(ls[0] - 0.0263) < 0.001 and abs(ls[-1] - 0.1436) < 0.001))
    # --- the draws really have the requested correlation
    for rho in (-0.7, 0.0, 0.4):
        _, price, dem = L.simulate_profit_corr(rho, n=100000, inputs=True)
        got = float(np.corrcoef(price, dem)[0, 1])
        checks.append((f"validation: the sample correlation of price and demand is {got:+.3f} for rho = {rho:+.1f}", abs(got - rho) < 0.01))
    _, price, dem = L.simulate_profit_corr(-0.5, n=100000, inputs=True)
    checks.append(("each input keeps its own mean and spread: price 3.50 and 0.20, demand 800 and 150",
                   abs(price.mean() - 3.5) < 0.01 and abs(price.std() - 0.2) < 0.005 and abs(dem.mean() - 800) < 2.0 and abs(dem.std() - 150) < 2.0))
    # --- formulas
    worst_m, worst_s = 0.0, 0.0
    for rho in (-0.9, -0.5, 0.0, 0.5, 0.9):
        pr = L.simulate_profit_corr(rho, n=200000)
        worst_m = max(worst_m, abs(pr.mean() - L.profit_mean_formula(rho)))
        worst_s = max(worst_s, abs(pr.std() / L.profit_std_formula(rho) - 1.0))
    checks.append((f"validation: simulated mean profit is within $3 of the formula (worst ${worst_m:.2f})", worst_m < 3.0))
    checks.append((f"validation: simulated standard deviation is within 1 percent of the exact formula (worst {100 * worst_s:.2f} percent)", worst_s < 0.01))
    checks.append(("worked example: rho = -0.5 gives mean $465.0 and standard deviation $300.8 by hand",
                   abs(L.profit_mean_formula(-0.5) - 465.0) < 1e-9 and abs(L.profit_std_formula(-0.5) - 300.8) < 0.05))
    checks.append(("the correlation moves the mean by only rho x 0.20 x 150 = 30 dollars per unit of rho",
                   abs((L.profit_mean_formula(1.0) - L.profit_mean_formula(0.0)) - 30.0) < 1e-9))
    s, s_0, diff = L.decompose_spread(-0.5)
    checks.append((f"a negative correlation shrinks the spread: ${s:.1f} against ${s_0:.1f} ({diff:.1f})", s < s_0 and abs(diff + 74.2) < 0.2))
    approx = L.loss_normal_approx(-0.5)
    checks.append((f"the normal shortcut Phi(-mean/std) gives {100 * approx:.1f} percent for rho = -0.5, within 1 point of the simulation but a little high (skewed profit)",
                   abs(approx - neg) < 0.01 and approx > neg))
    # --- implied correlation and the lender's limit
    ir = L.implied_rho()
    checks.append((f"the demand line of Session 2 implies a correlation of {ir:.3f} (-250 x 0.20 / 150)", abs(ir + 1.0 / 3.0) < 1e-9))
    checks.append(("limit: a demand line steeper than the whole demand spread is rejected", _raises(lambda: L.implied_rho(d_sd=40.0))))
    li = L.loss_probability(ir)
    checks.append((f"at the implied correlation the loss probability is {100 * li:.1f} percent, between the independent and the -0.5 value", neg < li < indep))
    r8 = L.rho_for_limit(0.08)
    checks.append((f"mini-project: the largest correlation with a loss probability of at most 8 percent is {r8:.3f}",
                   r8 is not None and abs(r8 + 0.189) < 0.01 and L.loss_probability(r8) <= 0.08 < L.loss_probability(r8 + 0.01)))
    checks.append(("mini-project: an 8 percent limit holds at the implied correlation and fails when the inputs are independent",
                   L.loss_probability(ir) <= 0.08 and indep > 0.08))
    checks.append(("edge: no correlation can reach a 1 percent limit, and every correlation meets a 20 percent limit",
                   L.rho_for_limit(0.01) is None and L.rho_for_limit(0.20) == 0.99))
    # --- limits and edges
    checks.append(("limit: a correlation outside -1 to +1 is rejected", _raises(lambda: L.simulate_profit_corr(1.2)) and _raises(lambda: L.simulate_profit_corr(-1.01))))
    pr1 = L.simulate_profit_corr(-1.0, n=50000, inputs=True)
    checks.append(("edge: correlation -1 puts every draw exactly on one line (demand falls 750 loaves per dollar of price)",
                   abs(float(np.corrcoef(pr1[1], pr1[2])[0, 1]) + 1.0) < 1e-9 and abs(float(np.polyfit(pr1[1], pr1[2], 1)[0]) + 750.0) < 1.0))
    checks.append(("limit: with no randomness at all the profit is exactly $480 every month",
                   np.allclose(L.simulate_profit_corr(0.5, n=50, p_sd=0, v_sd=0, d_sd=0), 480.0)))
    checks.append(("a price that matches the variable cost with certain demand gives a loss of exactly the fixed cost",
                   np.allclose(L.simulate_profit_corr(0.0, n=20, p_mu=1.4, p_sd=0, v_sd=0, d_sd=0), -1200.0)))
    return checks


def _raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


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
