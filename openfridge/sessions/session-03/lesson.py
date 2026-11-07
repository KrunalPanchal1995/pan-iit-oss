"""Session 3 (Level 3): a simplified vapour-compression cycle, validated against Carnot.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a vapour-compression cycle, built and validated
# **A. Real-world problem.** Session 2 assumed that a real fridge reaches some fraction
# `eta2` of the Carnot COP. Where does that fraction come from? Why does a hot kitchen
# hurt, and what does opening the door cost? Today we build the cycle state by state,
# check it against the energy balance and the Carnot bound, and then estimate a yearly
# energy bill.
#
# **Important.** The working fluid below is a TOY refrigerant with illustrative numbers
# chosen so that the model is self-consistent. It is NOT any real refrigerant and the
# results are not data for a real appliance.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ZERO_C = 273.15

# Toy refrigerant (illustrative numbers):
CP = 0.8        # kJ/(kg K): same for liquid and vapour, so the latent heat can stay constant
LATENT = 300.0  # kJ/kg: heat needed to boil 1 kg (taken as constant)
RGAS = 0.10     # kJ/(kg K): gas constant of the vapour (ideal gas)
P_ZERO = 2.9    # bar: illustrative saturation pressure at 0 C


# %% [markdown]
# ## Step 1: properties of the toy fluid
# * Saturation pressure from the Clausius-Clapeyron relation for an ideal vapour with
#   constant latent heat:  `P_sat(T) = P_zero x exp(-(L/R)(1/T - 1/T_zero))`  (T in kelvin).
# * Enthalpy h (kJ/kg), zero for liquid at 0 C:  `h_liquid(T) = cp (T - T_zero)`, and
#   `h_vapour = h_liquid + L` on the saturation line.

# %%
def psat_bar(t_c):
    t = t_c + ZERO_C
    return P_ZERO * np.exp(-(LATENT / RGAS) * (1.0 / t - 1.0 / ZERO_C))


def h_liquid(t_c):
    return CP * t_c


# %% [markdown]
# ## Step 2: the four states
# * State 1: saturated vapour leaves the evaporator at `T_evap`.
# * State 2s: ideal (reversible, isentropic) compression to the condenser pressure.
#   For an ideal gas `T_2s = T_1 (P_cond / P_evap)^(R / cp)`.
# * State 2: real compressor with isentropic efficiency `eta_c`: `h_2 = h_1 + (h_2s - h_1) / eta_c`.
# * State 3: saturated liquid leaves the condenser at `T_cond`.
# * State 4: expansion valve, enthalpy does not change: `h_4 = h_3` (some liquid flashes to vapour).

# %%
def cycle(t_evap_c, t_cond_c, eta_c=0.7):
    """States and energies (per kg of refrigerant) of the simplified cycle. Temperatures in Celsius."""
    if t_cond_c <= t_evap_c:
        raise ValueError("the condenser must be hotter than the evaporator")
    if not 0 < eta_c <= 1:
        raise ValueError("compressor efficiency must be above 0 and at most 1")
    te = t_evap_c + ZERO_C
    p_e, p_c = psat_bar(t_evap_c), psat_bar(t_cond_c)
    h1 = h_liquid(t_evap_c) + LATENT
    t2s = te * (p_c / p_e) ** (RGAS / CP)
    h2s = h1 + CP * (t2s - te)
    h2 = h1 + (h2s - h1) / eta_c
    h3 = h_liquid(t_cond_c)
    h4 = h3
    return {
        "t_evap": t_evap_c, "t_cond": t_cond_c, "p_evap": p_e, "p_cond": p_c,
        "t2s": t2s - ZERO_C, "t2": t_evap_c + (h2 - h1) / CP,
        "h1": h1, "h2s": h2s, "h2": h2, "h3": h3, "h4": h4,
        "quality4": (h4 - h_liquid(t_evap_c)) / LATENT,
        "q_evap": h1 - h4, "work": h2 - h1, "q_cond": h2 - h3,
        "cop": (h1 - h4) / (h2 - h1),
    }


# %% [markdown]
# ## Step 3: from the cycle to a whole fridge
# Heat must flow *in* to the refrigerant, so the evaporator is colder than the food space by
# `dt_ev`; heat must flow *out*, so the condenser is hotter than the room by `dt_cd`.
# The Carnot limit uses the real reservoirs (inside and room), so
# `eta2 = COP / COP_Carnot(inside, room)` is now a result, not an assumption.

# %%
def fridge(t_inside_c, t_room_c, eta_c=0.7, dt_ev=8.0, dt_cd=10.0):
    r = cycle(t_inside_c - dt_ev, t_room_c + dt_cd, eta_c)
    cop_carnot = (t_inside_c + ZERO_C) / (t_room_c - t_inside_c)
    r["t_inside"], r["t_room"] = t_inside_c, t_room_c
    r["cop_carnot"] = cop_carnot
    r["eta2"] = r["cop"] / cop_carnot
    # entropy generated per kg of refrigerant [kJ/(kg K)]: heat to the room over T_room minus heat from the inside over T_inside
    r["s_gen"] = r["q_cond"] / (t_room_c + ZERO_C) - r["q_evap"] / (t_inside_c + ZERO_C)
    return r


# %% [markdown]
# ## Step 4: loads, duty cycle and yearly energy
# * Wall leak `UA (T_room - T_inside)`.
# * Door opening: each opening swaps `V_air` of inside air for room air, costing
#   `rho cp_air V_air (T_room - T_inside)` (sensible heat only; moisture is ignored,
#   so real door loads are larger).
# * Duty cycle `d = load / capacity` (fraction of time the compressor runs). Capacity is the
#   cooling power while it runs. Electric power while running is `capacity / COP`.
# * Yearly energy `E = (d x capacity / COP + overhead) x 8760 h`.

# %%
RHO_AIR, CP_AIR, V_DOOR = 1.2, 1.006, 0.15   # kg/m3, kJ/(kg K), m3 swapped per opening


def door_load_w(openings_per_day, t_room_c, t_inside_c):
    """Average heat load of door openings in watts."""
    joules = RHO_AIR * CP_AIR * V_DOOR * (t_room_c - t_inside_c) * 1000.0
    return openings_per_day * joules / 86400.0


def fridge_year(t_room_c, openings_per_day=30, ua=3.0, t_inside_c=4.0, capacity_w=150.0,
                eta_c=0.7, overhead_w=5.0, tariff=8.0):
    """Yearly energy (kWh), cost (illustrative tariff per kWh) and duty cycle."""
    f = fridge(t_inside_c, t_room_c, eta_c)
    load = ua * (t_room_c - t_inside_c) + door_load_w(openings_per_day, t_room_c, t_inside_c)
    duty = load / capacity_w
    p_run = capacity_w / f["cop"]
    kwh = (min(duty, 1.0) * p_run + overhead_w) * 8760.0 / 1000.0
    return {"load_w": load, "duty": duty, "cop": f["cop"], "p_run_w": p_run, "kwh": kwh, "cost": kwh * tariff,
            "holds_temperature": duty <= 1.0}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    r = cycle(-8, 35, 0.7)
    print("states: p_evap %.2f bar, p_cond %.2f bar, T2s %.1f C, T2 %.1f C, quality after valve %.3f"
          % (r["p_evap"], r["p_cond"], r["t2s"], r["t2"], r["quality4"]))
    print("per kg: q_evap %.1f, work %.1f, q_cond %.1f kJ; COP %.2f" % (r["q_evap"], r["work"], r["q_cond"], r["cop"]))
    f = fridge(4, 25, 0.7)
    print("whole fridge 4 C / 25 C: COP %.2f, Carnot %.2f, eta2 %.2f, entropy generated %.4f kJ/(kg K)"
          % (f["cop"], f["cop_carnot"], f["eta2"], f["s_gen"]))

    # P-h diagram
    ts = np.linspace(-30, 60, 91)
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.plot([h_liquid(t) for t in ts], [psat_bar(t) for t in ts], "k-", lw=1)
    ax.plot([h_liquid(t) + LATENT for t in ts], [psat_bar(t) for t in ts], "k-", lw=1)
    pts = {"1": (r["h1"], r["p_evap"]), "2": (r["h2"], r["p_cond"]), "3": (r["h3"], r["p_cond"]), "4": (r["h4"], r["p_evap"])}
    loop = ["1", "2", "3", "4", "1"]
    ax.plot([pts[k][0] for k in loop], [pts[k][1] for k in loop], "o-", color="tab:blue")
    for k, (h, p) in pts.items():
        ax.annotate(k, (h, p), textcoords="offset points", xytext=(6, 6))
    ax.set_yscale("log")
    ax.set_xlabel("specific enthalpy h (kJ/kg)")
    ax.set_ylabel("pressure P (bar, log scale)")
    ax.set_title("Toy refrigerant cycle on a P-h diagram (illustrative)")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "ph_diagram.png", dpi=120)

    # sensitivity to condenser temperature
    tcs = np.linspace(25, 55, 31)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for eta, col in ((1.0, "tab:green"), (0.7, "tab:blue"), (0.5, "tab:red")):
        ax2.plot(tcs, [cycle(-8, t, eta)["cop"] for t in tcs], color=col, label=f"compressor eta_c = {eta}")
    ax2.plot(tcs, [(-8 + ZERO_C) / (t + 8) for t in tcs], "k--", label="Carnot between -8 C and T_cond")
    ax2.set_xlabel("condenser temperature (C)")
    ax2.set_ylabel("COP (no unit)")
    ax2.set_title("COP falls with condenser temperature (evaporator -8 C)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "cop_vs_condenser.png", dpi=120)

    # energy versus room temperature, with the door load
    rooms = np.arange(18, 41, 1.0)
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.2))
    for n, col in ((10, "tab:green"), (30, "tab:blue"), (80, "tab:red")):
        ax3.plot(rooms, [fridge_year(t, n)["kwh"] for t in rooms], color=col, label=f"{n} door openings per day")
    ax3.set_xlabel("room temperature (C)")
    ax3.set_ylabel("energy per year (kWh)")
    ax3.set_title("Yearly energy of the toy fridge")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "energy_vs_room.png", dpi=120)
    for t in (22, 28, 34):
        y = fridge_year(t)
        print("room %d C: load %.1f W, duty %.2f, COP %.2f, %.0f kWh/year, cost %.0f" % (t, y["load_w"], y["duty"], y["cop"], y["kwh"], y["cost"]))

# %% [markdown]
# ## Where this stops
# Real refrigerants are not ideal gases, real compressors have losses that depend on the
# pressure ratio, and heat exchangers need area and fans. The Target shows what a richer
# model looks like; see `promo/roadmap.md`.
