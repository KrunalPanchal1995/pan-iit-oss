"""Session 4 (Level 3): price and demand that move together.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: when price and demand move together
# **A. Real-world problem.** In Session 3 the bakery's price, variable cost and demand were
# random, but *independent*: a high price said nothing about demand. Real customers do not
# behave like that. When the price is higher than planned, fewer people buy; in a festival week
# a higher price can even come with more buyers. How much does that link change the risk of a
# loss month, even when every average stays the same? Today you add a **correlation** between
# price and demand to the Monte Carlo model, check it against formulas, and ask what correlation
# a lender should believe.
#
# *General education only: the bakery and its numbers are made up, and this is not
# financial advice.*

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

F, P, V, Q = 1200.0, 3.50, 1.40, 800.0          # as in Sessions 2 and 3
P_SD, V_SD, Q_SD = 0.20, 0.15, 150.0            # made-up standard deviations of Session 3
DEMAND_B = 250.0                                # Session 2: loaves per month lost per dollar of price


# %% [markdown]
# ## Step 1: correlated random draws
# The **correlation** rho (a number from -1 to +1) says how two random inputs move together:
# -1 means a high price always comes with low demand, 0 means no link, +1 means they rise
# together. To draw demand with a chosen rho we mix two independent standard normal numbers:
# `z_demand = rho * z_price + sqrt(1 - rho^2) * z_other`. Then the demand is `mean + sd * z_demand`.
# The price and the variable cost are drawn exactly as in Session 3, so with rho = 0 this
# reproduces Session 3 to the last digit.

# %%
def simulate_profit_corr(rho=0.0, n=20000, seed=42, p_mu=P, p_sd=P_SD, v_mu=V, v_sd=V_SD,
                         d_mu=Q, d_sd=Q_SD, fixed=F, inputs=False):
    """Monthly profit of n random months; correlation rho between price and demand (variable cost independent).

    With inputs=True also return the price and demand arrays."""
    if not -1.0 <= rho <= 1.0:
        raise ValueError("the correlation must be between -1 and +1")
    rng = np.random.default_rng(seed)
    z_price = rng.standard_normal(n)
    z_cost = rng.standard_normal(n)
    z_other = rng.standard_normal(n)
    price = p_mu + p_sd * z_price
    vcost = v_mu + v_sd * z_cost
    demand = np.maximum(d_mu + d_sd * (rho * z_price + math.sqrt(1.0 - rho * rho) * z_other), 0.0)
    profit = (price - vcost) * demand - fixed
    return (profit, price, demand) if inputs else profit


def summarize(profits):
    return {"mean": float(np.mean(profits)), "std": float(np.std(profits)),
            "p5": float(np.percentile(profits, 5)), "p50": float(np.percentile(profits, 50)),
            "p95": float(np.percentile(profits, 95)), "loss": float(np.mean(profits < 0))}


def loss_probability(rho, **kw):
    return float(np.mean(simulate_profit_corr(rho, **kw) < 0))


# %% [markdown]
# ## Step 2: formulas to check the simulation against
# Write profit = X * D - F with X = price - variable cost and D = demand. X and D are jointly
# normal, so the mean and the standard deviation of X D have exact formulas (Isserlis' theorem):
# * mean = mu_X mu_D + Cov(X, D) - F, and Cov(X, D) = rho sigma_p sigma_D (the cost is independent),
# * variance = mu_X^2 sigma_D^2 + mu_D^2 sigma_X^2 + 2 mu_X mu_D Cov + sigma_X^2 sigma_D^2 + Cov^2,
#   with sigma_X^2 = sigma_p^2 + sigma_v^2.
# These ignore the rare months where demand would be negative (clipped at 0 in the simulation;
# at 800 with sd 150 that is more than 5 standard deviations away).

# %%
def profit_mean_formula(rho, p_mu=P, p_sd=P_SD, v_mu=V, d_mu=Q, d_sd=Q_SD, fixed=F):
    return (p_mu - v_mu) * d_mu + rho * p_sd * d_sd - fixed


def profit_std_formula(rho, p_mu=P, p_sd=P_SD, v_mu=V, v_sd=V_SD, d_mu=Q, d_sd=Q_SD):
    mu_x, var_x = p_mu - v_mu, p_sd ** 2 + v_sd ** 2
    cov = rho * p_sd * d_sd
    var = mu_x ** 2 * d_sd ** 2 + d_mu ** 2 * var_x + 2.0 * mu_x * d_mu * cov + var_x * d_sd ** 2 + cov ** 2
    return math.sqrt(var)


def loss_normal_approx(rho, **kw):
    """Quick estimate Phi(-mean / std). The profit is a product of normals, so it is skewed and this is only rough."""
    z = -profit_mean_formula(rho, **{k: v for k, v in kw.items() if k in ("p_mu", "p_sd", "v_mu", "d_mu", "d_sd", "fixed")}) / \
        profit_std_formula(rho, **{k: v for k, v in kw.items() if k in ("p_mu", "p_sd", "v_mu", "v_sd", "d_mu", "d_sd")})
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


# %% [markdown]
# ## Step 3: what correlation is believable?
# Session 2 gave a demand line: each extra dollar of price loses 250 loaves a month. If the
# price wobbles by sigma_p = 0.20 dollars *and demand follows that line*, demand moves by
# 250 x 0.20 = 50 loaves, and since the whole demand spread is 150 loaves the correlation is
# -50 / 150 = -0.33. That is a plausible central value; a stronger link needs more of the demand
# spread to be explained by price.

# %%
def implied_rho(p_sd=P_SD, d_sd=Q_SD, slope=DEMAND_B):
    """Correlation if demand moves along a demand line of the given slope when the price wobbles."""
    r = -slope * p_sd / d_sd
    if r < -1.0:
        raise ValueError("the demand line alone would explain more than the whole demand spread")
    return r


# %% [markdown]
# ## Step 4: how the risk depends on the correlation
# We scan rho from -0.9 to +0.9 with the same seed (common random numbers, so the curve is
# smooth). The mean profit hardly moves (it shifts by rho sigma_p sigma_D = 30 dollars per unit
# of rho) but the spread, and with it the loss probability, changes a lot. The lender's limit
# turns that into a question: for which correlations is the loss probability at most the limit?

# %%
def loss_vs_rho(rhos=None, **kw):
    rhos = np.round(np.arange(-0.9, 0.9001, 0.1), 10) if rhos is None else rhos
    return [(float(r) + 0.0, loss_probability(float(r), **kw)) for r in rhos]


def rho_for_limit(limit, lo=-0.99, hi=0.99, **kw):
    """Largest correlation whose loss probability is at most `limit` (bisection), or None if even `lo` fails."""
    if loss_probability(lo, **kw) > limit:
        return None
    if loss_probability(hi, **kw) <= limit:
        return hi
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if loss_probability(mid, **kw) <= limit:
            lo = mid
        else:
            hi = mid
    return lo


# %% [markdown]
# ## Step 5: a note on what the correlation does
# A high price earns more per loaf but sells fewer loaves. With rho < 0 the two effects partly
# cancel (a **natural hedge**), so the profit varies less; with rho > 0 they add and the profit
# varies more. The expected profit changes only a little. So: *the risk of a loss depends on the
# links between the inputs, not only on the spread of each one.*

# %%
def decompose_spread(rho):
    """Standard deviation of profit with rho, and with rho = 0, and their difference."""
    s, s0 = profit_std_formula(rho), profit_std_formula(0.0)
    return s, s0, s - s0


# %% [markdown]
# ## See it
# Figure 1: price against demand for 1500 months at rho = 0 and rho = -0.5, with the loss
# months marked. Figure 2: profit histograms for rho = -0.5, 0 and +0.5, and the loss
# probability against rho with a limit.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("rho: loss probability, mean, std (simulated), mean, std (formula), normal estimate")
    for rho, loss in loss_vs_rho():
        pr = simulate_profit_corr(rho)
        print(f"{rho:5.1f}: loss {100 * loss:5.2f} %  mean {pr.mean():6.1f} std {pr.std():6.1f}   "
              f"formula {profit_mean_formula(rho):6.1f} {profit_std_formula(rho):6.1f}   normal {100 * loss_normal_approx(rho):5.2f} %")
    print("rho implied by the demand line:", round(implied_rho(), 3), "loss", round(100 * loss_probability(implied_rho()), 2), "%")
    r8 = rho_for_limit(0.08)
    print("largest rho with a loss probability of at most 8 %:", round(r8, 3))

    BLUE, ORANGE, MAGENTA = "#0072b2", "#c86a00", "#d81b60"
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.0), sharey=True)
    for ax, rho in zip(axs, (0.0, -0.5)):
        pr, price, dem = simulate_profit_corr(rho, n=1500, inputs=True)
        loss = pr < 0
        ax.scatter(price[~loss], dem[~loss], s=8, color=BLUE, alpha=0.55, label="profit month")
        ax.scatter(price[loss], dem[loss], s=10, color=MAGENTA, marker="x", label="loss month")
        ax.set_xlabel("price drawn ($ per loaf)")
        ax.set_title(f"correlation {rho:+.1f}: {100 * np.mean(loss):.1f} % of months lose money", fontsize=10)
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("demand drawn (loaves per month)")
    axs[0].legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "price_demand_scatter.png", dpi=120)

    fig2, axs2 = plt.subplots(1, 2, figsize=(9.6, 4.0))
    bins = np.linspace(-1000, 2500, 71)
    for rho, col, ls in ((-0.5, BLUE, "-"), (0.0, "#444444", "--"), (0.5, ORANGE, ":")):
        pr = simulate_profit_corr(rho)
        axs2[0].hist(pr, bins=bins, histtype="step", lw=2, color=col, ls=ls, label=f"correlation {rho:+.1f}")
    axs2[0].axvline(0, color="black", lw=0.8)
    axs2[0].set_xlabel("monthly profit ($)")
    axs2[0].set_ylabel("simulated months (of 20000)")
    axs2[0].set_title("Same averages, different spread", fontsize=10)
    axs2[0].legend(fontsize=8)
    axs2[0].grid(alpha=0.3)
    rs, ls_ = zip(*loss_vs_rho())
    axs2[1].plot(rs, [100 * x for x in ls_], color=BLUE, lw=2, marker="o", ms=4, label="simulated loss probability")
    axs2[1].axhline(8, color=MAGENTA, ls="--", lw=1.5, label="lender's limit 8 %")
    axs2[1].axvline(implied_rho(), color=ORANGE, ls=":", lw=2, label="implied by the demand line (-0.33)")
    axs2[1].set_xlabel("correlation between price and demand")
    axs2[1].set_ylabel("chance a month makes a loss (%)")
    axs2[1].set_title("Risk grows with the correlation", fontsize=10)
    axs2[1].legend(fontsize=8)
    axs2[1].grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "loss_vs_rho.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
