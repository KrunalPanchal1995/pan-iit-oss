"""Session 2 (Level 2): the real ethanol-water equilibrium and the azeotrope.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: real vapour pressures, real equilibrium, and a wall at 89 percent
# **A. Real-world problem.** Session 1 used one constant relative volatility. Real
# ethanol-water mixtures behave very differently at the dilute end and near the top. At what
# temperature does the wash boil, and what vapour comes off? Why can no ordinary column at
# atmospheric pressure make pure ethanol, and why does bottled "rectified spirit" stop near
# 95 percent by volume?
#
# **Plan.** (1) vapour pressure from the Antoine equation, (2) Raoult's law for an ideal
# mixture, (3) activity coefficients (van Laar) for the real, non-ideal mixture, (4) the bubble
# point: solve for T, (5) T-x-y and x-y diagrams, the azeotrope and the local alpha,
# (6) a single equilibrium stage: the flash and the lever rule.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
P_ATM = 760.0                                 # mmHg (= 101.325 kPa)
MMHG_PER_KPA = 760.0 / 101.325

# Antoine constants, log10(Psat / mmHg) = A - B / (T + C), T in degrees C (common textbook values)
ANTOINE = {"ethanol": (8.20417, 1642.89, 230.300), "water": (8.07131, 1730.63, 233.426)}
# van Laar constants (natural log of the activity coefficient at infinite dilution)
VAN_LAAR = (1.6798, 0.9227)


# %% [markdown]
# ## Step 1: vapour pressure (Antoine)
# The vapour pressure of a pure liquid is the pressure at which it boils at temperature T.
# It rises steeply with T:
#
#     log10(Psat / mmHg) = A - B / (T + C)        (T in degrees C)
#
# A liquid boils when its vapour pressure equals the pressure above it (760 mmHg at sea level).

# %%
def psat(t_c, component):
    """Vapour pressure in mmHg at temperature t_c (degrees C)."""
    a, b, c = ANTOINE[component]
    return 10.0 ** (a - b / (np.asarray(t_c, float) + c))


def boiling_point(component, p=P_ATM):
    """Pure-component boiling point (degrees C) at pressure p (mmHg): invert Antoine."""
    a, b, c = ANTOINE[component]
    return b / (a - np.log10(p)) - c


# %% [markdown]
# ## Step 2: Raoult's law and activity coefficients
# In an **ideal** mixture each component's partial pressure is its liquid mole fraction
# times its vapour pressure (Raoult's law). Ethanol and water are not ideal: the molecules
# prefer their own kind, so each one escapes more easily than Raoult predicts. We multiply by an
# **activity coefficient** gamma >= 1 (van Laar model):
#
#     y1 P = x1 gamma1 Psat1(T)          y2 P = x2 gamma2 Psat2(T)
#     ln gamma1 = A12 (A21 x2 / (A12 x1 + A21 x2))**2
#     ln gamma2 = A21 (A12 x1 / (A12 x1 + A21 x2))**2
#
# Setting A12 = A21 = 0 gives gamma = 1 and Raoult's ideal law back.

# %%
def activity(x, a12=VAN_LAAR[0], a21=VAN_LAAR[1]):
    """van Laar activity coefficients (gamma_ethanol, gamma_water) at liquid ethanol fraction x."""
    x = np.asarray(x, float)
    if a12 == 0 and a21 == 0:
        return np.ones_like(x), np.ones_like(x)
    x2 = 1.0 - x
    d = a12 * x + a21 * x2
    return np.exp(a12 * (a21 * x2 / d) ** 2), np.exp(a21 * (a12 * x / d) ** 2)


# %% [markdown]
# ## Step 3: the bubble point
# Given the liquid x and the pressure P, find the temperature where the partial pressures add
# up to P. The sum rises with T, so we can bisect: too much pressure means T is too high.
#
#     x1 gamma1 Psat1(T) + x2 gamma2 Psat2(T) = P        then  y1 = x1 gamma1 Psat1(T) / P

# %%
def bubble_point(x, p=P_ATM, ideal=False):
    """Bubble temperature (degrees C) and vapour fraction y for liquid ethanol fraction x."""
    x = float(x)
    if not 0.0 <= x <= 1.0:
        raise ValueError("mole fraction must be between 0 and 1")
    if p <= 0:
        raise ValueError("pressure must be positive")
    g1, g2 = activity(x, *((0.0, 0.0) if ideal else VAN_LAAR))
    lo, hi = -50.0, 250.0
    for _ in range(80):
        t = 0.5 * (lo + hi)
        if x * g1 * psat(t, "ethanol") + (1 - x) * g2 * psat(t, "water") > p:
            hi = t
        else:
            lo = t
    t = 0.5 * (lo + hi)
    return t, float(x * g1 * psat(t, "ethanol") / p)


def equilibrium_curve(n=401, p=P_ATM, ideal=False):
    """Arrays x, y, T along the bubble-point curve."""
    xs = np.linspace(0.0, 1.0, n)
    ty = np.array([bubble_point(x, p, ideal) for x in xs])
    return xs, ty[:, 1], ty[:, 0]


def local_alpha(x, p=P_ATM, ideal=False):
    """Relative volatility (y/(1-y)) / (x/(1-x)) at liquid x (0 < x < 1)."""
    _, y = bubble_point(x, p, ideal)
    return (y / (1 - y)) / (x / (1 - x))


def azeotrope(p=P_ATM, ideal=False):
    """Composition and temperature where y = x (None if there is no azeotrope). Bisection on y - x."""
    xs, ys, _ = equilibrium_curve(201, p, ideal)
    d = ys - xs
    idx = np.where((d[1:-2] > 0) & (d[2:-1] <= 0))[0]
    if idx.size == 0:
        return None
    lo, hi = xs[idx[0] + 1], xs[idx[0] + 2]
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if bubble_point(mid, p, ideal)[1] - mid > 0:
            lo = mid
        else:
            hi = mid
    x = 0.5 * (lo + hi)
    return x, bubble_point(x, p, ideal)[0]


# %% [markdown]
# ## Step 4: one equilibrium stage (a flash) and the lever rule
# Heat a feed of composition z until a fraction of it, V/F, has boiled, and let the vapour and
# liquid reach equilibrium. The liquid has composition x, the vapour y = y(x). The ethanol balance
# F z = V y + L x gives the **lever rule**: V/F = (z - x) / (y - x).
# We pick the temperature (between the bubble and dew points) by choosing x: every x below z
# defines one possible flash.

# %%
def flash_from_liquid(z, x, p=P_ATM):
    """Single-stage flash: given feed z and the liquid x left behind, return (V/F, y, T)."""
    if not 0 < x <= z < 1:
        raise ValueError("need 0 < x <= z < 1")
    t, y = bubble_point(x, p)
    if y <= x:
        raise ValueError("no enrichment at this composition (at or beyond the azeotrope)")
    return (z - x) / (y - x), y, t


MW = (46.07, 18.015)                          # g/mol, ethanol and water


def mass_percent(x):
    """Ethanol mole fraction to mass percent (exact: mass does not shrink on mixing)."""
    m1, m2 = x * MW[0], (1 - x) * MW[1]
    return 100.0 * m1 / (m1 + m2)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"boiling points at 1 atm: ethanol {boiling_point('ethanol'):.2f} C, water {boiling_point('water'):.2f} C")
    t, y = bubble_point(0.10)
    g1, g2 = activity(0.10)
    print(f"worked example x = 0.10: T = {t:.2f} C, Psat ethanol {psat(t, 'ethanol'):.1f}, water {psat(t, 'water'):.1f} mmHg,"
          f" gamma {g1:.3f}, {g2:.4f}, y = {y:.4f}, alpha = {local_alpha(0.10):.2f}")
    ti, yi = bubble_point(0.10, ideal=True)
    print(f"ideal (Raoult) x = 0.10: T = {ti:.2f} C, y = {yi:.4f}")
    xa, ta = azeotrope()
    print(f"azeotrope (model): x = {xa:.3f} at {ta:.2f} C  ({mass_percent(xa):.1f} % by mass); measured: x = 0.894 at 78.15 C (95.6 % by mass)")
    print("ideal mixture has an azeotrope:", azeotrope(ideal=True) is not None)
    for x in (0.02, 0.1, 0.3, 0.6, 0.85):
        print(f"local alpha at x = {x}: {local_alpha(x):.2f}")
    vf, yf, tf = flash_from_liquid(0.10, 0.05)
    print(f"flash z = 0.10 down to x = 0.05: V/F = {vf:.3f}, y = {yf:.3f}, T = {tf:.1f} C")

    xs, ys, ts = equilibrium_curve()
    xi, yi_, ti_ = equilibrium_curve(ideal=True)

    # Figure 1: T-x-y diagram
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.plot(xs, ts, color="#264653", label="bubble line (liquid, x)")
    ax.plot(ys, ts, color="#d9534f", label="dew line (vapour, y)")
    ax.plot(xi, ti_, color="#264653", ls=":", lw=1, label="ideal Raoult bubble line")
    ax.plot(yi_, ti_, color="#d9534f", ls=":", lw=1, label="ideal Raoult dew line")
    t1, y1 = bubble_point(0.10)
    ax.plot([0.10, y1], [t1, t1], "k--", lw=1)
    ax.annotate(f"x = 0.10 boils at {t1:.1f} C\nvapour y = {y1:.2f}", (y1, t1), textcoords="offset points", xytext=(8, 4), fontsize=8)
    ax.plot([xa], [ta], "o", color="#e9a23b")
    ax.annotate(f"azeotrope x = {xa:.2f}, {ta:.1f} C", (xa, ta), textcoords="offset points", xytext=(-150, 14), fontsize=8)
    ax.set_xlabel("ethanol mole fraction, x or y")
    ax.set_ylabel("temperature (degrees C)")
    ax.set_title("Ethanol-water at 1 atm: T-x-y diagram")
    ax.set_xlim(0, 1)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "txy.png", dpi=120)

    # Figure 2: x-y diagram and local alpha
    fig2, (axl, axr) = plt.subplots(1, 2, figsize=(10, 4.4))
    axl.plot(xs, ys, color="#2a9d8f", label="van Laar (real)")
    axl.plot(xi, yi_, color="#2a9d8f", ls=":", label="Raoult (ideal)")
    axl.plot([0, 1], [0, 1], "k", lw=1, label="y = x")
    axl.plot([xa], [xa], "o", color="#e9a23b")
    axl.set_xlabel("ethanol in liquid, x (mole fraction)")
    axl.set_ylabel("ethanol in vapour, y (mole fraction)")
    axl.set_title("x-y diagram: the curve crosses y = x")
    axl.legend(fontsize=8, loc="lower right")
    axl.grid(alpha=0.3)
    xa_ = np.linspace(0.01, 0.99, 99)
    axr.plot(xa_, [local_alpha(x) for x in xa_], color="#2a9d8f", label="van Laar (real)")
    axr.plot(xa_, [local_alpha(x, ideal=True) for x in xa_], color="#2a9d8f", ls=":", label="Raoult (ideal)")
    axr.axhline(1.0, color="k", lw=1)
    axr.set_yscale("log")
    axr.set_xlabel("ethanol in liquid, x (mole fraction)")
    axr.set_ylabel("local relative volatility alpha (log scale)")
    axr.set_title("alpha falls from about 10 to below 1")
    axr.legend(fontsize=8)
    axr.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "xy_alpha.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We now have the real equilibrium curve. Session 3 stacks equilibrium stages into a column
# with reflux, steps them off on the x-y diagram (McCabe-Thiele) and designs a real column.
