"""Session 3 (Level 3): a turbojet with real component efficiencies, validated, with thrust and fuel use.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a turbojet, built and validated
# **A. Real-world problem.** A jet engine does not make shaft power. The turbine takes only
# enough work to drive the compressor, and the rest of the hot gas expands through a nozzle
# and leaves fast: the push on the engine is the thrust. How much thrust does one kilogram
# of air per second give, how much fuel does it need, and how do the losses in the compressor,
# turbine and nozzle change the answer?
#
# Educational model: air with constant properties, a stationary engine on a test stand
# (flight speed 0), fully expanded nozzle, fuel mass ignored. Not a design tool.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
GAMMA, CP = 1.4, 1005.0      # air: ratio of specific heats (no unit), specific heat (J/(kg K))
K = (GAMMA - 1) / GAMMA
LHV = 43e6                   # fuel lower heating value (J/kg), typical for kerosene
ETA_B = 0.98                 # combustor efficiency (no unit)


# %% [markdown]
# ## Step 1: real compressor and turbine
# An isentropic efficiency says how much of the ideal work is really achieved.
#
#     T2 = T1 [1 + (r^K - 1) / eta_c]         compressor needs more work than ideal
#     T4 = T3 - (T2 - T1)                     the turbine only drives the compressor
#     (p4 / p3)^K = 1 - (T3 - T4) / (eta_t T3)    pressure left after the turbine
#
# Here p3 = r p1 (no pressure loss in the combustor).

# %%
def turbojet(t1, r, t3, eta_c=0.85, eta_t=0.90, eta_n=0.95):
    """Static turbojet. Returns a dictionary in SI units (K, J/kg, m/s, N s/kg).

    Raises ValueError if the turbine cannot leave any pressure for a jet.
    """
    if r < 1:
        raise ValueError("the pressure ratio must be at least 1")
    for e in (eta_c, eta_t, eta_n):
        if not 0 < e <= 1:
            raise ValueError("efficiencies must be above 0 and at most 1")
    t2 = t1 * (1 + (r ** K - 1) / eta_c)
    t4 = t3 - (t2 - t1)
    if t4 <= 0 or t3 <= t2:
        raise ValueError("T3 must be hotter than T2")
    inner = 1 - (t3 - t4) / (eta_t * t3)
    if inner <= 0:
        raise ValueError("the turbine cannot drive the compressor")
    p_ratio_nozzle = r * inner ** (1 / K)      # p4 / p1: the nozzle expands from p4 down to p1
    if p_ratio_nozzle < 1:
        raise ValueError("no pressure is left for a jet: raise T3 or the efficiencies, or lower r")
    t5s = t4 * p_ratio_nozzle ** (-K)
    dt_n = eta_n * (t4 - t5s)
    v_e = (2 * CP * dt_n) ** 0.5
    q_in = CP * (t3 - t2)
    fuel_air = q_in / (LHV * ETA_B)
    return {"t2": t2, "t4": t4, "t5": t4 - dt_n, "p_ratio_nozzle": p_ratio_nozzle, "v_e": v_e,
            "thrust_sp": v_e, "q_in": q_in, "fuel_air": fuel_air, "tsfc": fuel_air / v_e * 1e6 if v_e > 0 else float("inf")}


# %% [markdown]
# ## Step 2: thrust and fuel use
# On a test stand the air enters at rest, so the specific thrust (thrust per kg/s of air) is
# just the exit speed. The nozzle turns the temperature drop into speed:
#
#     v_e = sqrt(2 cp eta_n (T4 - T5s))        F / mdot = v_e - 0 (N s/kg)
#
# The fuel needed per kg of air is q_in / (eta_b x LHV). The thrust specific fuel consumption
# (TSFC) is the fuel per second per newton of thrust, in grams per kilonewton second.

# %%
def thrust_kn(mdot, **kw):
    """Thrust in kilonewtons for an air flow mdot (kg/s)."""
    return mdot * turbojet(**kw)["thrust_sp"] / 1000


def fuel_flow_kg_s(mdot, **kw):
    return mdot * turbojet(**kw)["fuel_air"]


# %% [markdown]
# ## Step 3: validation
# Two tests that do not need a real engine:
#
# 1. With no losses (all efficiencies 1) the kinetic energy of the jet, v_e^2 / 2, must equal the
#    net work of the ideal cycle from Session 2: w_net = cp [(T3 - T4) - (T2 - T1)].
# 2. Energy balance of the whole engine: q_in = cp (T5 - T1) + v_e^2 / 2 (the heat added leaves
#    as hot exhaust and as jet kinetic energy).

# %%
def ideal_net_work(t1, r, t3):
    x = r ** K
    return CP * ((t3 - t3 / x) - (t1 * x - t1))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    kw = dict(t1=288, r=10, t3=1400)
    j = turbojet(**kw)
    print(f"T2 = {j['t2']:.1f} K, T4 = {j['t4']:.1f} K, nozzle pressure ratio = {j['p_ratio_nozzle']:.2f}")
    print(f"exit speed = {j['v_e']:.0f} m/s = specific thrust {j['thrust_sp']:.0f} N s/kg")
    print(f"fuel/air = {j['fuel_air']:.4f}, TSFC = {j['tsfc']:.1f} g/(kN s)")
    print(f"20 kg/s of air -> thrust {thrust_kn(20, **kw):.1f} kN, fuel {fuel_flow_kg_s(20, **kw):.2f} kg/s")
    ideal = turbojet(**kw, eta_c=1, eta_t=1, eta_n=1)
    print(f"no losses: v_e^2/2 = {ideal['v_e'] ** 2 / 2 / 1000:.1f} kJ/kg, Session 2 w_net = {ideal_net_work(288, 10, 1400) / 1000:.1f} kJ/kg")

    r = np.linspace(2, 30, 140)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for t3x, col in ((1200, "tab:green"), (1400, "tab:blue"), (1600, "tab:red")):
        ys = []
        for x in r:
            try:
                ys.append(turbojet(288, x, t3x)["thrust_sp"])
            except ValueError:
                ys.append(np.nan)
        ax.plot(r, ys, color=col, label=f"T3 = {t3x} K")
    ax.set_xlabel("pressure ratio r (no unit)")
    ax.set_ylabel("specific thrust (N s per kg of air)")
    ax.set_title("Hotter turbine inlet, more thrust per kg of air")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "thrust_vs_ratio.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for e, col in ((1.0, "tab:gray"), (0.9, "tab:blue"), (0.8, "tab:red")):
        ys = []
        for x in r:
            try:
                ys.append(turbojet(288, x, 1400, eta_c=e, eta_t=e, eta_n=min(1.0, e + 0.05))["tsfc"])
            except ValueError:
                ys.append(np.nan)
        ax2.plot(r, ys, color=col, label=f"compressor and turbine efficiency {e}")
    ax2.set_xlabel("pressure ratio r (no unit)")
    ax2.set_ylabel("TSFC (g of fuel per kN per s)")
    ax2.set_ylim(15, 60)
    ax2.set_title("Losses raise the fuel needed per newton")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "tsfc_vs_ratio.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The model has no flight speed or ram compression, no pressure loss in the combustor or duct,
# no cooling air for the turbine blades and constant gas properties. The roadmap adds them.
