"""Session 3 (Level 3): statistical tolerance stacks, process capability and tolerance allocation.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: how likely is the worst case?
# **A. Real-world problem.** Session 2 added up the tolerances: safe, but every part must be
# held very tight. Yet it is very unlikely that five independent parts all sit at their worst
# limit together. Statistical stack-up uses that fact to allow looser, cheaper parts, and the
# price is a small, known fraction of assemblies that fail. Today you compute that fraction,
# check it by simulation, see how a drifting process breaks it, and allocate tolerances to five
# parts at the lowest (illustrative) cost.
#
# *Educational model.* Parts are independent and normally distributed. Real processes can be
# skewed, correlated or drifting; the cost model is illustrative, not data from a factory.

# %%
import itertools
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# the five-part assembly (mm): housing (+) and four stacked parts (-)
NOMINALS = np.array([52.0, 10.0, 12.0, 15.0, 13.0])
SIGNS = np.array([1, -1, -1, -1, -1])
GAP_NOMINAL = float(np.dot(SIGNS, NOMINALS))     # 2.00 mm
GAP_TOL = 0.30                                    # the gap must stay within 2.00 +- 0.30 mm
K_COST = np.array([3.0, 0.4, 1.0, 0.2, 0.6])      # illustrative cost coefficients, cost unit x mm
T_MIN = 0.05                                      # illustrative: no process here can hold better than +-0.05 mm
NSIGMA = 3.0                                      # a part tolerance t is +-3 sigma of its process


# %% [markdown]
# ## Step 1: worst case versus root-sum-square (RSS)
# A part tolerance +-t is taken as +-3 sigma, so `sigma_i = t_i / 3`. For independent parts the
# variances add:
#
#     sigma_gap = sqrt( sum sigma_i^2 )     so the +-3 sigma gap tolerance is  sqrt( sum t_i^2 )
#
# Worst case adds the tolerances directly: `sum t_i`. RSS is never larger than the sum.

# %%
def worst_case_tol(tols):
    return float(np.sum(tols))


def rss_tol(tols):
    """Gap tolerance (+-3 sigma) for independent parts: square root of the sum of squares."""
    return float(np.sqrt(np.sum(np.square(tols))))


def sigma_gap(tols):
    return rss_tol(tols) / NSIGMA


def corner_range(tols):
    """Lowest and highest gap over all 2^n corners (every part at a limit)."""
    gaps = []
    for pick in itertools.product((-1, 1), repeat=len(NOMINALS)):
        gaps.append(float(np.dot(SIGNS, NOMINALS + np.array(pick) * np.asarray(tols))))
    return min(gaps), max(gaps)


def simulate_gaps(tols, n=200_000, seed=7, drift=0.0):
    """Gap of n random assemblies. Each part ~ Normal(nominal, t/3). `drift` shifts every process
    centre by drift x sigma_i in the direction that makes the gap bigger (0 = centred)."""
    rng = np.random.default_rng(seed)
    tols = np.asarray(tols, dtype=float)
    sig = tols / NSIGMA
    centre = NOMINALS + drift * sig * SIGNS
    parts = rng.normal(centre, sig, size=(n, len(NOMINALS)))
    return parts @ SIGNS


# %% [markdown]
# ## Step 2: capability and the fraction out of tolerance
# With limits LSL and USL (the lower and upper specification limits) and a gap that is normal
# with mean mu and spread sigma:
#
#     Cp  = (USL - LSL) / (6 sigma)
#     Cpk = min(USL - mu, mu - LSL) / (3 sigma)          (penalises an off-centre process)
#     fraction out = Phi((LSL - mu)/sigma) + 1 - Phi((USL - mu)/sigma)
#
# where Phi(z) = (1 + erf(z / sqrt 2)) / 2 is the normal cumulative distribution. A common
# guideline is Cp >= 1.33, i.e. the limits are four sigma away.

# %%
def phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _need_sigma(sigma):
    if sigma <= 0:
        raise ValueError("sigma must be positive")


def cp(lsl, usl, sigma):
    _need_sigma(sigma)
    return (usl - lsl) / (6.0 * sigma)


def cpk(lsl, usl, mean, sigma):
    _need_sigma(sigma)
    return min(usl - mean, mean - lsl) / (3.0 * sigma)


def fraction_out(lsl, usl, mean, sigma):
    _need_sigma(sigma)
    return phi((lsl - mean) / sigma) + 1.0 - phi((usl - mean) / sigma)


def spec_limits():
    return GAP_NOMINAL - GAP_TOL, GAP_NOMINAL + GAP_TOL


# %% [markdown]
# ## Step 3: illustrative cost and allocation
# Tighter tolerances cost more. We *assume* cost_i = k_i / t_i (halve the tolerance, double the
# cost). Minimising `sum k_i / t_i` while keeping the RSS gap tolerance at `T` gives (by a
# Lagrange multiplier) `t_i` proportional to `k_i^(1/3)`. Under worst-case addition it is
# `t_i` proportional to `sqrt(k_i)`. A part with an expensive process (large k) is given the
# looser tolerance.

# %%
def cost(tols, k=K_COST):
    return float(np.sum(k / np.asarray(tols)))


def rss_target(cp_required=4.0 / 3.0, gap_tol=GAP_TOL):
    """RSS gap tolerance that gives the required Cp when the process is centred."""
    return gap_tol / cp_required


def allocate_rss(total, k=K_COST):
    w = k ** (1.0 / 3.0)
    return total * w / math.sqrt(float(np.sum(w ** 2)))


def allocate_worst_case(total, k=K_COST):
    w = np.sqrt(k)
    return total * w / float(np.sum(w))


def makeable(tols, t_min=T_MIN):
    """True if no part needs a tolerance tighter than the process limit."""
    return bool(np.all(np.asarray(tols) >= t_min - 1e-12))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    lsl, usl = spec_limits()
    t_eq = np.full(5, rss_target() / math.sqrt(5))
    print(f"gap nominal {GAP_NOMINAL:.2f} mm, limits {lsl:.2f} to {usl:.2f} mm")
    print(f"equal tolerances +-{t_eq[0]:.4f} mm: worst case {worst_case_tol(t_eq):.3f}, RSS {rss_tol(t_eq):.3f}")
    lo, hi = corner_range(t_eq)
    print(f"corners: {lo:.3f} to {hi:.3f} mm")
    g = simulate_gaps(t_eq)
    print(f"simulation: mean {g.mean():.4f}, std {g.std():.4f} (analytic {sigma_gap(t_eq):.4f})")
    s = sigma_gap(t_eq)
    print(f"Cp {cp(lsl, usl, s):.3f}, Cpk {cpk(lsl, usl, GAP_NOMINAL, s):.3f}, fraction out {fraction_out(lsl, usl, GAP_NOMINAL, s):.2e}")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(g, bins=80, density=True, alpha=0.6, label="simulated assemblies")
    zz = np.linspace(lsl - 0.1, usl + 0.1, 300)
    ax.plot(zz, np.exp(-0.5 * ((zz - GAP_NOMINAL) / s) ** 2) / (s * math.sqrt(2 * math.pi)), "k", label="normal, sigma = RSS")
    ax.axvline(lsl, color="red", ls="--", label="limits")
    ax.axvline(usl, color="red", ls="--")
    ax.set_xlabel("assembly gap (mm)")
    ax.set_ylabel("probability density (1/mm)")
    ax.set_title("Five-part stack: simulated gap versus the RSS normal curve")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "gap_histogram.png", dpi=120)

    t_rss = allocate_rss(rss_target())
    t_wc = allocate_worst_case(GAP_TOL)
    print("RSS allocation  :", np.round(t_rss, 4), f"cost {cost(t_rss):.2f}, makeable {makeable(t_rss)}")
    print("equal (RSS)     :", np.round(t_eq, 4), f"cost {cost(t_eq):.2f}")
    print("worst-case alloc:", np.round(t_wc, 4), f"cost {cost(t_wc):.2f}, makeable {makeable(t_wc)}")
    t_wc_eq = np.full(5, GAP_TOL / 5)
    print(f"worst-case equal +-{t_wc_eq[0]:.3f}: cost {cost(t_wc_eq):.2f}, makeable {makeable(t_wc_eq)}")

    fig2, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    labels = ["worst case\n(sum)", "RSS\n(statistical)"]
    axes[0].bar(labels, [worst_case_tol(t_eq), rss_tol(t_eq)], color=["tab:red", "tab:green"])
    axes[0].set_ylabel("gap tolerance, plus or minus (mm)")
    axes[0].set_title("Same five parts, two ways to add")
    drifts = np.linspace(0, 2.0, 21)
    sim = [np.mean((simulate_gaps(t_rss, 100_000, 3, d) < lsl) | (simulate_gaps(t_rss, 100_000, 3, d) > usl)) for d in drifts]
    s_r = sigma_gap(t_rss)
    ana = [fraction_out(lsl, usl, GAP_NOMINAL + d * float(np.sum(t_rss / NSIGMA)), s_r) for d in drifts]
    axes[1].plot(drifts, 100 * np.array(ana), label="analytic (erf)")
    axes[1].plot(drifts, 100 * np.array(sim), "o", ms=3, label="simulation")
    axes[1].set_xlabel("process drift of every part (multiples of its sigma)")
    axes[1].set_ylabel("assemblies out of tolerance (%)")
    axes[1].set_title("A drifting process breaks the stack")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "worst_case_vs_rss.png", dpi=120)

    d1 = simulate_gaps(t_rss, 400_000, 11, 1.0)
    print(f"RSS allocation with every process drifted by 1 sigma: {np.mean((d1 < lsl) | (d1 > usl)):.4f} out (analytic "
          f"{fraction_out(lsl, usl, GAP_NOMINAL + float(np.sum(t_rss / NSIGMA)), s_r):.4f})")

# %% [markdown]
# ## Where this stops
# Real parts are not always normal, and processes drift. The roadmap shows how a control chart
# watches for drift and how allowed tolerance grades are chosen from a standard list.
