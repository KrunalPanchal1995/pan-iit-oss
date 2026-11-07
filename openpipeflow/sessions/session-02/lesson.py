"""Session 2 (Level 2): friction loss, Reynolds number and the pump power for a pipe.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: friction loss, Reynolds number and pump power
# **A. Real-world problem.** A pump must push water through a long pipe. A thin pipe is cheap
# but the water rubs against the wall and the pump must work hard; a fat pipe costs more but
# wastes less energy. How do we put a number on the friction, and find the smallest pipe that
# keeps the pump within its power budget?
#
# **Plan.** (1) Reynolds number: is the flow smooth or turbulent?, (2) friction factor,
# (3) Darcy-Weisbach head loss plus minor losses, (4) pump power, (5) design: choose the
# smallest standard diameter within the budget. Educational model, not a design tool.

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

RHO = 998.0      # water density at 20 C, kg/m^3
NU = 1.0e-6      # kinematic viscosity of water at 20 C, m^2/s
G = 9.81         # gravity, m/s^2


# %% [markdown]
# ## Step 1: Reynolds number
# Re = v D / nu compares the push of the moving water (inertia) with its stickiness
# (viscosity). Below about 2000 the flow is smooth layers (laminar); above about 4000 it is
# churning (turbulent); in between nobody can predict it well.

# %%
def velocity(q, d):
    """Average speed (m/s) for flow q (m^3/s) in a round pipe of inside diameter d (m)."""
    return 4.0 * q / (math.pi * d ** 2)


def reynolds(q, d, nu=NU):
    """Reynolds number (no unit)."""
    return velocity(q, d) * d / nu


# %% [markdown]
# ## Step 2: friction factor f
# * Laminar (Re < 2000): f = 64 / Re, exact.
# * Turbulent (Re > 4000): the Swamee-Jain formula, with relative roughness e/D
#   (e = height of the wall bumps):  f = 0.25 / [log10( e/(3.7 D) + 5.74 / Re^0.9 )]^2
# * Between 2000 and 4000 we simply join the two with a straight line (a modelling choice).
#
# `colebrook` is the older, slower formula that needs iteration; it is our reference.

# %%
def friction_factor(re, rel_rough):
    """Darcy friction factor (no unit) for Reynolds number re and relative roughness e/D."""
    def turbulent(r):
        return 0.25 / math.log10(rel_rough / 3.7 + 5.74 / r ** 0.9) ** 2
    if re < 2000.0:
        return 64.0 / re
    if re > 4000.0:
        return turbulent(re)
    w = (re - 2000.0) / 2000.0
    return (1 - w) * (64.0 / 2000.0) + w * turbulent(4000.0)


def colebrook(re, rel_rough, iterations=60):
    """Reference turbulent friction factor from the Colebrook-White equation (fixed-point iteration)."""
    f = 0.02
    for _ in range(iterations):
        f = 1.0 / (-2.0 * math.log10(rel_rough / 3.7 + 2.51 / (re * math.sqrt(f)))) ** 2
    return f


# %% [markdown]
# ## Step 3: head loss
# Head is energy per unit weight of water, written as a height in metres. Friction along the
# pipe (Darcy-Weisbach) and bends, valves and entrances ("minor losses", K is their total
# loss coefficient) each cost head:
#
#     h_f = f (L / D) v^2 / (2 g)         h_m = K v^2 / (2 g)

# %%
def head_loss(q, d, length, rough, k_minor=0.0, nu=NU):
    """Total friction + minor head loss (m). rough = wall roughness e in metres."""
    v = velocity(q, d)
    f = friction_factor(reynolds(q, d, nu), rough / d)
    return (f * length / d + k_minor) * v ** 2 / (2 * G)


# %% [markdown]
# ## Step 4: pump power
# The pump lifts the water by the static rise `lift` and also pays the head loss:
# H = lift + h_loss. Water power = rho g Q H (watts). A real pump and motor waste some,
# so the electric power is water power divided by the efficiency eta.

# %%
def pump_head(q, d, length, rough, lift, k_minor=0.0, nu=NU):
    return lift + head_loss(q, d, length, rough, k_minor, nu)


def pump_power(q, d, length, rough, lift, k_minor=0.0, eta=0.65, nu=NU):
    """Electric power (W) the pump needs."""
    return RHO * G * q * pump_head(q, d, length, rough, lift, k_minor, nu) / eta


# %% [markdown]
# ## Step 5: design
# Pipes come in standard sizes. The power falls steeply as the diameter grows (v falls, so
# v^2 falls, and the friction term has 1/D on top). The smallest diameter inside the budget
# is usually the cheapest pipe that works. We also keep v below 3 m/s (noise, wear).

# %%
STANDARD_MM = [50, 65, 80, 100, 125, 150, 200, 250, 300]


def smallest_diameter(budget_w, q, length, rough, lift, k_minor=0.0, eta=0.65, vmax=3.0, sizes_mm=STANDARD_MM):
    """Smallest standard diameter (mm) with electric power <= budget and speed <= vmax, or None."""
    for mm in sizes_mm:
        d = mm / 1000.0
        if velocity(q, d) <= vmax and pump_power(q, d, length, rough, lift, k_minor, eta) <= budget_w:
            return mm
    return None


# %% [markdown]
# ## Step 6: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    q, length, rough, lift, k, eta = 0.020, 500.0, 0.00015, 10.0, 5.0, 0.65
    budget = 7000.0
    print(f"{'D (mm)':>7} {'v (m/s)':>8} {'Re':>9} {'f':>7} {'h_loss (m)':>11} {'power (kW)':>11}")
    for mm in STANDARD_MM:
        d = mm / 1000.0
        print(f"{mm:7d} {velocity(q, d):8.2f} {reynolds(q, d):9.0f} "
              f"{friction_factor(reynolds(q, d), rough / d):7.4f} {head_loss(q, d, length, rough, k):11.2f} "
              f"{pump_power(q, d, length, rough, lift, k, eta) / 1e3:11.2f}")
    print("smallest diameter within", budget / 1e3, "kW:", smallest_diameter(budget, q, length, rough, lift, k, eta), "mm")

    dd = np.linspace(0.06, 0.30, 100)
    pw = [pump_power(q, d, length, rough, lift, k, eta) / 1e3 for d in dd]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(dd * 1000, pw, label="pump electric power")
    ax.axhline(budget / 1e3, color="tab:red", ls="--", label="budget 7 kW")
    ax.set_ylim(0, 30)
    ax.set_xlabel("pipe inside diameter (mm)")
    ax.set_ylabel("pump electric power (kW)")
    ax.set_title("Power falls steeply as the pipe grows (20 L/s, 500 m)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "power_vs_diameter.png", dpi=120)

    res = np.logspace(2.5, 7, 200)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for rr in (1e-5, 1e-3, 1e-2):
        ax2.loglog(res, [friction_factor(r, rr) for r in res], label=f"e/D = {rr:g}")
    ax2.set_xlabel("Reynolds number (no unit)")
    ax2.set_ylabel("friction factor f (no unit)")
    ax2.set_title("Friction factor: laminar line, transition, turbulent curves")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "friction_factor.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
