"""Session 2 (Level 2): cycle temperatures, net work and the best pressure ratio.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: temperatures, work and the best pressure ratio
# **A. Real-world problem.** A power-station turbine takes in 20 kg of air every second at
# 288 K. The metal of the turbine can survive gas at 1400 K. What are the temperatures at
# each point of the engine, how much power comes out, and which pressure ratio gives the most?
#
# Educational model: ideal Brayton cycle, air with constant properties, no losses, no fuel
# mass. Not a design tool for real engines.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
GAMMA = 1.4        # ratio of specific heats (no unit)
CP = 1.005         # specific heat of air at constant pressure (kJ per kg per K)
K = (GAMMA - 1) / GAMMA


# %% [markdown]
# ## Step 1: temperatures at the four states
# State 1 is the inlet, 2 the compressor exit, 3 the turbine inlet (the hottest point) and
# 4 the turbine exit. Compression and expansion are ideal (no entropy change), so
#
#     T2 = T1 x r^K        T4 = T3 / r^K

# %%
def temperatures(t1, r, t3):
    """Return (T2, T4) in kelvin for inlet T1, pressure ratio r and turbine inlet T3."""
    if r < 1:
        raise ValueError("the pressure ratio must be at least 1")
    x = r ** K
    if t3 <= t1 * x:
        raise ValueError("T3 must be hotter than T2, otherwise the combustor cools the air")
    return t1 * x, t3 / x


# %% [markdown]
# ## Step 2: work and heat per kilogram of air
# With constant cp, each heat or work is cp times a temperature difference:
#
#     w_c = cp (T2 - T1)        compressor work in
#     w_t = cp (T3 - T4)        turbine work out
#     w_net = w_t - w_c         net work
#     q_in = cp (T3 - T2)       heat added in the combustor
#     eta = w_net / q_in        (this equals 1 - 1 / r^K from Session 1)

# %%
def cycle_work(t1, r, t3):
    """Return a dictionary of work and heat per kg of air (kJ/kg) and the efficiency."""
    t2, t4 = temperatures(t1, r, t3)
    w_c, w_t, q_in = CP * (t2 - t1), CP * (t3 - t4), CP * (t3 - t2)
    return {"t2": t2, "t4": t4, "w_c": w_c, "w_t": w_t, "w_net": w_t - w_c, "q_in": q_in, "eta": (w_t - w_c) / q_in}


def power_mw(mdot, t1, r, t3):
    """Net power in megawatts for an air flow mdot in kg/s (kJ/kg x kg/s = kW)."""
    return mdot * cycle_work(t1, r, t3)["w_net"] / 1000


# %% [markdown]
# ## Step 3: the pressure ratio that gives the most work
# Write x = r^K and tau = T3 / T1. Then w_net = cp T1 [tau (1 - 1/x) - (x - 1)]. Setting the
# derivative with respect to x to zero gives x = sqrt(tau), so
#
#     r_opt = (T3 / T1)^(1 / (2K))
#
# Below r_opt the cycle is wasting hot gas, above it the compressor eats too much work.

# %%
def best_ratio_for_work(t1, t3):
    return (t3 / t1) ** (1 / (2 * K))


def max_ratio(t1, t3):
    """Largest r for which T2 does not exceed T3 (the combustor would have nothing to do)."""
    return (t3 / t1) ** (1 / K)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t1, t3, mdot = 288, 1400, 20
    c = cycle_work(t1, 10, t3)
    print(f"r = 10: T2 = {c['t2']:.1f} K, T4 = {c['t4']:.1f} K")
    print(f"w_c = {c['w_c']:.1f}, w_t = {c['w_t']:.1f}, w_net = {c['w_net']:.1f} kJ/kg, eta = {c['eta']:.4f}")
    print(f"power for {mdot} kg/s = {power_mw(mdot, t1, 10, t3):.2f} MW")
    print(f"best r for work = {best_ratio_for_work(t1, t3):.1f}; largest possible r = {max_ratio(t1, t3):.0f}")

    r = np.linspace(2, 40, 190)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for t3x, col in ((1200, "tab:green"), (1400, "tab:blue"), (1600, "tab:red")):
        ax.plot(r, [cycle_work(t1, x, t3x)["w_net"] for x in r], color=col, label=f"T3 = {t3x} K")
        ro = best_ratio_for_work(t1, t3x)
        ax.plot(ro, cycle_work(t1, ro, t3x)["w_net"], "o", color=col)
    ax.set_xlabel("pressure ratio r (no unit)")
    ax.set_ylabel("net work (kJ per kg of air)")
    ax.set_title("Each curve peaks at its own best pressure ratio (dots)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "work_vs_ratio.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(r, [cycle_work(t1, x, t3)["t2"] for x in r], color="tab:blue", label="T2 (compressor exit)")
    ax2.plot(r, [cycle_work(t1, x, t3)["t4"] for x in r], color="tab:red", label="T4 (turbine exit)")
    ax2.axhline(t3, color="gray", ls=":", label="T3 = 1400 K")
    ax2.set_xlabel("pressure ratio r (no unit)")
    ax2.set_ylabel("temperature (K)")
    ax2.set_title("Compressor exit gets hotter, turbine exit gets cooler")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "temperatures_vs_ratio.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real compressors and turbines do not reach the ideal temperatures: each needs more work
# than the ideal one. Session 3 adds their efficiencies and uses what is left of the gas to
# make thrust.
