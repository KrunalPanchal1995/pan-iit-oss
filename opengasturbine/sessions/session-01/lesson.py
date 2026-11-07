"""Session 1 (Level 1): how a gas turbine turns fuel into power: four parts, the energy balance and the efficiency.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: four parts, one energy balance
# **A. Real-world problem.** A jet engine or a power-station gas turbine burns fuel to make
# power. Only part of the fuel's heat becomes useful work, and the rest leaves in the hot
# exhaust. How much work can we get, and why does a higher pressure ratio help?
#
# **Plan.** (1) learn the four parts, (2) write the energy balance, (3) define the efficiency,
# (4) see how the pressure ratio changes it.
#
# Educational model: air as an ideal gas with constant properties, no losses. Not a design
# tool for real engines.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
GAMMA = 1.4                    # ratio of specific heats of air (no unit)
K = (GAMMA - 1) / GAMMA        # exponent that links pressure ratio and temperature ratio

PARTS = [
    ("compressor", "squeezes the incoming air to a higher pressure; this takes work w_c"),
    ("combustor", "burns fuel in the compressed air; this is where the heat q_in goes in"),
    ("turbine", "the hot gas expands through it and gives work w_t"),
    ("exhaust", "the gas leaves hot; the heat q_out is lost to the surroundings"),
]


# %% [markdown]
# ## Step 1: the four parts and the energy balance
# Follow one kilogram of air through the engine. Heat q_in is added in the combustor.
# The turbine gives more work than the compressor takes, and the difference is the net work
# w_net. Over a complete cycle the air returns to its start, so energy in equals energy out:
#
#     w_net = q_in - q_out
#
# The thermal efficiency is the useful work divided by the heat paid for:
#
#     eta = w_net / q_in

# %%
def show_parts():
    for name, job in PARTS:
        print(f"{name:11s} {job}")


# %% [markdown]
# ## Step 2: the ideal efficiency depends only on the pressure ratio
# For the ideal cycle (the Brayton cycle) the compression ratio r = p2 / p1 alone sets the
# efficiency:
#
#     eta = 1 - 1 / r^K       with K = (gamma - 1) / gamma = 0.2857 for air
#
# Doubling r does not double eta: the gain gets smaller and smaller.

# %%
def ideal_efficiency(r):
    """Ideal Brayton efficiency (no unit) for a pressure ratio r of at least 1."""
    if np.any(np.asarray(r) < 1):
        raise ValueError("the pressure ratio must be at least 1")
    return 1 - 1 / np.asarray(r, dtype=float) ** K if np.ndim(r) else 1 - 1 / float(r) ** K


def energy_balance(q_in, r):
    """Net work and rejected heat (both in kJ per kg of air) for heat q_in and pressure ratio r."""
    w_net = ideal_efficiency(r) * q_in
    return w_net, q_in - w_net


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    show_parts()
    r0, q0 = 10, 600
    w, q_out = energy_balance(q0, r0)
    print(f"\nr = {r0}, heat in {q0} kJ/kg -> efficiency {ideal_efficiency(r0):.3f}, net work {w:.0f} kJ/kg, heat out {q_out:.0f} kJ/kg")

    r = np.linspace(1, 40, 200)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(r, ideal_efficiency(r) * 100, color="tab:blue")
    ax.plot(r0, ideal_efficiency(r0) * 100, "o", color="tab:red", label=f"r = {r0}: {ideal_efficiency(r0) * 100:.1f} %")
    ax.set_xlabel("pressure ratio r (no unit)")
    ax.set_ylabel("ideal thermal efficiency (percent)")
    ax.set_title("More pressure helps, with smaller and smaller gains")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "efficiency_vs_ratio.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    labels = ["heat in", "net work", "heat out"]
    ax2.bar(labels, [q0, w, q_out], color=["tab:red", "tab:green", "tab:gray"])
    for i, v in enumerate([q0, w, q_out]):
        ax2.text(i, v + 10, f"{v:.0f}", ha="center")
    ax2.set_ylabel("energy per kg of air (kJ/kg)")
    ax2.set_title(f"Energy balance at r = {r0}: in = out")
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "energy_bars.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real compressors and turbines waste part of their work, and the engine must also fit the
# metal limits of the turbine. Session 2 builds the temperatures state by state, and
# Session 3 adds real component efficiencies and the thrust of a jet engine.
