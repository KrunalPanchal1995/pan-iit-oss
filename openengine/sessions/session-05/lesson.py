"""Session 5 (Level 2): the dual (Seiliger) cycle, between Otto and Diesel.

Run:  python start.py 5
"""
# %% [markdown]
# # Session 5: the dual cycle
# **A. Real-world problem.** Session 2 had two extremes: the Otto cycle adds all its heat at
# constant volume, the Diesel cycle all of it at constant pressure. A real high-speed diesel does
# both: the fuel injected before top dead centre burns almost at once (nearly constant volume),
# the rest burns while the piston moves down (nearly constant pressure). How does the share of
# heat added at constant volume change the efficiency and the peak pressure?
#
# **Plan.** (1) split the heat into a constant-volume part and a constant-pressure part,
# (2) follow the temperatures round the five states, (3) the closed-form efficiency and its two
# limits (Otto and Diesel), (4) the P-V path, (5) the trade-off between efficiency and peak
# pressure.
#
# **Model.** Air-standard cycle as in Session 2: ideal gas with constant gamma = 1.4, heat from
# outside, isentropic compression and expansion, no losses. A simplified teaching model, not a
# design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_AIR = 0.287          # gas constant of air, kJ/(kg K)
GAMMA = 1.4            # ratio of specific heats (constant, as in Session 2)


# %% [markdown]
# ## Step 1: five states instead of four
# 1 to 2: isentropic compression by r, `T2 = T1 r**(gamma-1)`, `P2 = P1 r**gamma`.
# 2 to 3: a share x of the heat at constant volume, `x q_in = cv (T3 - T2)`.
# The **pressure ratio** `alpha = P3 / P2 = T3 / T2`.
# 3 to 4: the rest at constant pressure, `(1 - x) q_in = cp (T4 - T3)`.
# The **cut-off ratio** `rho = v4 / v3 = T4 / T3`.
# 4 to 5: isentropic expansion from `v4 = rho v2` back to `v1 = r v2`.
# 5 to 1: heat rejected at constant volume, `q_out = cv (T5 - T1)`.
#
# x = 1 is the Otto cycle (rho = 1), x = 0 is the Diesel cycle (alpha = 1).

# %%
def dual_cycle(r, q_in, x, t1=300.0, p1=100.0, gamma=GAMMA):
    """Dual cycle with a share x (0 to 1) of q_in (kJ/kg) added at constant volume.

    Returns a dict with T (T1..T5 in K), P (P1..P5 in kPa), alpha, rho, q_out and eta."""
    if r <= 1:
        raise ValueError("compression ratio must be above 1")
    if q_in <= 0:
        raise ValueError("heat input must be positive")
    if not 0.0 <= x <= 1.0:
        raise ValueError("the constant-volume share x must be between 0 and 1")
    cv = R_AIR / (gamma - 1.0)
    cp = gamma * cv
    t2 = t1 * r ** (gamma - 1.0)
    t3 = t2 + x * q_in / cv
    t4 = t3 + (1.0 - x) * q_in / cp
    alpha, rho = t3 / t2, t4 / t3
    t5 = t4 * (rho / r) ** (gamma - 1.0)
    q_out = cv * (t5 - t1)
    p2 = p1 * r ** gamma
    p3 = alpha * p2
    p5 = p1 * t5 / t1
    return {"T": (t1, t2, t3, t4, t5), "P": (p1, p2, p3, p3, p5), "alpha": alpha, "rho": rho,
            "q_out": q_out, "eta": 1.0 - q_out / q_in}


# %% [markdown]
# ## Step 2: the closed-form efficiency
# Putting the temperatures into `1 - q_out / q_in` and simplifying gives the textbook result
#
#     eta = 1 - (1 / r**(gamma-1)) * (alpha rho**gamma - 1) / ((alpha - 1) + gamma alpha (rho - 1))
#
# Check the limits: with rho = 1 the fraction is (alpha - 1) / (alpha - 1) = 1, the Otto formula.
# With alpha = 1 it is (rho**gamma - 1) / (gamma (rho - 1)), the Diesel formula of Session 2.

# %%
def dual_eta(r, alpha, rho, gamma=GAMMA):
    """Dual-cycle efficiency from r, pressure ratio alpha >= 1 and cut-off ratio rho >= 1."""
    if r <= 1:
        raise ValueError("compression ratio must be above 1")
    if alpha < 1 or rho < 1:
        raise ValueError("pressure ratio and cut-off ratio must be at least 1")
    den = (alpha - 1.0) + gamma * alpha * (rho - 1.0)
    if den < 1e-12:                       # alpha = rho = 1: no heat, use the Otto limit
        return 1.0 - r ** (1.0 - gamma)
    return 1.0 - r ** (1.0 - gamma) * (alpha * rho ** gamma - 1.0) / den


def otto_eta(r, gamma=GAMMA):
    """Session 2 Otto efficiency."""
    return 1.0 - r ** (1.0 - gamma)


def diesel_eta(r, rho, gamma=GAMMA):
    """Session 2 Diesel efficiency."""
    if abs(rho - 1.0) < 1e-12:
        return otto_eta(r, gamma)
    return 1.0 - r ** (1.0 - gamma) * (rho ** gamma - 1.0) / (gamma * (rho - 1.0))


# %% [markdown]
# ## Step 3: the P-V path
# Per kg of air, v = R T / P in m3/kg. The two heat-addition lines are a vertical segment
# (2 to 3) followed by a horizontal one (3 to 4).

# %%
def dual_path(r, q_in, x, t1=300.0, p1=100.0, gamma=GAMMA, n=60):
    """(v, P) arrays tracing the dual cycle once; v in m3/kg, P in kPa."""
    c = dual_cycle(r, q_in, x, t1, p1, gamma)
    v1 = R_AIR * t1 / p1
    v2 = v1 / r
    v4 = c["rho"] * v2
    p2, p3, p5 = c["P"][1], c["P"][2], c["P"][4]
    s = np.linspace(0.0, 1.0, n)
    v_c = v1 + (v2 - v1) * s
    v_e = v4 + (v1 - v4) * s
    v = np.concatenate([v_c, np.full(n, v2), v2 + (v4 - v2) * s, v_e, np.full(n, v1)])
    p = np.concatenate([p1 * (v1 / v_c) ** gamma, p2 + (p3 - p2) * s, np.full(n, p3),
                        p3 * (v4 / v_e) ** gamma, p5 + (p1 - p5) * s])
    return v, p


def loop_work(v, p):
    """Sum of P dv around the closed loop (trapezoid rule), kJ/kg."""
    v2, p2 = np.roll(v, -1), np.roll(p, -1)
    return float(np.sum(0.5 * (p + p2) * (v2 - v)))


# %% [markdown]
# ## Step 4: design under a peak-pressure limit
# More heat at constant volume raises the efficiency but also the peak pressure P3, which the
# engine structure must carry. For a pressure limit, the largest allowed share is
# `x_max = cv T2 (P_max / P2 - 1) / q_in` (clipped to 0..1).

# %%
def max_cv_share(r, q_in, p_max, t1=300.0, p1=100.0, gamma=GAMMA):
    """Largest constant-volume share x allowed by a peak pressure p_max (kPa), or None if even x = 0 is too high."""
    p2 = p1 * r ** gamma
    if p2 > p_max:
        return None
    cv = R_AIR / (gamma - 1.0)
    t2 = t1 * r ** (gamma - 1.0)
    return min(1.0, cv * t2 * (p_max / p2 - 1.0) / q_in)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    r, q = 18.0, 1100.0
    for x in (0.0, 0.5, 1.0):
        c = dual_cycle(r, q, x)
        print(f"x = {x:.1f}: alpha = {c['alpha']:.3f}, rho = {c['rho']:.3f}, eta = {c['eta']:.4f}, peak P = {c['P'][2]:.0f} kPa")
    half = dual_cycle(r, q, 0.5)
    print(f"closed form for the half split: {dual_eta(r, half['alpha'], half['rho']):.4f}")
    print(f"largest share for P3 <= 9000 kPa at r = 18: x = {max_cv_share(r, q, 9000):.3f}")

    # colour-blind-safe colours (Okabe-Ito) and a line style per cycle
    C_OTTO, C_DIESEL, C_DUAL = "#0072B2", "#D55E00", "#009E73"

    # Figure 1: P-V loops of Otto, Diesel and the half split at r = 18
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for x, col, ls, name in ((1.0, C_OTTO, "-", "Otto (x = 1)"), (0.0, C_DIESEL, "--", "Diesel (x = 0)"), (0.5, C_DUAL, "-.", "dual, x = 0.5")):
        v, p = dual_path(r, q, x)
        ax.plot(v, p, color=col, ls=ls, label=f"{name}: eta = {dual_cycle(r, q, x)['eta']:.3f}")
    ax.set_xscale("log")              # log-log: isentropes are straight lines and the heat-addition corner spreads out
    ax.set_yscale("log")
    ax.set_xlabel("specific volume v (m3/kg, log scale)")
    ax.set_ylabel("pressure P (kPa, log scale)")
    ax.set_title("r = 18, q_in = 1100 kJ/kg: three ways to add the heat")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "pv_dual.png", dpi=120)

    # Figure 2: efficiency and peak pressure against the constant-volume share (the roadmap checkpoint)
    xs = np.linspace(0, 1, 101)
    fig2, (b1, b2) = plt.subplots(1, 2, figsize=(9.6, 4))
    b1.plot(xs, [dual_cycle(r, q, x)["eta"] for x in xs], color=C_DUAL, label="dual cycle")
    b1.axhline(otto_eta(r), color=C_OTTO, ls="-", lw=1, label=f"Otto {otto_eta(r):.3f}")
    b1.axhline(dual_cycle(r, q, 0)["eta"], color=C_DIESEL, ls="--", lw=1, label=f"Diesel {dual_cycle(r, q, 0)['eta']:.3f}")
    b1.plot([0.5], [half["eta"]], "o", color=C_DUAL)
    b1.annotate(f"half split {half['eta']:.3f}", (0.5, half["eta"]), textcoords="offset points", xytext=(6, -16))
    b1.set_xlabel("share of heat added at constant volume x")
    b1.set_ylabel("ideal efficiency (no unit)")
    b1.set_title("Efficiency lies between Diesel and Otto")
    b2.plot(xs, [dual_cycle(r, q, x)["P"][2] / 1000 for x in xs], color=C_DUAL, label="peak pressure P3")
    b2.axhline(9.0, color="k", ls=":", lw=1, label="example limit 9 MPa")
    b2.set_xlabel("share of heat added at constant volume x")
    b2.set_ylabel("peak pressure (MPa)")
    b2.set_title("but the peak pressure climbs")
    for b in (b1, b2):
        b.grid(alpha=0.3)
        b.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "eta_split.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Gamma is still constant (Session 4 showed how much that flatters the result) and the heat still
# arrives instantly. The next milestone on the roadmap draws the T-S diagram of the simulated
# cycle, where the area of the loop is the net heat.
