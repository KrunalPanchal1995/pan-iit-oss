"""Session 1 (Level 1): boil, condense, repeat. Why vapour is richer in ethanol.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: boil it, condense it, do it again
# **A. Real-world problem.** A sugar-cane molasses distillery ferments a "wash" that is about
# 10 percent ethanol by moles and 90 percent water. Ethanol boils at 78.3 C, water at 100 C.
# If you boil the wash once, how much richer in ethanol is the vapour? How many boil-and-condense
# steps (stages) do you need to reach 80 percent ethanol? And how much of the feed ends up as
# product?
#
# **Plan.** (1) relative volatility and the equilibrium curve y(x), (2) one stage, (3) the
# material balance F = D + B, (4) stacking stages: the minimum number of stages at total reflux.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: relative volatility and one equilibrium stage
# Put a liquid mixture in a closed pot, heat it to boiling and wait. The vapour above it is
# richer in the component that boils more easily (ethanol). We write x for the **mole fraction**
# of ethanol in the liquid and y for the mole fraction of ethanol in the vapour.
#
# The simplest model says the vapour's ethanol-to-water ratio is alpha times the liquid's:
#
#     y / (1 - y) = alpha * x / (1 - x)      so      y = alpha x / (1 + (alpha - 1) x)
#
# alpha is the **relative volatility** (no unit). alpha = 1 means no separation at all; the
# bigger alpha, the easier the job. Session 2 shows that for ethanol and water alpha is not
# really constant; here we treat it as one number to learn the idea.

# %%
def vapour_fraction(x, alpha):
    """Ethanol mole fraction in the vapour in equilibrium with liquid x (constant alpha)."""
    if alpha <= 0:
        raise ValueError("relative volatility must be positive")
    x = np.asarray(x, float)
    if np.any((x < 0) | (x > 1)):
        raise ValueError("mole fraction must be between 0 and 1")
    return alpha * x / (1.0 + (alpha - 1.0) * x)


def liquid_fraction(y, alpha):
    """Inverse of vapour_fraction: the liquid x that is in equilibrium with vapour y."""
    y = np.asarray(y, float)
    return y / (alpha - (alpha - 1.0) * y)


def odds(z):
    """Ethanol-to-water ratio z / (1 - z). One stage multiplies the odds by alpha."""
    return z / (1.0 - z)


# %% [markdown]
# ## Step 2: the material balance
# A column takes a feed F (mol) with ethanol fraction zF and splits it into a top product,
# the **distillate** D with fraction xD, and a bottom product B with fraction xB. Nothing is
# created or destroyed, so both the total and the ethanol must balance:
#
#     F = D + B          F zF = D xD + B xB
#
# Solving the two equations gives D = F (zF - xB) / (xD - xB). The **recovery** is the share of
# the feed's ethanol that leaves in the distillate: D xD / (F zF).

# %%
def split(feed, z_feed, x_top, x_bottom):
    """Distillate and bottoms amounts (same unit as feed) from the two material balances."""
    if not (0 <= x_bottom < z_feed < x_top <= 1):
        raise ValueError("need 0 <= xB < zF < xD <= 1")
    d = feed * (z_feed - x_bottom) / (x_top - x_bottom)
    return d, feed - d


def recovery(feed, z_feed, x_top, x_bottom):
    """Share of the feed's ethanol that ends up in the distillate (no unit)."""
    d, _ = split(feed, z_feed, x_top, x_bottom)
    return d * x_top / (feed * z_feed)


# %% [markdown]
# ## Step 3: stack the stages (total reflux)
# A distillation column is a stack of stages. Vapour from one stage is condensed and becomes
# the liquid of the stage above, which boils again. If all the condensed liquid is sent back
# (total reflux, nothing taken out) every stage multiplies the odds by alpha. To climb from
# the bottom xB to the top xD the odds must grow by the factor odds(xD) / odds(xB), so the
# smallest number of stages is (the Fenske equation)
#
#     N_min = ln[ odds(xD) / odds(xB) ] / ln(alpha)

# %%
def min_stages(x_top, x_bottom, alpha):
    """Fenske minimum number of equilibrium stages at total reflux (may be fractional)."""
    if alpha <= 1:
        raise ValueError("alpha must be above 1 for any separation")
    if not (0 < x_bottom < x_top < 1):
        raise ValueError("need 0 < xB < xD < 1")
    return float(np.log(odds(x_top) / odds(x_bottom)) / np.log(alpha))


def climb(x_bottom, alpha, n):
    """Liquid fractions on n stages at total reflux, starting from x_bottom at the bottom."""
    xs = [float(x_bottom)]
    for _ in range(n):
        xs.append(float(vapour_fraction(xs[-1], alpha)))   # vapour condenses into the next liquid
    return np.array(xs)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # numbers used in the worked example
    print(f"one stage, alpha = 2.5, x = 0.20: y = {float(vapour_fraction(0.20, 2.5)):.4f}")
    d, b = split(100.0, 0.10, 0.80, 0.02)
    print(f"F = 100 mol, zF = 0.10, xD = 0.80, xB = 0.02: D = {d:.2f} mol, B = {b:.2f} mol, recovery = {recovery(100, 0.10, 0.80, 0.02):.3f}")
    print(f"minimum stages (alpha = 2.5): {min_stages(0.80, 0.02, 2.5):.2f}")

    # Figure 1: equilibrium curves for several alpha, and one stage marked
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    x = np.linspace(0, 1, 201)
    for a, colour in ((1.0, "#888888"), (1.5, "#e9a23b"), (2.5, "#2a9d8f"), (6.0, "#264653")):
        ax.plot(x, vapour_fraction(x, a), color=colour, label=f"alpha = {a:g}" + ("  (no separation)" if a == 1 else ""))
    y1 = float(vapour_fraction(0.20, 2.5))
    ax.plot([0.20, 0.20, 0], [0, y1, y1], "k--", lw=1)
    ax.annotate(f"liquid x = 0.20\nvapour y = {y1:.3f}", (0.20, y1), textcoords="offset points", xytext=(10, -34), fontsize=9)
    ax.set_xlabel("ethanol in liquid, x (mole fraction)")
    ax.set_ylabel("ethanol in vapour, y (mole fraction)")
    ax.set_title("Vapour is richer in the more volatile component")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "equilibrium_alpha.png", dpi=120)

    # Figure 2: stages at total reflux climb from 2 % to 80 %
    alpha = 2.5
    xs = climb(0.02, alpha, 7)
    fig2, (axl, axr) = plt.subplots(1, 2, figsize=(10, 4.4))
    axl.plot(x, vapour_fraction(x, alpha), color="#2a9d8f", label=f"equilibrium, alpha = {alpha:g}")
    axl.plot(x, x, color="k", lw=1, label="y = x (total reflux)")
    for i in range(len(xs) - 1):
        axl.plot([xs[i], xs[i], xs[i + 1]], [xs[i], xs[i + 1], xs[i + 1]], color="#d9534f", lw=1.4)
    axl.axvline(0.80, color="#264653", ls=":", lw=1)
    axl.text(0.81, 0.05, "xD = 0.80", fontsize=8)
    axl.set_xlabel("ethanol in liquid, x (mole fraction)")
    axl.set_ylabel("ethanol in vapour, y (mole fraction)")
    axl.set_title("Each step is one stage")
    axl.legend(fontsize=8, loc="lower right")
    axl.grid(alpha=0.3)
    axr.bar(range(len(xs)), xs, color=["#264653"] + ["#2a9d8f"] * (len(xs) - 1))
    axr.axhline(0.80, color="#d9534f", ls="--", lw=1)
    for i, v in enumerate(xs):
        axr.text(i, v + 0.015, f"{v:.2f}", ha="center", fontsize=8)
    axr.set_xlabel("stage number (0 = bottom liquid)")
    axr.set_ylabel("ethanol in liquid (mole fraction)")
    axr.set_title(f"Fenske: N_min = {min_stages(0.80, 0.02, alpha):.2f} stages")
    axr.set_ylim(0, 1)
    fig2.tight_layout()
    fig2.savefig(OUT / "stages_total_reflux.png", dpi=120)
    print("liquid fractions up the column:", np.round(xs, 3))

# %% [markdown]
# ## Where this stops
# Real ethanol-water mixtures do not have one constant alpha: it is about 10 when ethanol is
# dilute and falls to 1 near 89 percent, where no further enrichment by boiling is possible.
# Session 2 builds the real equilibrium curve from vapour pressures.
