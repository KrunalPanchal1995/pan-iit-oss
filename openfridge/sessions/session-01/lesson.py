"""Session 1 (Level 1): a refrigerator moves heat uphill, and it needs work to do it.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a refrigerator moves heat uphill, and it needs work to do it
# **A. Real-world problem.** Put a warm drink on the table and it cools down by itself.
# Heat always flows from warm to cold. A refrigerator does the opposite: it keeps its inside
# colder than the kitchen. Why does it have to be plugged in?
#
# **Plan.** (1) learn the four parts, (2) write the energy balance, (3) define the COP
# (coefficient of performance), (4) see that without work nothing moves.
#
# Educational model: simplified numbers, not a design tool for real appliances.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

PARTS = [
    ("evaporator", "liquid boils at low pressure and takes heat from the inside"),
    ("compressor", "the electric motor squeezes the vapour; this is where the work W goes in"),
    ("condenser", "the hot compressed vapour gives heat to the kitchen and turns back to liquid"),
    ("expansion valve", "a narrow opening drops the pressure so the liquid becomes cold again"),
]


# %% [markdown]
# ## Step 1: the energy balance
# Over one full turn of the loop the fluid ends where it started, so it stores no energy.
# Energy in must equal energy out:
#
#     Q_hot = Q_cold + W
#
# * `Q_cold` is the heat taken from the cold inside (kJ),
# * `W` is the work put in by the compressor (kJ),
# * `Q_hot` is the heat given to the warm kitchen (kJ).

# %%
def heat_to_room(q_cold, work):
    """Energy balance of one cycle: Q_hot = Q_cold + W (all in the same unit)."""
    if q_cold < 0 or work < 0:
        raise ValueError("heat and work are amounts here, so they cannot be negative")
    return q_cold + work


def cop(q_cold, work):
    """Coefficient of performance = heat removed per unit of work. Needs work > 0."""
    if work <= 0:
        raise ValueError("with no work there is no refrigeration: COP is not defined")
    return q_cold / work


def cooling_from_work(work, cop_value):
    """Heat removed from the inside when `work` is used by a fridge with this COP."""
    return cop_value * work


# %% [markdown]
# ## Step 2: how much must a fridge remove?
# In steady state the inside stays at the same temperature, so the fridge must remove exactly
# the heat that leaks in through the walls. Leak power = UA x (T_room - T_inside), where UA
# (W per kelvin) says how leaky the walls are.

# %%
def wall_leak_watts(ua, t_room, t_inside):
    """Heat leaking in through the walls, in watts (J per second)."""
    return ua * (t_room - t_inside)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # worked example numbers: 300 J removed using 100 J of work
    qc, w = 300.0, 100.0
    qh = heat_to_room(qc, w)
    print(f"Q_cold = {qc:.0f} J, W = {w:.0f} J -> Q_hot = {qh:.0f} J, COP = {cop(qc, w):.2f}")
    leak = wall_leak_watts(2.0, 25.0, 4.0)
    print(f"wall leak with UA = 2.0 W/K, 25 C kitchen, 4 C inside: {leak:.0f} W")

    fig, ax = plt.subplots(figsize=(6, 4))
    names = ["Q_cold\n(from inside)", "W\n(compressor)", "Q_hot\n(to kitchen)"]
    ax.bar(names, [qc, w, qh], color=["tab:blue", "tab:orange", "tab:red"])
    for i, v in enumerate([qc, w, qh]):
        ax.text(i, v + 6, f"{v:.0f} J", ha="center")
    ax.set_ylabel("energy per cycle (J)")
    ax.set_title("Energy flows of one cycle: Q_hot = Q_cold + W")
    ax.set_ylim(0, 480)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "energy_flow.png", dpi=120)

    work = np.linspace(0, 5, 51)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for c, col in ((2.0, "tab:green"), (3.0, "tab:blue"), (4.0, "tab:purple")):
        ax2.plot(work, cooling_from_work(work, c), color=col, label=f"heat removed, COP = {c:.0f}")
    ax2.plot(work, work, "k--", label="work put in (W)")
    ax2.set_xlabel("work W (kJ)")
    ax2.set_ylabel("heat removed from inside, Q_cold (kJ)")
    ax2.set_title("No work, no cooling; more work, more heat moved")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "cooling_vs_work.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We have not asked how large the COP can be. Session 2 answers: there is a limit set by the
# two temperatures, and it is why a hot kitchen costs more to cool against.
