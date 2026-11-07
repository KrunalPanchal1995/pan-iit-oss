"""Session 3 (Level 3): step through the cycle numerically and validate it.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate the cycle, then check it against the formulas
# **A. Real-world problem.** The Session 2 formulas assume heat arrives instantly and that
# nothing is lost. A real engine burns fuel over a few tens of crank degrees, loses heat
# to its walls and drags against friction. Can we simulate the cycle step by step, show that
# the simulation reproduces the formulas when we switch the real effects off, and then
# measure how much each real effect costs? And which cycle wins when we compare them fairly?
#
# **Plan.** (1) a step-by-step ideal cycle (first law, numerical P dV), (2) validation,
# (3) a crank-angle model with a Wiebe heat-release curve, heat loss and friction,
# (4) sensitivity, (5) Otto against Diesel in two fair comparisons, (6) the knock limit.
#
# **Model.** Air as an ideal gas with constant gamma; per kilogram of air; pressure in kPa,
# specific volume in m3/kg, so P x v is in kJ/kg. A simplified teaching model, not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_AIR, GAMMA, P1, T1 = 0.287, 1.4, 100.0, 300.0     # kJ/(kg K), no unit, kPa, K


# %% [markdown]
# ## Step 1: the ideal cycle, one small step at a time
# The first law for a small step of a closed ideal gas is `dQ = dU + P dv` with
# `U = P v / (gamma - 1)`. That gives:
#
# * no heat (compression, expansion): `dP/dv = -gamma P / v`, integrated with Runge-Kutta 4
# * heat at constant volume (Otto): `dP = (gamma - 1) dQ / v`
# * heat at constant pressure (Diesel): `dv = (gamma - 1) dQ / (gamma P)`
# * rejection at constant volume back to P1.
#
# The work is the sum of `P dv` (trapezoid rule) around the closed loop. Nothing here uses
# the efficiency formula, so comparing with it is a real test.

# %%
def _isentrope(p, v_from, v_to, gamma, n):
    """RK4 integration of dP/dv = -gamma P / v from v_from to v_to; returns arrays (v, P)."""
    vs = np.linspace(v_from, v_to, n + 1)
    ps = np.empty(n + 1)
    ps[0] = p
    f = lambda pp, vv: -gamma * pp / vv
    for i in range(n):
        h = vs[i + 1] - vs[i]
        k1 = f(ps[i], vs[i])
        k2 = f(ps[i] + 0.5 * h * k1, vs[i] + 0.5 * h)
        k3 = f(ps[i] + 0.5 * h * k2, vs[i] + 0.5 * h)
        k4 = f(ps[i] + h * k3, vs[i] + h)
        ps[i + 1] = ps[i] + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
    return vs, ps


def loop_integral(v, p):
    """Closed-loop integral of P dv by the trapezoid rule (kJ/kg for P in kPa, v in m3/kg)."""
    v2, p2 = np.roll(v, -1), np.roll(p, -1)
    return float(np.sum(0.5 * (p + p2) * (v2 - v)))


def ideal_cycle(kind, r, q_in, gamma=GAMMA, n=400, p1=P1, t1=T1):
    """Step through an ideal air cycle. kind is 'otto' or 'diesel'. q_in in kJ/kg.

    Returns a dict with arrays v, p and the numbers work, q_out, eta, rho, p_max, t_max, residual
    (residual = work - (q_in - q_out), the first-law error)."""
    if r <= 1 or q_in <= 0:
        raise ValueError("need r > 1 and q_in > 0")
    v1 = R_AIR * t1 / p1
    v2 = v1 / r
    va, pa = _isentrope(p1, v1, v2, gamma, n)                  # 1 -> 2
    dq = q_in / n
    if kind == "otto":                                          # 2 -> 3 at constant volume
        pb = pa[-1] + np.cumsum(np.full(n, (gamma - 1.0) * dq / v2))
        vb = np.full(n, v2)
    else:                                                       # 2 -> 3 at constant pressure
        vb = np.empty(n)
        v = v2
        for i in range(n):
            v = v + (gamma - 1.0) * dq / (gamma * pa[-1])
            vb[i] = v
        pb = np.full(n, pa[-1])
    v3, p3 = vb[-1], pb[-1]
    vc, pc = _isentrope(p3, v3, v1, gamma, n)                   # 3 -> 4
    p4 = pc[-1]
    q_out = v1 * (p4 - p1) / (gamma - 1.0)                      # 4 -> 1 at constant volume
    vd = np.full(n, v1)
    pd = p4 + (p1 - p4) * np.arange(1, n + 1) / n
    v = np.concatenate([va, vb, vc[1:], vd])
    p = np.concatenate([pa, pb, pc[1:], pd])
    work = loop_integral(v, p)
    return {"v": v, "p": p, "work": work, "q_in": q_in, "q_out": q_out, "eta": work / q_in,
            "rho": v3 / v2, "p_max": float(p.max()), "t_max": float((p * v).max() / R_AIR),
            "residual": work - (q_in - q_out)}


def analytic_eta(kind, r, rho=1.0, gamma=GAMMA):
    """The Session 2 formulas."""
    base = r ** (1.0 - gamma)
    if kind == "otto":
        return 1.0 - base
    return 1.0 - base * (rho ** gamma - 1.0) / (gamma * (rho - 1.0))


# %% [markdown]
# ## Step 2: a crank-angle model with a Wiebe burn, heat loss and friction
# A piston on a crank has volume `V/Vc = 1 + (r-1)/2 (L + 1 - cos(a) - sqrt(L**2 - sin(a)**2))`
# where `a` is the crank angle from top dead centre (TDC) and `L` = rod length / crank radius.
# Heat is released along a **Wiebe** curve: the burnt fraction is
# `x = 1 - exp(-A z**(m+1))` with `z = (a - a0) / duration`, A = 6.908, m = 2, so burning
# starts slowly, speeds up and tails off. The first law gives the pressure change per degree:
#
#     dP/da = [ (gamma - 1) dQ/da  -  gamma P dV/da ] / V
#
# Two knock-downs: `loss` is the share of the heat that escapes to the cylinder walls instead
# of heating the gas; `fmep` (friction mean effective pressure, kPa) is subtracted from the
# indicated work as `fmep x displacement`.

# %%
WIEBE_A, WIEBE_M, ROD_RATIO = 6.908, 2.0, 3.5


def volume_ratio(angle_deg, r, rod=ROD_RATIO):
    """V / Vc at crank angle (degrees from TDC)."""
    a = np.radians(angle_deg)
    return 1.0 + 0.5 * (r - 1.0) * (rod + 1.0 - np.cos(a) - np.sqrt(rod ** 2 - np.sin(a) ** 2))


def _dvr(angle_deg, r, rod=ROD_RATIO):
    """d(V/Vc)/d(angle in degrees)."""
    a = np.radians(angle_deg)
    return 0.5 * (r - 1.0) * (np.sin(a) + np.sin(a) * np.cos(a) / np.sqrt(rod ** 2 - np.sin(a) ** 2)) * np.pi / 180.0


def wiebe_rate(angle_deg, start, duration):
    """Burnt fraction per degree (integrates to 1 between start and start + duration)."""
    z = (angle_deg - start) / duration
    if z <= 0 or z >= 1:
        return 0.0
    norm = 1.0 - np.exp(-WIEBE_A)
    return WIEBE_A * (WIEBE_M + 1) * z ** WIEBE_M * np.exp(-WIEBE_A * z ** (WIEBE_M + 1)) / (duration * norm)


def engine_cycle(r, q_fuel, start=-10.0, duration=40.0, loss=0.0, fmep=0.0, gamma=GAMMA, step=0.25):
    """Crank-angle simulation from bottom dead centre (-180) round to +180 degrees.

    q_fuel in kJ/kg of air; start = crank angle where burning begins (degrees, negative is
    before TDC); duration in degrees; loss = share of heat lost to walls (0 to 1);
    fmep in kPa. Returns a dict with angle, v, p, t arrays and the numbers."""
    if not (0 <= loss < 1) or duration <= 0 or r <= 1:
        raise ValueError("need 0 <= loss < 1, duration > 0, r > 1")
    v1 = R_AIR * T1 / P1
    vc = v1 / r
    q_gas = (1.0 - loss) * q_fuel
    n = int(round(360.0 / step))
    ang = -180.0 + step * np.arange(n + 1)
    p = np.empty(n + 1)
    p[0] = P1

    def f(a, pp):
        vv = vc * volume_ratio(a, r)
        return ((gamma - 1.0) * q_gas * wiebe_rate(a, start, duration) - gamma * pp * vc * _dvr(a, r)) / vv

    for i in range(n):
        a, h = ang[i], step
        k1 = f(a, p[i])
        k2 = f(a + h / 2, p[i] + h / 2 * k1)
        k3 = f(a + h / 2, p[i] + h / 2 * k2)
        k4 = f(a + h, p[i] + h * k3)
        p[i + 1] = p[i] + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
    v = vc * volume_ratio(ang, r)
    w_ind = loop_integral(v, p)                                # exhaust at constant v adds no work
    q_out = v1 * (p[-1] - P1) / (gamma - 1.0)
    w_fric = fmep * (v1 - vc)
    return {"angle": ang, "v": v, "p": p, "t": p * v / R_AIR, "work_ind": w_ind, "q_out": q_out,
            "q_gas": q_gas, "eta_ind": w_ind / q_fuel, "eta_brake": (w_ind - w_fric) / q_fuel,
            "p_max": float(p.max()), "t_max": float((p * v).max() / R_AIR),
            "residual": w_ind - (q_gas - q_out)}


# %% [markdown]
# ## Step 3: fair comparisons of Otto and Diesel
# Which is better depends on what you hold equal.
# * **Equal compression ratio and equal heat:** Otto wins (Session 2 showed why: the Diesel
#   adds part of its heat while the piston is already moving down).
# * **Equal peak pressure and equal heat:** the structure limits the pressure, not r. The
#   Diesel can compress harder (higher r) before it burns, so it wins.
# We find the compression ratio that gives a chosen peak pressure by bisection on the simulation.

# %%
def r_for_peak_pressure(kind, p_max, q_in, gamma=GAMMA):
    """Compression ratio at which the simulated cycle reaches exactly p_max (kPa)."""
    lo, hi = 1.5, 60.0
    if ideal_cycle(kind, lo, q_in, gamma, n=60)["p_max"] > p_max:
        raise ValueError("peak pressure too low for this heat input")
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if ideal_cycle(kind, mid, q_in, gamma, n=60)["p_max"] < p_max:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def compare_equal_r(r, q_in, gamma=GAMMA):
    """(eta_otto, eta_diesel) from the simulation at equal r and equal heat."""
    return ideal_cycle("otto", r, q_in, gamma)["eta"], ideal_cycle("diesel", r, q_in, gamma)["eta"]


def compare_equal_pmax(p_max, q_in, gamma=GAMMA):
    """(r_otto, eta_otto, r_diesel, eta_diesel) at equal peak pressure and equal heat."""
    ro = r_for_peak_pressure("otto", p_max, q_in, gamma)
    rd = r_for_peak_pressure("diesel", p_max, q_in, gamma)
    return ro, ideal_cycle("otto", ro, q_in, gamma)["eta"], rd, ideal_cycle("diesel", rd, q_in, gamma)["eta"]


# %% [markdown]
# ## Step 4: the knock limit (a failure case)
# In a spark-ignition engine the unburnt "end gas" ahead of the flame is squeezed and heated.
# If it gets hot enough for long enough it ignites by itself, all at once: a pressure shock
# called **knock** that rings the engine and can melt a piston. Compression heats the air to
# `T2 = T1 r**(gamma-1)`, so a higher r means a hotter end gas. Fuels differ in how much heat
# they tolerate. We use an illustrative limit on T2, not a real fuel specification. A Diesel
# engine compresses only air and injects fuel at the end, so it does not knock this way and can
# use a high r.

# %%
def end_compression_temperature(r, gamma=GAMMA, t1=T1):
    """Air temperature (K) at the end of isentropic compression."""
    return t1 * r ** (gamma - 1.0)


def max_r_knock_free(t_limit, margin=0.0, gamma=GAMMA, t1=T1, step=0.5):
    """Largest compression ratio, in multiples of `step`, whose end temperature stays
    at or below t_limit - margin (K). Returns None if even r = 1 is too hot."""
    t_allow = t_limit - margin
    if t_allow < t1:
        return None
    r_exact = (t_allow / t1) ** (1.0 / (gamma - 1.0))
    return float(np.floor(r_exact / step + 1e-9) * step)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    q_in = 1100.0

    # validation against Session 2
    for kind, r in (("otto", 9.0), ("diesel", 18.0)):
        c = ideal_cycle(kind, r, q_in)
        ref = analytic_eta(kind, r, c["rho"])
        print(f"{kind} r = {r:g}: simulated eta {c['eta']:.5f}, formula {ref:.5f}, first-law residual {c['residual']:.2e} kJ/kg")

    # Figure 1: ideal cycles from the simulation
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for kind, r, colour in (("otto", 9.0, "#2a9d8f"), ("diesel", 18.0, "#d9534f")):
        c = ideal_cycle(kind, r, q_in)
        ax.plot(c["v"], c["p"], color=colour, label=f"{kind} r = {r:g}, eta = {c['eta']:.3f}")
    ax.set_yscale("log")
    ax.set_xlabel("specific volume v (m3/kg)")
    ax.set_ylabel("pressure P (kPa, log scale)")
    ax.set_title("Simulated ideal cycles (heat in 1100 kJ/kg)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "ideal_cycles.png", dpi=120)

    # Figure 2: the real effects, one at a time (Otto r = 9)
    cases = [("ideal (instant heat)", dict(start=-0.5, duration=1.0)),
             ("Wiebe burn, 40 deg", dict()),
             ("+ 10% heat loss", dict(loss=0.10)),
             ("+ friction 100 kPa", dict(loss=0.10, fmep=100.0))]
    fig2, (axp, axb) = plt.subplots(1, 2, figsize=(10, 4.2))
    etas = []
    for name, kw in cases:
        c = engine_cycle(9.0, q_in, **kw)
        etas.append(c["eta_brake"])
        print(f"{name:24s} indicated {c['eta_ind']:.4f}  brake {c['eta_brake']:.4f}  Pmax {c['p_max']:.0f} kPa  first-law residual {c['residual']:.2e}")
        if "friction" not in name:
            axp.plot(c["v"], c["p"], label=name)
    axp.set_yscale("log")
    axp.set_xlabel("specific volume v (m3/kg)")
    axp.set_ylabel("pressure P (kPa, log scale)")
    axp.set_title("P-V loops from the crank-angle model")
    axp.legend(fontsize=8)
    axp.grid(alpha=0.3, which="both")
    axb.barh([n for n, _ in cases][::-1], etas[::-1], color=["#d9534f", "#e9a23b", "#2a9d8f", "#264653"][::-1])
    axb.axvline(analytic_eta("otto", 9.0), color="k", ls="--")
    axb.set_xlabel("efficiency (no unit); dashed = Otto formula")
    axb.set_title("Each real effect costs efficiency")
    fig2.tight_layout()
    fig2.savefig(OUT / "knockdown.png", dpi=120)

    # Figure 3: the two fair comparisons
    eo, ed = compare_equal_r(14.0, q_in)
    ro, eo2, rd, ed2 = compare_equal_pmax(6000.0, q_in)
    print(f"equal r = 14, equal heat: Otto {eo:.4f}, Diesel {ed:.4f}")
    print(f"equal Pmax = 6000 kPa, equal heat: Otto r = {ro:.2f} eta {eo2:.4f}; Diesel r = {rd:.2f} eta {ed2:.4f}")
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.2))
    x = np.arange(2)
    ax3.bar(x - 0.18, [eo, eo2], 0.36, color="#2a9d8f", label="Otto")
    ax3.bar(x + 0.18, [ed, ed2], 0.36, color="#d9534f", label="Diesel")
    for xi, a, b in zip(x, [eo, eo2], [ed, ed2]):
        ax3.text(xi - 0.18, a + 0.005, f"{a:.3f}", ha="center", fontsize=9)
        ax3.text(xi + 0.18, b + 0.005, f"{b:.3f}", ha="center", fontsize=9)
    ax3.set_xticks(x)
    ax3.set_xticklabels(["equal r = 14", f"equal peak pressure 6000 kPa\n(Otto r = {ro:.1f}, Diesel r = {rd:.1f})"])
    ax3.set_ylim(0.4, 0.8)
    ax3.set_ylabel("ideal efficiency (no unit)")
    ax3.set_title("Which wins depends on what you hold equal")
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "fair_comparison.png", dpi=120)

    # sensitivity
    print("sensitivity of the ideal Otto efficiency to r:", [round(ideal_cycle("otto", x, q_in)["eta"], 3) for x in (6, 8, 10, 12, 14)])
    print("sensitivity to gamma (r = 9):", [round(ideal_cycle("otto", 9.0, q_in, g)["eta"], 3) for g in (1.3, 1.35, 1.4)])
    print("Otto eta against heat input (no change):", [round(ideal_cycle("otto", 9.0, q)["eta"], 4) for q in (500, 1100, 1700)])
    print("Diesel r = 18 eta against heat input:", [round(ideal_cycle("diesel", 18.0, q)["eta"], 4) for q in (500, 1100, 1700)])
    print("brake efficiency against r (Wiebe 40 deg, 10% loss, fmep 100):", [round(engine_cycle(x, q_in, loss=0.10, fmep=100.0)["eta_brake"], 3) for x in (6, 8, 10, 12, 14)])
    for r in (8, 9, 10, 11, 12):
        print(f"r = {r}: end-of-compression temperature {end_compression_temperature(r):.0f} K")

# %% [markdown]
# ## Where this stops
# Constant gamma, a single Wiebe curve and a fixed loss share are still crude. Real engines
# need temperature-dependent gas properties, a flame model and a knock model. That is the
# road to the Target: see `promo/roadmap.md`.
