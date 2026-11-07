"""Session 1 (Level 1): an engine turns heat into work and throws the rest away.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: heat in, work out, heat rejected
# **A. Real-world problem.** A car engine burns fuel, but only part of the fuel's energy
# turns the wheels. The rest leaves through the exhaust and the radiator. Why can no engine
# turn all the heat into work? And how can a loop drawn on a pressure-volume graph tell you
# how much work one cycle gives?
#
# **Plan.** (1) the energy balance W = Qh - Qc, (2) efficiency = W / Qh, (3) the Carnot
# limit that no engine can beat, (4) the area of a P-V loop is the work.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the energy balance and the efficiency
# Over one full cycle the engine returns to where it started, so its stored energy has not
# changed. Energy in must equal energy out:
#
#     Qh = W + Qc      so      W = Qh - Qc        efficiency = W / Qh
#
# Qh is heat taken from the hot source, Qc is heat rejected to the cold surroundings, W is
# the useful (net) work. All three are in joules (J) per cycle, and all three are
# positive numbers: the direction of each flow is already in its name.

# %%
def work(q_hot, q_cold):
    """Net work per cycle (J) from the energy balance W = Qh - Qc."""
    return q_hot - q_cold


def efficiency(q_hot, q_cold):
    """Thermal efficiency W / Qh (no unit). Qh must be positive."""
    if q_hot <= 0:
        raise ValueError("heat taken from the hot source must be positive")
    return work(q_hot, q_cold) / q_hot


# %% [markdown]
# ## Step 2: the Carnot limit
# The second law of thermodynamics says some heat must always be rejected. If the hot source
# is at temperature Th and the cold surroundings at Tc (both in **kelvin**, K = degrees C +
# 273.15), the best any engine can do is
#
#     efficiency <= 1 - Tc / Th

# %%
def carnot_limit(t_hot, t_cold):
    """Highest possible efficiency between two temperatures in kelvin."""
    if t_cold <= 0 or t_hot < t_cold:
        raise ValueError("need 0 < Tc <= Th, both in kelvin")
    return 1.0 - t_cold / t_hot


def is_allowed(q_hot, q_cold, t_hot, t_cold):
    """True if an engine with these heats does not break the energy balance or the Carnot limit."""
    if q_cold < 0 or q_cold > q_hot:
        return False
    return efficiency(q_hot, q_cold) <= carnot_limit(t_hot, t_cold) + 1e-12


# %% [markdown]
# ## Step 3: a P-V loop and its area
# Plot the gas pressure P against its volume V while the engine goes round one cycle. When
# the gas expands at high pressure it does more work than is spent squeezing it back at low
# pressure, so a loop that goes **clockwise** gives positive net work, and the area enclosed
# by the loop equals that work.
# With pressure in kPa and volume in litres, kPa x L = J.

# %%
def rectangle_loop(p_low, p_high, v_low, v_high):
    """Corners of a clockwise rectangular loop as (V, P) arrays.

    It starts at the bottom-left corner (v_low, p_low) and goes up, right, down,
    then back left to the start, which is clockwise on a P-V graph."""
    v = np.array([v_low, v_low, v_high, v_high])
    p = np.array([p_low, p_high, p_high, p_low])
    return v, p


def loop_work(v, p):
    """Work done by the gas around a closed loop: the sum of P dV (trapezoid rule).

    Positive for a clockwise loop (an engine), negative for a counter-clockwise loop
    (a refrigerator or heat pump)."""
    v = np.asarray(v, float)
    p = np.asarray(p, float)
    v2, p2 = np.roll(v, -1), np.roll(p, -1)
    return float(np.sum(0.5 * (p + p2) * (v2 - v)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # Figure 1: where does the heat go? three engines taking 1000 J from a 600 K source
    q_hot, t_hot, t_cold = 1000.0, 600.0, 300.0
    names = ["Engine A", "Engine B", "Engine C"]
    q_cold = [700.0, 550.0, 400.0]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for i, (n, qc) in enumerate(zip(names, q_cold)):
        w = work(q_hot, qc)
        ax.bar(i, w, color="#2a9d8f", label="work W" if i == 0 else None)
        ax.bar(i, qc, bottom=w, color="#d9534f", alpha=0.6, label="rejected heat Qc" if i == 0 else None)
        ax.text(i, q_hot + 15, f"efficiency {efficiency(q_hot, qc):.2f}", ha="center", fontsize=9)
        print(f"{n}: W = {w:.0f} J, efficiency = {efficiency(q_hot, qc):.2f}, allowed = {is_allowed(q_hot, qc, t_hot, t_cold)}")
    ax.axhline(q_hot, color="k", lw=1, ls="--")
    ax.text(2.45, q_hot - 60, "Qh = 1000 J", ha="right", fontsize=9)
    ax.set_xticks(range(3))
    ax.set_xticklabels(names)
    ax.set_ylabel("heat per cycle (J)")
    ax.set_ylim(0, 1150)
    ax.set_title(f"Qh = W + Qc (Carnot limit {carnot_limit(t_hot, t_cold):.2f} for 600 K and 300 K)")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "energy_split.png", dpi=120)

    # Figure 2: the area of a P-V loop is the work
    fig2, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
    for ax, (p_hi, name) in zip(axes, [(300.0, "small loop"), (500.0, "taller loop")]):
        v, p = rectangle_loop(100.0, p_hi, 1.0, 3.0)
        ax.fill(v, p, color="#2a9d8f", alpha=0.35)
        ax.plot(np.r_[v, v[0]], np.r_[p, p[0]], "k-")
        for k, lab in enumerate("1234"):
            ax.annotate(lab, (v[k], p[k]), textcoords="offset points", xytext=(6, 6))
        ax.annotate("", xy=(2.0, p_hi), xytext=(1.5, p_hi), arrowprops=dict(arrowstyle="->"))
        ax.set_title(f"{name}: W = {loop_work(v, p):.0f} J")
        ax.set_xlabel("volume V (L)")
        ax.grid(alpha=0.3)
        print(f"{name}: W = {loop_work(v, p):.0f} J")
    axes[0].set_ylabel("pressure P (kPa)")
    fig2.tight_layout()
    fig2.savefig(OUT / "pv_loop_area.png", dpi=120)

# %% [markdown]
# ## Where this stops
# A rectangle is not what a real engine draws. Session 2 builds the real shapes (the Otto and
# Diesel cycles) from the gas laws and gets their efficiency from a formula.
