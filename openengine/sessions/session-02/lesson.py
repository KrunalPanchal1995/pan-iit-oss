"""Session 2 (Level 2): the Otto and Diesel cycles and their efficiency formulas.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: Otto, Diesel and Carnot efficiency
# **A. Real-world problem.** A petrol engine and a diesel engine both squeeze air, add heat
# and let the hot gas push a piston. Which compression ratio do you need for a target
# efficiency, and why do real engines do much worse than the formula?
#
# **Plan.** (1) air as an ideal gas, (2) the isentropic process, (3) the Otto cycle, (4) the
# Diesel cycle, (5) the Carnot limit, (6) invert the formula for a design.
#
# **Model.** "Air-standard" cycles: the working fluid is air, treated as an ideal gas with
# constant gamma = 1.4; heat comes from outside instead of burning fuel; there is no friction
# and no heat loss. This is a simplified teaching model, not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_AIR = 0.287          # gas constant of air, kJ/(kg K)
GAMMA = 1.4            # ratio of specific heats for air (cp / cv)


# %% [markdown]
# ## Step 1: efficiency formulas
# **Otto** (heat added at constant volume): `eta = 1 - 1 / r**(gamma - 1)`, where
# `r = V_big / V_small` is the compression ratio.
#
# **Diesel** (heat added at constant pressure): with cut-off ratio `rho = V3 / V2` (how far
# the piston has moved while fuel burns),
# `eta = 1 - (1 / r**(gamma-1)) * (rho**gamma - 1) / (gamma * (rho - 1))`.
# As rho tends to 1 the last factor tends to 1 and Diesel becomes Otto.
#
# **Carnot** (the limit for any engine between two temperatures in kelvin): `1 - Tc / Th`.

# %%
def otto_eta(r, gamma=GAMMA):
    """Ideal Otto efficiency for compression ratio r > 1."""
    if r <= 1:
        raise ValueError("compression ratio must be above 1")
    return 1.0 - r ** (1.0 - gamma)


def cutoff_factor(rho, gamma=GAMMA):
    """(rho**gamma - 1) / (gamma * (rho - 1)), equal to 1 at rho = 1 (careful near 1)."""
    x = rho - 1.0
    if rho < 1:
        raise ValueError("cut-off ratio must be at least 1")
    if abs(x) < 1e-12:
        return 1.0
    return float(np.expm1(gamma * np.log1p(x)) / (gamma * x))


def diesel_eta(r, rho, gamma=GAMMA):
    """Ideal Diesel efficiency for compression ratio r > 1 and cut-off ratio rho >= 1."""
    if r <= 1:
        raise ValueError("compression ratio must be above 1")
    return 1.0 - r ** (1.0 - gamma) * cutoff_factor(rho, gamma)


def carnot_eta(t_cold, t_hot):
    """Carnot efficiency, temperatures in kelvin."""
    if t_cold <= 0 or t_hot < t_cold:
        raise ValueError("need 0 < Tc <= Th, both in kelvin")
    return 1.0 - t_cold / t_hot


# %% [markdown]
# ## Step 2: follow the temperatures round the cycle
# Air at state 1 has pressure P1 and temperature T1. For an ideal gas P V = R T per kg, and
# cv = R / (gamma - 1), cp = gamma cv. Along an **isentrope** (no heat, no friction)
# `T V**(gamma-1)` and `P V**gamma` stay constant. Then:
#
# * 1 to 2: isentropic compression: `T2 = T1 r**(gamma-1)`
# * 2 to 3: heat added `q_in` (kJ/kg): Otto `T3 = T2 + q_in / cv`; Diesel `T3 = T2 + q_in / cp`
# * 3 to 4: isentropic expansion back to the original volume (Otto), or `rho` times larger
#   volume at the start of the expansion (Diesel)
# * 4 to 1: heat rejected at constant volume: `q_out = cv (T4 - T1)`
#
# Efficiency from the heats: `eta = 1 - q_out / q_in`. The formulas above must agree.

# %%
def otto_temperatures(r, q_in, t1=300.0, gamma=GAMMA):
    """Temperatures T1..T4 (K) of the Otto cycle and the rejected heat q_out (kJ/kg)."""
    cv = R_AIR / (gamma - 1.0)
    t2 = t1 * r ** (gamma - 1.0)
    t3 = t2 + q_in / cv
    t4 = t3 / r ** (gamma - 1.0)
    return (t1, t2, t3, t4), cv * (t4 - t1)


def diesel_cutoff_for_heat(r, q_in, t1=300.0, gamma=GAMMA):
    """Cut-off ratio rho reached when q_in (kJ/kg) is added at constant pressure."""
    cp = gamma * R_AIR / (gamma - 1.0)
    t2 = t1 * r ** (gamma - 1.0)
    return 1.0 + q_in / (cp * t2)


def diesel_temperatures(r, q_in, t1=300.0, gamma=GAMMA):
    """Temperatures T1..T4 (K) of the Diesel cycle, the cut-off ratio and q_out (kJ/kg)."""
    cv = R_AIR / (gamma - 1.0)
    rho = diesel_cutoff_for_heat(r, q_in, t1, gamma)
    t2 = t1 * r ** (gamma - 1.0)
    t3 = rho * t2                              # constant pressure: T is proportional to V
    t4 = t3 * (rho / r) ** (gamma - 1.0)       # isentropic expansion from V3 = rho V2 to V4 = r V2
    return (t1, t2, t3, t4), rho, cv * (t4 - t1)


# %% [markdown]
# ## Step 3: design by inverting the formula
# Otto: solve `eta = 1 - r**(1-gamma)` for r: `r = (1 - eta) ** (-1 / (gamma - 1))`.
# Diesel at fixed r: eta falls as rho grows, so find rho by bisection.

# %%
def otto_r_for_eta(eta, gamma=GAMMA):
    """Compression ratio an ideal Otto cycle needs for efficiency eta (0 < eta < 1)."""
    if not 0 < eta < 1:
        raise ValueError("efficiency must be between 0 and 1")
    return (1.0 - eta) ** (-1.0 / (gamma - 1.0))


def diesel_rho_for_eta(eta, r, gamma=GAMMA, rho_max=10.0):
    """Cut-off ratio that gives efficiency eta at compression ratio r, or None if impossible."""
    if eta > otto_eta(r, gamma) or eta < diesel_eta(r, rho_max, gamma):
        return None
    lo, hi = 1.0, rho_max
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if diesel_eta(r, mid, gamma) > eta:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# %% [markdown]
# ## Step 4: P-V points of each cycle (for plotting)
# Per kg of air with P1 = 100 kPa, T1 = 300 K: specific volume v = R T / P in m3/kg.

# %%
def cycle_path(kind, r, q_in, p1=100.0, t1=300.0, gamma=GAMMA, n=60):
    """(v, P) arrays tracing the cycle once. kind is 'otto' or 'diesel'. v in m3/kg, P in kPa."""
    v1 = R_AIR * t1 / p1
    v2 = v1 / r
    cv = R_AIR / (gamma - 1.0)
    t2 = t1 * r ** (gamma - 1.0)
    p2 = p1 * r ** gamma
    if kind == "otto":
        t3 = t2 + q_in / cv
        v3, p3 = v2, p2 * t3 / t2
    else:
        v3 = v2 * diesel_cutoff_for_heat(r, q_in, t1, gamma)
        p3 = p2
    s = np.linspace(0.0, 1.0, n)
    v_c = v1 + (v2 - v1) * s                       # compression 1 to 2
    comp = (v_c, p1 * (v1 / v_c) ** gamma)
    heat = (v2 + (v3 - v2) * s, p2 + (p3 - p2) * s)  # 2 to 3 (vertical for Otto, horizontal for Diesel)
    v_e = v3 + (v1 - v3) * s                       # expansion 3 to 4
    p4 = p3 * (v3 / v1) ** gamma
    exp = (v_e, p3 * (v3 / v_e) ** gamma)
    cool = (np.full(n, v1), p4 + (p1 - p4) * s)    # 4 to 1
    v = np.concatenate([comp[0], heat[0], exp[0], cool[0]])
    p = np.concatenate([comp[1], heat[1], exp[1], cool[1]])
    return v, p


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"Otto r = 9: eta = {otto_eta(9):.4f}")
    print(f"Diesel r = 18, rho = 2: eta = {diesel_eta(18, 2):.4f}; Otto r = 18: {otto_eta(18):.4f}")
    print(f"Otto r needed for eta = 0.60: {otto_r_for_eta(0.60):.2f}")
    print(f"Carnot 300 K / 2000 K: {carnot_eta(300, 2000):.3f}")

    # Figure 1: P-V loops of the two cycles, same compression ratio and same heat input
    r, q_in = 9.0, 1100.0
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for kind, colour in (("otto", "#2a9d8f"), ("diesel", "#d9534f")):
        v, p = cycle_path(kind, r, q_in)
        ax.plot(v, p, color=colour, label=f"{kind.capitalize()}, r = 9")
    ax.set_yscale("log")
    ax.set_xlabel("specific volume v (m3/kg)")
    ax.set_ylabel("pressure P (kPa, log scale)")
    ax.set_title("Otto and Diesel loops: same r, same heat in")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "pv_otto_diesel.png", dpi=120)

    # Figure 2: efficiency against compression ratio
    rs = np.linspace(4, 24, 100)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(rs, [otto_eta(x) for x in rs], color="#2a9d8f", label="Otto")
    for rho, ls in ((1.5, "-"), (2.5, "--")):
        ax2.plot(rs, [diesel_eta(x, rho) for x in rs], color="#d9534f", ls=ls, label=f"Diesel, rho = {rho}")
    ax2.axhline(carnot_eta(300, 2000), color="k", ls=":", label="Carnot, 300 K and 2000 K")
    ax2.set_xlabel("compression ratio r")
    ax2.set_ylabel("ideal efficiency (no unit)")
    ax2.set_title("More squeeze, more efficiency, but with diminishing returns")
    ax2.set_ylim(0.3, 0.9)
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "eta_vs_r.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The formulas assume instant heat addition, constant gamma and no losses. Session 3 relaxes
# these by stepping through the cycle numerically and measuring how far real behaviour falls
# below the formula.
