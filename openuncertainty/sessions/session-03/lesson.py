"""Session 3 (Level 3): Monte Carlo propagation versus the linear formula, and when linear fails.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: Monte Carlo propagation and its limits
# **A. Real-world problem.** The linear formula of Session 2 replaces the formula by a
# straight line near the measured values. That is fine for small errors. But what if you
# divide by a reading that is close to zero, or sit at the top of a curve where the slope
# is zero? We let the computer try 100000 possible experiments and look at the outcome.
#
# **Plan.** (1) Monte Carlo propagation, (2) a derivative by central differences,
# (3) non-normal inputs, (4) combined and expanded uncertainty, (5) two failure cases.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: Monte Carlo propagation
# Draw each input from its distribution (seeded, so results repeat), push every draw through
# the formula and look at the list of outputs. A 95 percent interval is the 2.5th to 97.5th
# percentile of that list; it needs no derivative and no normal assumption.

# %%
def mc_samples(f, means, sigmas, n=100000, seed=7):
    """Output samples of f for independent normal inputs."""
    rng = np.random.default_rng(seed)
    xs = [m + s * rng.standard_normal(n) for m, s in zip(means, sigmas)]
    return f(*xs)


def percentile_interval(samples, level=0.95):
    """Central interval holding `level` of the samples."""
    a = 100.0 * (1.0 - level) / 2.0
    lo, hi = np.percentile(samples, [a, 100.0 - a])
    return float(lo), float(hi)


# %% [markdown]
# ## Step 2: a derivative by central differences
# The slope of f at x is (f(x + h) - f(x - h)) / (2 h). A step h that is too big blurs the
# curve; one that is too small drowns the difference in round-off. A relative step of about
# 1e-5 to 1e-6 works well for smooth functions.

# %%
def central_diff(f, x, h):
    return (f(x + h) - f(x - h)) / (2.0 * h)


def numeric_linear_sigma(f, means, sigmas, rel_step=1e-6):
    """First-order sigma using central-difference partial derivatives (independent inputs)."""
    means = [float(m) for m in means]
    var = 0.0
    for i, (m, s) in enumerate(zip(means, sigmas)):
        h = rel_step * (abs(m) if m != 0 else 1.0)

        def fi(v, i=i):
            a = list(means)
            a[i] = v
            return f(*a)

        var += (central_diff(fi, m, h) * s) ** 2
    return float(np.sqrt(var))


# %% [markdown]
# ## Step 3: inputs that are not normal, and the GUM combination
# A digital ruler shows a value rounded to a step LSB (say 0.01 mm). The true value is
# anywhere in a band of width LSB: a uniform distribution, with standard deviation
# LSB / sqrt(12). Independent standard uncertainties combine in quadrature (after being
# multiplied by their sensitivities) into the combined uncertainty u_c; the expanded
# uncertainty is U = k u_c, with k = 2 for about 95 percent coverage.

# %%
def uniform_sigma(lsb):
    return lsb / np.sqrt(12.0)


def combined_uncertainty(sens, us):
    return float(np.sqrt(np.sum((np.asarray(sens, dtype=float) * np.asarray(us, dtype=float)) ** 2)))


def expanded(uc, k=2.0):
    return k * uc


# %% [markdown]
# ## Step 4: when the linear formula fails
# (a) A ratio with the denominator near zero. (b) A function at its maximum: the slope is
# zero, so the first-order formula says "no uncertainty". The second-order term gives
# sigma = |f''| s^2 / sqrt(2) for a normal input of spread s.

# %%
def ratio(x, y):
    return x / y


def second_order_sigma(f2, s):
    """Spread of f near a maximum or minimum for a normal input: |f''| s^2 / sqrt(2)."""
    return abs(f2) * s ** 2 / np.sqrt(2.0)


# %% [markdown]
# ## Step 5: see it
# Figure 1: Monte Carlo histogram of x / y with the linear Gaussian on top.
# Figure 2: the central-difference error against the step size.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for rel in (0.01, 0.30):
        out = mc_samples(ratio, [10.0, 5.0], [0.5, 5.0 * rel])
        lin = numeric_linear_sigma(ratio, [10.0, 5.0], [0.5, 5.0 * rel])
        lo, hi = percentile_interval(out)
        print(f"y error {100 * rel:.0f}%: linear {2 - 1.96 * lin:.3f}..{2 + 1.96 * lin:.3f}, "
              f"Monte Carlo {lo:.3f}..{hi:.3f}")
    out = mc_samples(ratio, [10.0, 5.0], [0.5, 1.5])
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.hist(out, bins=np.linspace(-1, 8, 181), density=True, alpha=0.5, label="Monte Carlo (100000)")
    lin = numeric_linear_sigma(ratio, [10.0, 5.0], [0.5, 1.5])
    xs = np.linspace(-1, 8, 400)
    ax.plot(xs, np.exp(-0.5 * ((xs - 2) / lin) ** 2) / (lin * np.sqrt(2 * np.pi)), "r", label="linear formula")
    ax.set_xlabel("x / y (no unit)")
    ax.set_ylabel("probability density")
    ax.set_title("30 % error in the denominator: skewed output")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "ratio_skew.png", dpi=120)

    f = lambda t: 4 * np.pi ** 2 * 1.0 / t ** 2
    exact = -8 * np.pi ** 2 / 2.007 ** 3
    hs = 10.0 ** -np.arange(1, 14, dtype=float)
    errs = [abs(central_diff(f, 2.007, h * 2.007) / exact - 1) for h in hs]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.loglog(hs, errs, "o-")
    ax2.set_xlabel("relative step size h / T (no unit)")
    ax2.set_ylabel("relative error of the derivative (no unit)")
    ax2.set_title("Central difference: truncation versus round-off")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "step_size.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the exercises, answer the questions in the README (section F), run the checkpoint,
# then start the mini-project (error budget for a metal cylinder).
