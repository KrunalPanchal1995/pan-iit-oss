"""Session 2 (Level 2): the first-order propagation formula, checked against Monte Carlo.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: propagating uncertainty with a formula
# **A. Real-world problem.** A pendulum of length L and period T gives g = 4 pi^2 L / T^2.
# You measure L with a ruler and T with a stopwatch. Both have uncertainty. What is the
# uncertainty of g, and which measurement should you improve first?
#
# **Plan.** (1) the standard error of the mean, (2) the propagation formula,
# (3) check it by simulation, (4) error budget, (5) correlated inputs, (6) reporting.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: standard uncertainty and standard error of the mean
# Repeat a reading n times. The standard deviation s of the readings is the *standard
# uncertainty* of one reading. The mean of n readings is steadier: its uncertainty is the
# *standard error of the mean*, s / sqrt(n). We verify this by simulating many experiments.

# %%
def sem(s, n):
    """Standard error of the mean of n readings with standard deviation s."""
    return s / np.sqrt(n)


def simulate_sem(sigma, n, trials=20000, seed=1):
    """Spread of the means of `trials` experiments, each with n readings of spread sigma."""
    rng = np.random.default_rng(seed)
    means = rng.normal(10.0, sigma, size=(trials, n)).mean(axis=1)
    return float(means.std(ddof=1))


# %% [markdown]
# ## Step 2: the propagation formula
# For q = f(x, y) with small errors sx and sy:
#     sq^2 = (df/dx)^2 sx^2 + (df/dy)^2 sy^2  + 2 (df/dx)(df/dy) cov(x, y)
# The covariance term is zero for independent inputs. `linear_sigma` takes the list of
# partial derivatives (the sensitivities) and the standard uncertainties; an optional
# correlation rho (two inputs) adds the covariance cov = rho sx sy.

# %%
def linear_sigma(grads, sigmas, rho=0.0):
    g = np.asarray(grads, dtype=float)
    s = np.asarray(sigmas, dtype=float)
    var = float(np.sum((g * s) ** 2))
    if len(g) == 2:
        var += 2.0 * g[0] * g[1] * rho * s[0] * s[1]
    return float(np.sqrt(max(var, 0.0)))


def variance_shares(grads, sigmas):
    """Fraction of the output variance that comes from each input (independent inputs)."""
    parts = (np.asarray(grads, dtype=float) * np.asarray(sigmas, dtype=float)) ** 2
    return parts / parts.sum()


def mc_sigma(f, means, sigmas, n=200000, seed=2, rho=0.0):
    """Monte Carlo spread of f for normal inputs (rho links the first two inputs)."""
    rng = np.random.default_rng(seed)
    k = len(means)
    z = rng.standard_normal((k, n))
    if k >= 2 and rho != 0.0:
        z[1] = rho * z[0] + np.sqrt(1.0 - rho ** 2) * z[1]
    xs = [m + s * zi for m, s, zi in zip(means, sigmas, z)]
    return float(np.std(f(*xs), ddof=1))


# %% [markdown]
# ## Step 3: three formulas
# Each function comes with its analytic partial derivatives, so we can compare the formula
# with Monte Carlo.

# %%
def area(L, W):
    return L * W


def area_grads(L, W):
    return [W, L]


def density(m, r, h):
    """Density of a cylinder: mass / (pi r^2 h)."""
    return m / (np.pi * r ** 2 * h)


def density_grads(m, r, h):
    rho = density(m, r, h)
    return [rho / m, -2.0 * rho / r, -rho / h]


def pendulum_g(L, T):
    """g = 4 pi^2 L / T^2 (small swings, point mass)."""
    return 4.0 * np.pi ** 2 * L / T ** 2


def pendulum_grads(L, T):
    g = pendulum_g(L, T)
    return [g / L, -2.0 * g / T]


# %% [markdown]
# ## Step 4: reporting and the error budget
# Quote the uncertainty with ONE significant figure, then round the value to the same
# decimal place: g = 9.801 +- 0.109 is written 9.8 +- 0.1 m/s^2.

# %%
def round_report(value, unc):
    """Return (value, unc, decimals): unc to one significant figure, value to the same place."""
    e = int(np.floor(np.log10(unc)))
    u1 = round(unc / 10.0 ** e) * 10.0 ** e
    if u1 >= 10.0 ** (e + 1):
        e += 1
    decimals = max(-e, 0)
    return round(value, -e), round(u1, -e), decimals


def pendulum_budget(L, sL, T, sT):
    """g, its uncertainty, the relative uncertainty and the variance share of L and T."""
    g = pendulum_g(L, T)
    gr = pendulum_grads(L, T)
    s = linear_sigma(gr, [sL, sT])
    return g, s, s / g, variance_shares(gr, [sL, sT])


# %% [markdown]
# ## Step 5: see it
# Figure 1: the pendulum Monte Carlo cloud of g with the linear Gaussian on top.
# Figure 2: correlated inputs; the uncertainty of x - y falls as the correlation grows.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    L0, sL, T0, sT = 1.000, 0.005, 2.007, 0.010
    g0, sg, rel, sh = pendulum_budget(L0, sL, T0, sT)
    print(f"g = {g0:.3f}, linear sigma = {sg:.4f} ({100 * rel:.3f}%), shares L {sh[0]:.3f}, T {sh[1]:.3f}")
    print("Monte Carlo sigma =", round(mc_sigma(pendulum_g, [L0, T0], [sL, sT]), 4))
    print("report:", round_report(g0, sg))

    rng = np.random.default_rng(3)
    gs = pendulum_g(L0 + sL * rng.standard_normal(100000), T0 + sT * rng.standard_normal(100000))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(gs, bins=80, density=True, alpha=0.5, label="Monte Carlo (100000)")
    xs = np.linspace(gs.min(), gs.max(), 300)
    ax.plot(xs, np.exp(-0.5 * ((xs - g0) / sg) ** 2) / (sg * np.sqrt(2 * np.pi)), "r", label="linear formula")
    ax.set_xlabel("g (m/s^2)")
    ax.set_ylabel("probability density (s^2/m)")
    ax.set_title("Pendulum: spread of g from L and T errors")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "pendulum_g.png", dpi=120)

    rhos = np.linspace(0, 1, 51)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(rhos, [linear_sigma([1, -1], [0.1, 0.1], r) for r in rhos], label="x - y")
    ax2.plot(rhos, [linear_sigma([1, 1], [0.1, 0.1], r) for r in rhos], label="x + y")
    ax2.set_xlabel("correlation rho between x and y (no unit)")
    ax2.set_ylabel("uncertainty of result (cm)")
    ax2.set_title("Shared calibration error cancels in a difference")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "correlation.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the exercises, answer the questions in the README (section F), run the checkpoint.
