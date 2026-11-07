"""Session 2 (Level 2): return, risk and correlation of a two-asset portfolio.

General education only, not investment advice. Both assets are synthetic.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: return, risk and correlation
# **A. Real-world problem.** Session 1 had shops that were exactly opposite. Real assets are
# only partly opposite. We need numbers: how much does an asset earn on average (its *mean
# return*), how much does it wobble (its *standard deviation*, our measure of risk), and how
# much do two assets move together (their *correlation* rho, between -1 and +1)? Then: how
# should we split money between two assets to get the steadiest result?
#
# **Safety note.** Both assets below are made up (Asset 1: mean 10%, std 20%; Asset 2: mean 6%,
# std 10% per year). Returns are drawn from a seeded random generator. This is a model for
# learning, NOT investment advice; real markets do not follow a fixed bell curve and past
# performance does not predict the future.
#
# **Plan.** (1) simulate returns and measure mean and std, (2) write the two-asset portfolio
# formulas and check them on sampled portfolios, (3) see how rho changes the risk, (4) find the
# minimum-risk weight and check it by scanning.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

MU1, SD1 = 0.10, 0.20     # asset 1: mean and standard deviation of yearly return
MU2, SD2 = 0.06, 0.10     # asset 2


# %% [markdown]
# ## Step 1: simulate returns and measure them
# We draw two bell-curve (normal) numbers z1, z2 for each simulated year, then
#
#     r1 = mu1 + s1 * z1
#     r2 = mu2 + s2 * (rho * z1 + sqrt(1 - rho^2) * z2)
#
# so r1 and r2 have the stated means and standard deviations, and their correlation is rho.
# The mean is the average of the yearly returns; the standard deviation is the typical distance
# of a year from that average.

# %%
def simulate_returns(n, rho, seed=7, mu1=MU1, s1=SD1, mu2=MU2, s2=SD2):
    """n simulated years of (r1, r2), with correlation rho. Seeded: same seed, same numbers."""
    rng = np.random.default_rng(seed)
    z1 = rng.standard_normal(n)
    z2 = rng.standard_normal(n)
    r1 = mu1 + s1 * z1
    r2 = mu2 + s2 * (rho * z1 + np.sqrt(1 - rho ** 2) * z2)
    return np.stack([r1, r2], axis=1)


def mean_std(x):
    return float(np.mean(x)), float(np.std(x))


# %% [markdown]
# ## Step 2: the two-asset portfolio
# Put weight `w` of the money in asset 1 and `1 - w` in asset 2 (both between 0 and 1).
#
#     expected return  = w mu1 + (1 - w) mu2
#     variance         = w^2 s1^2 + (1 - w)^2 s2^2 + 2 w (1 - w) rho s1 s2
#     risk (std)       = sqrt(variance)
#
# The return is just a weighted average, so mixing never changes the average in a surprising
# way. The variance has an extra last term that depends on rho: this is where diversification
# lives.

# %%
def port_return(w, mu1=MU1, mu2=MU2):
    return w * mu1 + (1 - w) * mu2


def port_var(w, rho, s1=SD1, s2=SD2):
    return w ** 2 * s1 ** 2 + (1 - w) ** 2 * s2 ** 2 + 2 * w * (1 - w) * rho * s1 * s2


def port_std(w, rho, s1=SD1, s2=SD2):
    return np.sqrt(port_var(w, rho, s1, s2))


def sampled_portfolio(returns, w):
    """Mean and variance measured on the simulated portfolio returns w r1 + (1 - w) r2."""
    p = w * returns[:, 0] + (1 - w) * returns[:, 1]
    return float(np.mean(p)), float(np.var(p))


# %% [markdown]
# ## Step 3: the effect of correlation
# * rho = +1 (move together): variance = (w s1 + (1 - w) s2)^2, so the risk is just the
#   weighted average of the two risks. No benefit.
# * rho = -1 (exactly opposite): variance = (w s1 - (1 - w) s2)^2. This is zero when
#   w s1 = (1 - w) s2, that is **w = s2 / (s1 + s2)**: the risk can vanish.
# * In between, the lower rho, the lower the risk of the mix.

# %%
def zero_variance_weight(s1=SD1, s2=SD2):
    """Weight in asset 1 that makes the variance zero when rho = -1."""
    return s2 / (s1 + s2)


# %% [markdown]
# ## Step 4: the minimum-variance weight
# Differentiate the variance with respect to w and set it to zero:
#
#     w* = (s2^2 - rho s1 s2) / (s1^2 + s2^2 - 2 rho s1 s2)
#
# The bottom is never zero unless s1 = s2 and rho = 1. We check the formula by scanning
# many weights and picking the smallest variance. Careful: w* may fall outside 0..1 for some
# inputs, which would mean borrowing or short selling; here we only look at 0..1.

# %%
def min_var_weight(rho, s1=SD1, s2=SD2):
    return (s2 ** 2 - rho * s1 * s2) / (s1 ** 2 + s2 ** 2 - 2 * rho * s1 * s2)


def scan_min_var_weight(rho, s1=SD1, s2=SD2, n=100001):
    ws = np.linspace(0.0, 1.0, n)
    return float(ws[np.argmin(port_var(ws, rho, s1, s2))])


def weight_for_return(target, mu1=MU1, mu2=MU2):
    """Weight in asset 1 that gives expected return `target` (solve w mu1 + (1-w) mu2 = target)."""
    return (target - mu2) / (mu1 - mu2)


def max_rho_for_risk(w, risk_limit, s1=SD1, s2=SD2):
    """Largest correlation for which the w-mix has std <= risk_limit (solve the variance for rho)."""
    return (risk_limit ** 2 - w ** 2 * s1 ** 2 - (1 - w) ** 2 * s2 ** 2) / (2 * w * (1 - w) * s1 * s2)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    r = simulate_returns(100000, 0.3)
    for i, name in enumerate(("asset 1", "asset 2")):
        m, s = mean_std(r[:, i])
        print(f"{name}: sample mean {m:.4f}, sample std {s:.4f}")
    print(f"sample correlation {np.corrcoef(r.T)[0, 1]:.4f}")
    for w in (0.0, 0.25, 0.5, 1.0):
        m, v = sampled_portfolio(r, w)
        print(f"w={w:4.2f}: formula return {port_return(w):.4f} std {port_std(w, 0.3):.4f} | "
              f"sampled return {m:.4f} std {np.sqrt(v):.4f}")
    for rho in (1.0, 0.3, 0.0, -0.5, -1.0):
        ws = min_var_weight(rho)
        print(f"rho={rho:5.2f}: w* formula {ws:.4f}, scan {scan_min_var_weight(rho):.4f}, "
              f"std at w* {port_std(np.clip(ws, 0, 1), rho):.4f}")
    wz = zero_variance_weight()
    print(f"rho=-1 zero-variance weight {wz:.4f}: std {port_std(wz, -1.0):.2e}")
    print(f"weight for 7% return {weight_for_return(0.07):.3f}: std at rho 0.3 {port_std(0.25, 0.3):.4f}")
    print(f"max rho for std<=11% at w=0.5: {max_rho_for_risk(0.5, 0.11):.3f}")

    ws = np.linspace(0, 1, 201)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for rho, c in [(1.0, "#d9534f"), (0.3, "#e0a030"), (0.0, "#888888"), (-0.5, "#2a9d8f"), (-1.0, "#2a6fdb")]:
        ax.plot(100 * ws, 100 * port_std(ws, rho), color=c, label=f"rho = {rho:g}")
        wm = np.clip(min_var_weight(rho), 0, 1)
        ax.plot(100 * wm, 100 * port_std(wm, rho), "o", color=c)
    ax.set_xlabel("weight in asset 1 (%)")
    ax.set_ylabel("portfolio risk, std of yearly return (%)")
    ax.set_title("Lower correlation, lower risk (dots: minimum risk)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "risk_vs_weight.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for rho, c in [(1.0, "#d9534f"), (0.3, "#e0a030"), (-0.5, "#2a9d8f"), (-1.0, "#2a6fdb")]:
        ax2.plot(100 * port_std(ws, rho), 100 * port_return(ws), color=c, label=f"rho = {rho:g}")
    ax2.plot(100 * SD1, 100 * MU1, "ks")
    ax2.plot(100 * SD2, 100 * MU2, "ks")
    ax2.annotate("asset 1", (100 * SD1, 100 * MU1), textcoords="offset points", xytext=(-40, -4), fontsize=8)
    ax2.annotate("asset 2", (100 * SD2, 100 * MU2), textcoords="offset points", xytext=(6, -10), fontsize=8)
    ax2.set_xlabel("risk, std of yearly return (%)")
    ax2.set_ylabel("expected yearly return (%)")
    ax2.set_title("The mix bends to the left as rho falls")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "risk_return_curves.png", dpi=120)

# %% [markdown]
# ## Where this stops
# With more than two assets, writing every pair term by hand gets long. Session 3 uses a
# covariance matrix, many assets, and shows what diversification can and cannot remove.
