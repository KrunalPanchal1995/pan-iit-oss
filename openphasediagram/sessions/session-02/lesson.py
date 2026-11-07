"""Session 2 (Level 2): the lever rule on an isomorphous (Cu-Ni style) diagram.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: tie lines and the lever rule
# **A. Real-world problem.** A foundry wants a casting that is exactly half liquid and half solid
# (a "semi-solid" slurry that can be pressed into shape). Which alloy composition and which
# temperature give that? Session 1 told us only the region; today we get numbers: how much
# of each phase there is, and what each phase is made of.
#
# **Illustrative diagram.** As in Session 1 the liquidus and solidus are straight-line pieces
# between Cu 1085 C and Ni 1455 C. They are for teaching, not the measured Cu-Ni diagram.
# Composition is in weight percent (wt%) Ni.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

X_NODES = np.array([0.0, 50.0, 100.0])
LIQ_NODES = np.array([1085.0, 1320.0, 1455.0])    # liquidus temperatures (C) at those compositions
SOL_NODES = np.array([1085.0, 1240.0, 1455.0])    # solidus temperatures (C)


def liquidus(x):
    return np.interp(x, X_NODES, LIQ_NODES)


def solidus(x):
    return np.interp(x, X_NODES, SOL_NODES)


# %% [markdown]
# ## Step 1: read the phase compositions off a tie line
# At temperature T draw a horizontal line (a *tie line*) through the two-phase band.
# Where it meets the liquidus the liquid has composition C_L; where it meets the solidus the
# solid has composition C_S. We find them by reading the boundary lines *sideways*:
# the inverse of "temperature at composition" is "composition at temperature".

# %%
def liquid_composition(T):
    """C_L: composition (wt% Ni) of the liquid on the liquidus at temperature T."""
    return float(np.interp(T, LIQ_NODES, X_NODES))


def solid_composition(T):
    """C_S: composition (wt% Ni) of the solid on the solidus at temperature T."""
    return float(np.interp(T, SOL_NODES, X_NODES))


# %% [markdown]
# ## Step 2: the lever rule (derived)
# Let the alloy have overall composition C0 and let a fraction f_L be liquid, f_S = 1 - f_L solid.
# *Nickel is conserved.* The Ni carried by the liquid plus the Ni carried by the solid is all the Ni:
#
#     C0 = f_L * C_L + (1 - f_L) * C_S
#
# Solve for f_L:   C0 - C_S = f_L (C_L - C_S)   so
#
#     f_L = (C_S - C0) / (C_S - C_L)      f_S = (C0 - C_L) / (C_S - C_L)
#
# In words: the fraction of a phase is the *opposite arm* of the tie line divided by the *whole*
# tie line. The liquid fraction uses the arm from C0 to C_S (the far end).

# %%
def tie_line(C0, T):
    """Return (C_L, C_S, f_L, f_S) for alloy C0 at temperature T (C)."""
    tl, ts = float(liquidus(C0)), float(solidus(C0))
    if T >= tl:
        return C0, float("nan"), 1.0, 0.0       # fully liquid: no solid yet
    if T <= ts:
        return float("nan"), C0, 0.0, 1.0       # fully solid
    cl, cs = liquid_composition(T), solid_composition(T)
    fl = (cs - C0) / (cs - cl)
    return cl, cs, fl, 1.0 - fl


def liquid_fraction(C0, T):
    return tie_line(C0, T)[2]


# %% [markdown]
# ## Step 3: the inverse (design) problem
# * Fixed composition, find the temperature for a wanted liquid fraction: f_L falls from 1 at the
#   liquidus to 0 at the solidus, so bisection finds T.
# * Fixed temperature, find the composition: a 50 percent liquid alloy sits exactly in the
#   middle of the tie line, C0 = (C_L + C_S) / 2. More generally C0 = f_L C_L + (1 - f_L) C_S.

# %%
def temperature_for_liquid_fraction(C0, target):
    """Temperature (C) where alloy C0 has liquid fraction `target` (0 < target < 1)."""
    lo, hi = float(solidus(C0)), float(liquidus(C0))
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if liquid_fraction(C0, mid) > target:      # too liquid: go colder
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def composition_for_liquid_fraction(T, target):
    """Overall composition C0 giving liquid fraction `target` at temperature T (on the tie line)."""
    return target * liquid_composition(T) + (1.0 - target) * solid_composition(T)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    C0, T = 50.0, 1280.0
    cl, cs, fl, fs = tie_line(C0, T)
    print(f"alloy {C0:.0f} wt% Ni at {T:.0f} C: C_L = {cl:.1f}, C_S = {cs:.1f}, f_L = {fl:.3f}, f_S = {fs:.3f}")
    print(f"50% liquid for C0 = 50: T = {temperature_for_liquid_fraction(50.0, 0.5):.1f} C")
    for Tq in (1250, 1300, 1350):
        print(f"50% liquid at {Tq} C needs C0 = {composition_for_liquid_fraction(Tq, 0.5):.1f} wt% Ni")

    xs = np.linspace(0, 100, 201)
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.plot(xs, liquidus(xs), "r-", label="liquidus")
    ax.plot(xs, solidus(xs), "b-", label="solidus")
    ax.plot([cl, cs], [T, T], "k-", lw=2, label="tie line")
    ax.plot([C0], [T], "ko")
    ax.annotate("C_L", (cl, T), xytext=(cl - 6, T + 18))
    ax.annotate("C0", (C0, T), xytext=(C0 - 2, T - 32))
    ax.annotate("C_S", (cs, T), xytext=(cs + 1, T + 18))
    ax.set_xlabel("composition (weight percent Ni)")
    ax.set_ylabel("temperature (C)")
    ax.set_title(f"Tie line at {T:.0f} C: f_L = {fl:.2f}, f_S = {fs:.2f}")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "tie_line.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.2, 4.4))
    for c in (30.0, 50.0, 70.0):
        Ts = np.linspace(float(solidus(c)), float(liquidus(c)), 100)
        ax2.plot(Ts, [liquid_fraction(c, t) for t in Ts], label=f"C0 = {c:.0f} wt% Ni")
    ax2.set_xlabel("temperature (C)")
    ax2.set_ylabel("liquid fraction f_L")
    ax2.set_title("Liquid fraction falls from 1 to 0 across the band")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "liquid_fraction.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The lever rule assumes the phases always reach equilibrium (every atom has time to move).
# Session 3 simulates cooling, adds a eutectic, and shows when this assumption breaks.
