"""Session 1 (Level 1): a pure metal melts at a point, an alloy melts over a range.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: melting point versus melting range
# **A. Real-world problem.** A plumber's solder goes soft and pasty before it runs like water,
# but a bar of pure copper stays hard until one exact temperature. Why do mixtures of metals
# (alloys) melt over a range of temperatures? A *phase diagram* is the map that answers this.
#
# **Plan.** (1) draw a simple Cu-Ni style map of liquid, mushy and solid regions, (2) determine which phase is
# present at a given composition and temperature, (3) cool a melt at a steady rate and observe the
# cooling curve. The pure metal shows a flat thermal arrest; the alloy displays a continuous bend.
#
# **Important.** The diagram here is a simplified *illustration*: it uses straight lines between
# the well-known melting points (Cu 1085 C, Ni 1455 C) and is not the measured Cu-Ni diagram.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

T_CU, T_NI = 1085.0, 1455.0                 # melting points of pure Cu and pure Ni, degrees C
# composition x = weight percent Ni. Illustrative model: straight-line pieces through three points.
X_NODES = np.array([0.0, 50.0, 100.0])
LIQ_NODES = np.array([T_CU, 1320.0, T_NI])   # liquidus: above this the alloy is fully liquid
SOL_NODES = np.array([T_CU, 1240.0, T_NI])   # solidus: below this the alloy is fully solid

C_HEAT = 0.5      # specific heat, J/(g K), the same for all phases (simplification)
L_HEAT = 200.0    # latent heat of freezing, J/g (illustrative)
Q_OUT = 2.0       # heat removal rate per gram, W/g (steady)


# %% [markdown]
# ## Step 1: the two boundary lines
# The **liquidus** is the temperature where the first crystals appear on cooling; the **solidus** is
# where the last liquid disappears. Between them the metal is part solid, part liquid.

# %%
def liquidus(x):
    """Liquidus temperature (C) at x weight percent Ni."""
    return np.interp(x, X_NODES, LIQ_NODES)


def solidus(x):
    """Solidus temperature (C) at x weight percent Ni."""
    return np.interp(x, X_NODES, SOL_NODES)


def melting_range(x):
    """Width of the melting range in kelvin (zero for a pure metal)."""
    return float(liquidus(x) - solidus(x))


def region(x, T):
    """Name of the phase region at composition x (wt% Ni) and temperature T (C)."""
    if T > liquidus(x):
        return "liquid"
    if T < solidus(x):
        return "solid"
    return "liquid + solid"


# %% [markdown]
# ## Step 2: a cooling curve with an energy balance
# Take heat out at a steady rate `Q_OUT` (W per gram). The heat content (enthalpy) per gram is
#
#     H(T) = C_HEAT * T + L_HEAT * (1 - fs)
#
# where `fs` is the fraction frozen. In this first model `fs` rises in a straight line from 0 at
# the liquidus to 1 at the solidus. Time = (heat removed) / Q_OUT, so
# `t = (H_start - H(T)) / Q_OUT`. A pure metal freezes at one temperature: `fs` jumps from 0 to 1,
# H drops by L_HEAT at constant T, and the curve shows a flat arrest.

# %%
def frozen_fraction(T, x):
    """Fraction frozen at temperature T for composition x: 0 above liquidus, 1 below solidus."""
    T = np.asarray(T, dtype=float)
    tl, ts = float(liquidus(x)), float(solidus(x))
    if tl - ts < 1e-9:                     # pure metal: all-or-nothing at the melting point
        return np.where(T < tl, 1.0, 0.0)
    return np.clip((tl - T) / (tl - ts), 0.0, 1.0)


def enthalpy(T, x):
    return C_HEAT * np.asarray(T, dtype=float) + L_HEAT * (1.0 - frozen_fraction(T, x))


def temperature_from_enthalpy(H, x, lo=0.0, hi=2000.0):
    """Invert H(T) by bisection (works on a flat arrest because H never decreases with T)."""
    H = np.atleast_1d(np.asarray(H, dtype=float))
    a = np.full(H.shape, lo)
    b = np.full(H.shape, hi)
    for _ in range(60):
        m = 0.5 * (a + b)
        up = enthalpy(m, x) >= H
        b = np.where(up, m, b)
        a = np.where(up, a, m)
    return 0.5 * (a + b)


def cooling_curve(x, t_end=None, n=2000, superheat=50.0, T_final_margin=60.0):
    """Time (s) and temperature (C) while heat leaves at Q_OUT, from liquidus+superheat down
    to solidus-T_final_margin."""
    T_start = float(liquidus(x)) + superheat
    T_stop = float(solidus(x)) - T_final_margin
    H0 = float(enthalpy(T_start, x))
    H1 = float(enthalpy(T_stop, x))
    if t_end is None:
        t_end = (H0 - H1) / Q_OUT
    t = np.linspace(0.0, t_end, n)
    return t, temperature_from_enthalpy(H0 - Q_OUT * t, x)


def arrest_time(x, tol=1e-6):
    """Time (s) the curve spends flat at the pure-metal melting point (0 for an alloy)."""
    t, T = cooling_curve(x, n=40001)
    return float(np.sum(np.abs(T - liquidus(x)) < tol) * (t[1] - t[0]))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    xs = np.linspace(0, 100, 201)
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    ax.fill_between(xs, liquidus(xs), 1600, color="#f3c6a5", alpha=0.6)
    ax.fill_between(xs, solidus(xs), liquidus(xs), color="#b9d7ea", alpha=0.8)
    ax.fill_between(xs, 1000, solidus(xs), color="#d9d9d9", alpha=0.8)
    ax.plot(xs, liquidus(xs), "r-", label="liquidus")
    ax.plot(xs, solidus(xs), "b-", label="solidus")
    ax.text(12, 1470, "liquid", fontsize=11)
    ax.text(42, 1280, "liquid + solid", fontsize=9)
    ax.text(70, 1130, "solid", fontsize=11)
    ax.set_xlim(0, 100)
    ax.set_ylim(1000, 1550)
    ax.set_xlabel("composition (weight percent Ni)")
    ax.set_ylabel("temperature (C)")
    ax.set_title("Illustrative Cu-Ni style phase diagram")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "simple_diagram.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.2, 4.6))
    for x, lab in ((0.0, "pure Cu (0 wt% Ni)"), (50.0, "alloy 50 wt% Ni")):
        t, T = cooling_curve(x)
        ax2.plot(t, T, label=lab)
        print(f"{lab}: liquidus {float(liquidus(x)):.0f} C, solidus {float(solidus(x)):.0f} C, "
              f"range {melting_range(x):.0f} K, flat arrest {arrest_time(x):.0f} s")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("temperature (C)")
    ax2.set_title("Cooling curves: arrest versus slope change")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "cooling_curves.png", dpi=120)
    print("phase of 50 wt% Ni at 1400 C:", region(50, 1400), "| at 1280 C:", region(50, 1280), "| at 1200 C:", region(50, 1200))

# %% [markdown]
# ## Where this stops
# We only know which region we are in. Session 2 turns "liquid + solid" into numbers: how much of
# each, and what each is made of (the lever rule).
