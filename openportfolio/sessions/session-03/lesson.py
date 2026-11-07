"""Session 3 (Level 3): many assets, the efficient frontier, and what can go wrong.

General education only, not investment advice. All assets are synthetic; the returns are
made up. Models like this do not predict real markets.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: N assets, the frontier, and the limits of diversification
# **A. Real-world problem.** Session 2 mixed two assets. A real portfolio may hold dozens.
# Three questions follow. (1) If I add more and more assets, does the risk keep falling to
# zero? (2) With several assets, which mixes give the least risk for a chosen return, and which
# mix has the best return per unit of risk? (3) Those answers are computed from numbers
# *estimated* from a short history. How much should we trust them?
#
# **Safety note.** Everything here is synthetic. The four assets, their returns and their
# correlations are made up. This is NOT investment advice, and models like this one do not
# predict real markets: real returns have fat tails, correlations change, and past performance
# does not predict the future.
#
# **Plan.** (1) N equal-weight assets with a common correlation, (2) the covariance matrix and
# the efficient frontier for 4 assets, (3) the Sharpe ratio and the tangency portfolio,
# (4) estimation error, (5) two failure cases.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: N equal-weight assets with a common correlation
# Every asset has standard deviation s and every pair has correlation rho. With weights 1/N,
# the variance of the portfolio is
#
#     var = s^2 * (1/N + (1 - 1/N) * rho)
#
# The first part, s^2/N, is the *idiosyncratic* risk (each asset's own wobble): it shrinks as N
# grows. The second part tends to s^2 * rho, the *market* risk shared by all: no number of
# assets removes it. We check the formula with a covariance matrix and with a simulation in
# which every asset = a shared market part + its own part.

# %%
def equal_weight_var(n, s, rho):
    return s ** 2 * (1.0 / n + (1.0 - 1.0 / n) * rho)


def equal_weight_var_matrix(n, s, rho):
    """Same quantity from w' Sigma w, with Sigma built entry by entry."""
    sigma = np.full((n, n), rho * s * s)
    np.fill_diagonal(sigma, s * s)
    w = np.full(n, 1.0 / n)
    return float(w @ sigma @ w)


def simulate_equal_weight_std(n, s, rho, years=200000, seed=5):
    """Std of the equal-weight portfolio of n simulated assets: asset = s*(sqrt(rho)*market + sqrt(1-rho)*own)."""
    rng = np.random.default_rng(seed)
    market = rng.standard_normal(years)
    own = rng.standard_normal((years, n))
    assets = s * (np.sqrt(rho) * market[:, None] + np.sqrt(1 - rho) * own)
    return float(np.std(assets.mean(axis=1)))


def market_floor(s, rho):
    """The risk that remains however many assets we add: s * sqrt(rho)."""
    return s * np.sqrt(rho)


# %% [markdown]
# ## Step 2: four made-up assets and their covariance matrix
# With several assets we keep the means in a list `mu`, the standard deviations in `sd` and the
# correlations in a table `CORR`. The covariance matrix is Sigma[i][j] = corr[i][j] sd[i] sd[j].
# A covariance matrix must be *positive definite* (every portfolio has positive variance); we
# check that all its eigenvalues are above zero.

# %%
NAMES = ["A", "B", "C", "D"]
MU = np.array([0.06, 0.08, 0.10, 0.12])
SD = np.array([0.10, 0.15, 0.20, 0.25])
CORR = np.array([[1.0, 0.3, 0.2, 0.1],
                 [0.3, 1.0, 0.4, 0.3],
                 [0.2, 0.4, 1.0, 0.5],
                 [0.1, 0.3, 0.5, 1.0]])
RF = 0.02                 # a made-up risk-free rate for the Sharpe ratio


def covariance(sd, corr):
    return corr * np.outer(sd, sd)


SIGMA = covariance(SD, CORR)


def is_positive_definite(sigma):
    return bool(np.all(np.linalg.eigvalsh(sigma) > 1e-12))


def port_stats(w, mu, sigma):
    """Expected return and risk (std) of weights w."""
    return float(w @ mu), float(np.sqrt(w @ sigma @ w))


# %% [markdown]
# ## Step 3: the efficient frontier
# For a target return m, which weights (summing to 1) give the smallest variance? Lagrange
# multipliers give a closed form. With inv = Sigma^-1 and a vector of ones `one`:
#
#     A = one' inv one,  B = one' inv mu,  C = mu' inv mu,  D = A C - B^2
#     w(m) = inv (lam one + gam mu),  lam = (C - B m)/D,  gam = (A m - B)/D
#     var(m) = (A m^2 - 2 B m + C) / D
#
# The weights here may be negative (short selling) - that is what "closed form" allows.
# The least-risk portfolio of all (any return) is w = inv one / A.

# %%
def frontier_constants(mu, sigma):
    inv = np.linalg.inv(sigma)
    one = np.ones(len(mu))
    a = float(one @ inv @ one)
    b = float(one @ inv @ mu)
    c = float(mu @ inv @ mu)
    return inv, a, b, c, a * c - b * b


def frontier_weights(m, mu, sigma):
    inv, a, b, c, d = frontier_constants(mu, sigma)
    one = np.ones(len(mu))
    lam, gam = (c - b * m) / d, (a * m - b) / d
    return inv @ (lam * one + gam * mu)


def frontier_var(m, mu, sigma):
    _, a, b, c, d = frontier_constants(mu, sigma)
    return (a * m * m - 2 * b * m + c) / d


def min_variance_weights(sigma):
    inv = np.linalg.inv(sigma)
    x = inv @ np.ones(len(sigma))
    return x / x.sum()


def random_portfolios(n, n_assets=4, seed=3):
    """Random long-only weights (each row sums to 1)."""
    return np.random.default_rng(seed).dirichlet(np.ones(n_assets), size=n)


# %% [markdown]
# ## Step 4: Sharpe ratio and the tangency portfolio
# The Sharpe ratio is the extra return above the risk-free rate per unit of risk:
# (return - rf) / risk. The portfolio with the highest Sharpe ratio (the *tangency* portfolio)
# has weights proportional to inv (mu - rf one), scaled to sum to 1. Its Sharpe ratio is
# sqrt((mu - rf)' inv (mu - rf)).

# %%
def sharpe(w, mu, sigma, rf=RF):
    r, s = port_stats(w, mu, sigma)
    return (r - rf) / s


def tangency_weights(mu, sigma, rf=RF):
    x = np.linalg.solve(sigma, mu - rf)
    return x / x.sum()


def max_sharpe(mu, sigma, rf=RF):
    ex = mu - rf
    return float(np.sqrt(ex @ np.linalg.solve(sigma, ex)))


# %% [markdown]
# ## Step 5: estimation error
# In real life nobody knows mu and Sigma. We estimate them from T past periods, then build the
# "optimal" portfolio from the estimates. We can test this honestly only in a simulation where
# we *do* know the truth: draw T periods from the true model, estimate, optimise, then measure
# the portfolio's risk under the true Sigma (out-of-sample) and compare with the risk the
# estimate predicted (in-sample).

# %%
def draw_sample(t, mu, sigma, seed):
    """t periods of correlated returns: mu + z L', where L L' = Sigma (Cholesky) and z is standard normal."""
    rng = np.random.default_rng(seed)
    return mu + rng.standard_normal((t, len(mu))) @ np.linalg.cholesky(sigma).T


def estimation_experiment(t, reps, mu=MU, sigma=SIGMA, seed=11):
    """Average over `reps` samples of length t: predicted risk, true risk and true Sharpe
    of the estimated minimum-variance and maximum-Sharpe portfolios."""
    rng = np.random.default_rng(seed)
    chol = np.linalg.cholesky(sigma).T
    pred, true, tsh, psh = [], [], [], []
    for _ in range(reps):
        x = mu + rng.standard_normal((t, len(mu))) @ chol
        mu_hat, sig_hat = x.mean(axis=0), np.cov(x.T)
        w = min_variance_weights(sig_hat)
        pred.append(np.sqrt(w @ sig_hat @ w))
        true.append(np.sqrt(w @ sigma @ w))
        v = tangency_weights(mu_hat, sig_hat)
        psh.append(sharpe(v, mu_hat, sig_hat))
        tsh.append(sharpe(v, mu, sigma))
    return {"pred_risk": float(np.mean(pred)), "true_risk": float(np.mean(true)),
            "pred_sharpe": float(np.mean(psh)), "true_sharpe": float(np.mean(tsh))}


# %% [markdown]
# ## Step 6: two failure cases
# 1. **Correlations rise in a crisis.** The same N assets with a higher rho have a higher
#    floor s * sqrt(rho): the benefit shrinks just when it is needed.
# 2. **Near-singular covariance.** If one asset is almost a copy of another, `inv` becomes
#    huge, and the "optimal" weights explode into big long and short positions that nobody
#    should trust. `near_clone_sigma` makes asset D follow asset C closely with a small
#    independent part `eps`. We then nudge D's mean return by half a percentage point and
#    watch the tangency weights jump.

# %%
def near_clone_sigma(eps, sigma=SIGMA, sd=SD):
    """Covariance where asset D = (sd_D / sd_C) * asset C plus an independent part of std eps."""
    s = sigma.copy()
    k = sd[3] / sd[2]
    s[3, :3] = k * s[2, :3]
    s[:3, 3] = s[3, :3]
    s[3, 3] = k * k * s[2, 2] + eps ** 2
    return s


def condition_number(sigma):
    return float(np.linalg.cond(sigma))


def nudged_mu(delta=0.005):
    """The same mean returns, but asset D's mean raised by delta (0.005 = half a percentage point):
    the kind of small change that estimation error causes."""
    return MU + np.array([0.0, 0.0, 0.0, delta])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    s_, rho_ = 0.20, 0.3
    print("N equal-weight, s=0.20, rho=0.3:")
    for n in (1, 2, 4, 10, 100, 1000):
        print(f"  N={n:5d}: std formula {np.sqrt(equal_weight_var(n, s_, rho_)):.4f}")
    for n in (1, 2, 4, 10):
        print(f"  N={n:2d}: matrix {np.sqrt(equal_weight_var_matrix(n, s_, rho_)):.4f}  "
              f"simulated {simulate_equal_weight_std(n, s_, rho_):.4f}")
    print(f"  floor s*sqrt(rho) = {market_floor(s_, rho_):.4f}; N=10 at rho 0.8: "
          f"{np.sqrt(equal_weight_var(10, s_, 0.8)):.4f}")
    print("eigenvalues of Sigma:", np.round(np.linalg.eigvalsh(SIGMA), 5), "PD:", is_positive_definite(SIGMA))

    wmv = min_variance_weights(SIGMA)
    print("min-variance weights", np.round(wmv, 4), "ret/risk", np.round(port_stats(wmv, MU, SIGMA), 4))
    wt = tangency_weights(MU, SIGMA)
    print("tangency weights", np.round(wt, 4), "ret/risk", np.round(port_stats(wt, MU, SIGMA), 4),
          "sharpe", round(sharpe(wt, MU, SIGMA), 4), "max_sharpe", round(max_sharpe(MU, SIGMA), 4))
    for m in (0.08, 0.10):
        w = frontier_weights(m, MU, SIGMA)
        print(f"frontier at m={m}: weights {np.round(w, 4)} sum {w.sum():.6f} risk {np.sqrt(frontier_var(m, MU, SIGMA)):.4f}")
    rp = random_portfolios(5000)
    rr = rp @ MU
    rs = np.sqrt(np.einsum("ij,jk,ik->i", rp, SIGMA, rp))
    gap = rs - np.sqrt(frontier_var(rr, MU, SIGMA))
    print("random portfolios: min gap to frontier", gap.min(), "best sharpe", ((rr - RF) / rs).max())

    for t in (12, 24, 60, 240):
        e = estimation_experiment(t, 1000)
        print(f"T={t}: predicted risk {e['pred_risk']:.4f}, true risk {e['true_risk']:.4f}, "
              f"min possible {np.sqrt(wmv @ SIGMA @ wmv):.4f}; "
              f"Sharpe predicted {e['pred_sharpe']:.3f} true {e['true_sharpe']:.3f} best {max_sharpe(MU, SIGMA):.3f}")
    for eps in (0.1, 0.05, 0.01, 0.001):
        sg = near_clone_sigma(eps)
        print(f"near clone eps={eps}: cond {condition_number(sg):.3g} tangency {np.round(tangency_weights(MU, sg), 2)} "
              f"nudged {np.round(tangency_weights(nudged_mu(), sg), 2)}")

    # figures
    ns = np.arange(1, 101)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for rho, c in [(0.1, "#2a9d8f"), (0.3, "#e0a030"), (0.8, "#d9534f")]:
        ax.plot(ns, 100 * np.sqrt(equal_weight_var(ns, s_, rho)), color=c, label=f"rho = {rho}")
        ax.axhline(100 * market_floor(s_, rho), color=c, ls=":")
    ax.plot([1, 2, 5, 10, 25, 50], [100 * simulate_equal_weight_std(n, s_, 0.3) for n in (1, 2, 5, 10, 25, 50)],
            "ko", ms=4, label="simulation (rho = 0.3)")
    ax.set_xlabel("number of assets N (equal weights)")
    ax.set_ylabel("portfolio risk, std (%)")
    ax.set_title("Risk falls with N, but stops at the market floor (dotted)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "diversification_vs_n.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.4))
    ax2.scatter(100 * rs, 100 * rr, s=4, alpha=0.35, color="#888888", label="5000 random long-only mixes")
    ms = np.linspace(0.04, 0.16, 100)
    ax2.plot(100 * np.sqrt(frontier_var(ms, MU, SIGMA)), 100 * ms, color="#2a6fdb", lw=2, label="efficient frontier")
    ax2.plot(100 * SD, 100 * MU, "ks")
    for nm, sd_, mu_ in zip(NAMES, SD, MU):
        ax2.annotate(nm, (100 * sd_, 100 * mu_), textcoords="offset points", xytext=(6, -4))
    ax2.plot(*(100 * np.array(port_stats(wt, MU, SIGMA))[::-1]), "r*", ms=12, label="max Sharpe")
    ax2.plot(*(100 * np.array(port_stats(wmv, MU, SIGMA))[::-1]), "g^", ms=8, label="min variance")
    ax2.set_xlabel("risk, std of yearly return (%)")
    ax2.set_ylabel("expected yearly return (%)")
    ax2.set_title("No random mix beats the frontier")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "efficient_frontier.png", dpi=120)

    ts = [12, 24, 36, 60, 120, 240]
    res = [estimation_experiment(t, 600) for t in ts]
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.2))
    ax3.plot(ts, [100 * r_["pred_risk"] for r_ in res], "o-", label="risk the estimate predicted (in-sample)")
    ax3.plot(ts, [100 * r_["true_risk"] for r_ in res], "s-", label="risk the portfolio really has (out-of-sample)")
    ax3.axhline(100 * np.sqrt(wmv @ SIGMA @ wmv), color="gray", ls=":", label="best possible (true minimum)")
    ax3.set_xscale("log")
    ax3.set_xlabel("length of the history T (periods)")
    ax3.set_ylabel("portfolio risk, std (%)")
    ax3.set_title("A short history makes the portfolio look safer than it is")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "estimation_error.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The model assumes bell-curve returns, fixed correlations and known costs of nothing. It
# ignores trading costs, taxes, and the fact that real correlations jump in a crisis. Better
# estimates (shrinkage), weight limits and robust methods are the road to the Target: see
# `promo/roadmap.md`.
