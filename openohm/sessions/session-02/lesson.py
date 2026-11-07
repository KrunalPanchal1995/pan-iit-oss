"""Session 2 (Level 2): series and parallel networks, power ratings, a design problem.

Run:  python start.py 2
Low-voltage educational circuits only (never mains). Ideal supply, ideal wires.
"""
# %% [markdown]
# # Session 2: resistor networks and a design to a limit
# **A. Real-world problem.** You have a 12 V supply and small 0.25 W resistors. You want about
# 0.1 A to flow. One resistor of the right size would overheat. Can several resistors share the
# load safely?
#
# **Plan.** (1) series and parallel rules, (2) current and power in every resistor,
# (3) search the standard E12 values for the smallest safe design.

# %%
import itertools
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

E12 = (1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2)   # standard values per decade


# %% [markdown]
# ## Step 1: equivalent resistance
# Series (one path): the same current flows through all, R = R1 + R2 + ...
# Parallel (several paths): the same voltage is across all, 1/R = 1/R1 + 1/R2 + ...
# Check by hand: 6 ohm in series with 12 ohm is 18 ohm; 6 ohm parallel with 12 ohm is
# 6*12/(6+12) = 4 ohm.

# %%
def series(rs):
    return float(sum(rs))


def parallel(rs):
    return float(1.0 / sum(1.0 / r for r in rs))


# %% [markdown]
# ## Step 2: a grid of identical resistors
# `n_s` resistors in series make one branch; `n_p` such branches sit in parallel. Each
# resistor has the value `r`. Total R = n_s * r / n_p. Total current I = V / R, and each
# branch carries I / n_p, so each resistor dissipates (I / n_p)^2 * r.

# %%
def grid_resistance(r, n_s, n_p):
    return parallel([series([r] * n_s)] * n_p)


def grid_per_resistor_power(volts, r, n_s, n_p):
    """Power (W) in each resistor of the grid."""
    i_total = volts / grid_resistance(r, n_s, n_p)
    return (i_total / n_p) ** 2 * r


# %% [markdown]
# ## Step 3: design search
# Find all grids of E12 values (decades from 1 ohm to
# 8.2 kilohm) with at most `max_n` resistors, whose current is within `tol` of the target and
# where every resistor stays under its power rating. Sort by the number of resistors.

# %%
def design(volts, i_target, tol, rating, max_n=8):
    """List of dicts (n, n_s, n_p, r, current, p_each) meeting the limits, fewest parts first."""
    found = []
    values = [v * 10 ** d for d in range(0, 4) for v in E12]
    for n_s, n_p in itertools.product(range(1, max_n + 1), repeat=2):
        if n_s * n_p > max_n:
            continue
        for r in values:
            i = volts / grid_resistance(r, n_s, n_p)
            p_each = grid_per_resistor_power(volts, r, n_s, n_p)
            if abs(i - i_target) <= tol * i_target and p_each <= rating:
                found.append({"n": n_s * n_p, "n_s": n_s, "n_p": n_p, "r": r, "current": i, "p_each": p_each})
    found.sort(key=lambda d: (d["n"], abs(d["current"] - i_target)))
    return found


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("series(6, 12) =", series([6, 12]), "ohm; parallel(6, 12) =", parallel([6, 12]), "ohm")
    print("one 120 ohm resistor on 12 V dissipates", 12 ** 2 / 120, "W (rating 0.25 W!)")
    best = design(12.0, 0.100, 0.05, 0.25)
    for d in best[:5]:
        print(f"{d['n']} parts: {d['n_s']} in series x {d['n_p']} branches of {d['r']:g} ohm -> "
              f"I = {1000 * d['current']:.1f} mA, each part {d['p_each']:.3f} W")

    # P vs. number of series parts for total R fixed near 120 ohm
    fig, ax = plt.subplots(figsize=(6, 4))
    ns = np.arange(1, 9)
    p_each = [(12.0 / 120.0) ** 2 * (120.0 / n) for n in ns]
    ax.bar(ns, p_each, color="#3b6fb6")
    ax.axhline(0.25, color="crimson", ls="--", label="rating 0.25 W")
    ax.set_xlabel("identical resistors in series, total 120 ohm")
    ax.set_ylabel("power in each resistor (watts)")
    ax.set_title("Sharing the load: 12 V, 0.1 A")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "share_the_load.png", dpi=120)

    # design space: total R vs V -> current and per-part limit
    v = np.linspace(1, 24, 120)
    r_tot = np.linspace(5, 300, 120)
    VV, RR = np.meshgrid(v, r_tot)
    II = VV / RR
    PP = VV ** 2 / RR
    fig2, ax2 = plt.subplots(figsize=(6, 4.5))
    m = ax2.pcolormesh(VV, RR, PP, shading="auto", cmap="viridis")
    fig2.colorbar(m, ax=ax2, label="power P (watts)")
    ax2.contour(VV, RR, II, levels=[0.1], colors="white")
    ax2.contour(VV, RR, PP, levels=[0.25], colors="red")
    ax2.set_xlabel("supply voltage V (volts)")
    ax2.set_ylabel("resistance R (ohms)")
    ax2.set_title("Power map; white: I = 0.1 A, red: P = 0.25 W")
    fig2.tight_layout()
    fig2.savefig(OUT / "design_map.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
