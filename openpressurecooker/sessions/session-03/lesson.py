"""Session 3 (Level 3): simulate heating, venting and cooking, and validate the model.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a cooker simulation you can check
# **A. Real-world problem.** How long does a cooker take to heat up, how much water does it
# lose, and how much faster does it really cook lentils than an open pot? We build a lumped
# model (one temperature for the water) with three parts: heating energy balance, a venting
# regulator with a steam-filled headspace, and cooking progress from an Arrhenius rate.
# Then we validate it, test its sensitivity, and look at a blocked-vent failure case to see
# why safety valves exist.
#
# **Safety and scope.** Simplified teaching model, not a design tool. Never modify, block or
# remove the valves of real equipment. The blocked-vent case is a model result only.
#
# **Assumptions.** One uniform water temperature; steam in the headspace is pure saturated
# steam (air already purged) and an ideal gas; constant latent heat 40.7 kJ/mol; no heat loss
# to the room; fixed efficiency from heater to water; the user turns the heat down to a
# "hold" level when boiling starts.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R = 8.314                      # J/(mol K)
L_MOL = 40700.0                # J/mol
M_W = 0.018015                 # kg/mol, water
L_MASS = L_MOL / M_W           # J/kg, about 2.26 MJ/kg
P_ATM = 101.325                # kPa
T_REF = 373.15                 # K
CP_W = 4186.0                  # J/(kg K), liquid water
EA = 82400.0                   # J/mol, activation energy chosen so that Q10 is about 2 near 100 C
D_TARGET = 40.0                # lentils: 40 "equivalent boil minutes" (an open pot needs about 40 min)


# %% [markdown]
# ## Step 1: saturation pressure, headspace steam, and the energy of heating
# Clausius-Clapeyron (Session 2) gives the vapour pressure `psat(T)`. The headspace of volume V
# is full of steam at that pressure; the ideal gas law gives its mass `m_s = psat V M / (R T)`.
# Heating the water raises its enthalpy `H(T) = C T + L_mass m_s(T)`, where
# `C = m_water cp + C_pot` is the heat capacity of water plus pot. The second term is the
# latent heat needed to fill the headspace with steam as it warms.

# %%
def psat_kpa(temp_k):
    return P_ATM * np.exp(L_MOL / R * (1.0 / T_REF - 1.0 / temp_k))


def tsat_k(p_abs_kpa):
    return 1.0 / (1.0 / T_REF - R * np.log(p_abs_kpa / P_ATM) / L_MOL)


def steam_mass(temp_k, v_head):
    """Mass (kg) of saturated steam filling a headspace of v_head m^3 (ideal gas)."""
    return psat_kpa(temp_k) * 1000.0 * v_head * M_W / (R * temp_k)


def enthalpy(temp_k, cap, v_head):
    return cap * temp_k + L_MASS * steam_mass(temp_k, v_head)


_GRID = np.linspace(270.0, 450.0, 36001)


def temp_from_enthalpy(h, cap, v_head):
    return float(np.interp(h, enthalpy(_GRID, cap, v_head), _GRID))


# %% [markdown]
# ## Step 2: cooking progress
# Cooking is a rate process. Arrhenius: `k(T) = exp(-Ea/R (1/T - 1/T_ref))`, equal to 1 at
# 100 C. Doneness `D` is the integral of `k` over time, in "equivalent boil minutes": 1 minute
# at 100 C adds 1. Lentils are done when D = 40. Ea is chosen so the rate about doubles for
# 10 C near 100 C (an illustrative value, not a measured one for lentils).

# %%
def arrhenius(temp_k, ea=EA):
    return np.exp(-ea / R * (1.0 / temp_k - 1.0 / T_REF))


# %% [markdown]
# ## Step 3: the time-stepping simulation
# Each step of `dt` seconds:
# * below the boiling point, net power `eta * P` raises the enthalpy;
# * at the boiling point (the regulator is open, so pressure stays at the set value), the
#   hold power `eta * hold * P` makes steam which leaves, losing `power / L_mass` kg per second;
# * if the vent is blocked, heating continues and pressure follows `psat(T)` upward.

# %%
def simulate(gauge_kpa=100.0, power_w=1000.0, hold=0.25, eta=0.8, m_water=1.0, c_pot=700.0,
             v_head=3e-3, t0_c=25.0, d_target=D_TARGET, dt=1.0, t_max=7200.0,
             vent=True, p_stop_kpa=None, stop_at_done=True):
    """Simulate heating, venting and cooking. Returns a dict of arrays and summary numbers.

    gauge_kpa  regulator setting above the air (0 with v_head=0 is the open pot)
    hold       fraction of full power used once boiling starts
    vent       False means the vent is blocked (failure case)
    p_stop_kpa stop when the absolute pressure reaches this value (blocked case)
    """
    cap = m_water * CP_W + c_pot
    tb = tsat_k(P_ATM + gauge_kpa)
    temp = t0_c + 273.15
    t = 0.0
    rec = {"t": [0.0], "temp_c": [t0_c], "p_abs": [float(psat_kpa(temp))], "done": [0.0], "lost": [0.0]}
    e_in = 0.0
    lost = 0.0
    done = 0.0
    t_boil = None
    t_done = None
    while t < t_max:
        k0 = arrhenius(temp)
        boiling = vent and temp >= tb - 1e-9
        if not boiling:
            e = eta * power_w * dt
            h0 = enthalpy(temp, cap, v_head)
            new = temp_from_enthalpy(h0 + e, cap, v_head)
            if vent and new > tb:
                used = enthalpy(tb, cap, v_head) - h0
                lost += (e - used) / L_MASS
                new = tb
        else:
            e = eta * hold * power_w * dt
            lost += e / L_MASS
            new = tb
        e_in += e
        temp = new
        t += dt
        done += 0.5 * (k0 + arrhenius(temp)) * dt / 60.0
        if t_boil is None and vent and temp >= tb - 1e-9:
            t_boil = t
        rec["t"].append(t)
        rec["temp_c"].append(temp - 273.15)
        rec["p_abs"].append(float(psat_kpa(temp)))
        rec["done"].append(done)
        rec["lost"].append(lost)
        if t_done is None and done >= d_target:
            f = (d_target - rec["done"][-2]) / (rec["done"][-1] - rec["done"][-2])
            t_done = t - dt + f * dt
            if stop_at_done:
                break
        if p_stop_kpa is not None and psat_kpa(temp) >= p_stop_kpa:
            break
    out = {k: np.array(v) for k, v in rec.items()}
    out.update(t_boil=t_boil, t_done=t_done, lost_kg=lost, e_in=e_in, cap=cap, v_head=v_head,
               temp_k=temp, tb=tb, t0_c=t0_c, eta=eta, power_w=power_w, hold=hold)
    return out


def boil_c(gauge_kpa):
    return float(tsat_k(P_ATM + gauge_kpa) - 273.15)


def open_pot(**kw):
    """The same pot without a lid: pressure 1 atmosphere, no headspace of its own."""
    kw.update(gauge_kpa=0.0, v_head=0.0)
    return simulate(**kw)


# %% [markdown]
# ## Step 4: validation tools
# 1. Energy balance: energy supplied = sensible heat + steam in headspace + latent heat carried
#    away by vented steam.
# 2. Hand formula for the heating time, ignoring the headspace: `t = C (T_b - T_0) / (eta P)`.
# 3. Clausius-Clapeyron values against the steam table (Session 2).

# %%
def energy_closure(res):
    """Relative error of the energy balance (supplied versus stored plus vented)."""
    t0 = res["t0_c"] + 273.15
    stored = enthalpy(res["temp_k"], res["cap"], res["v_head"]) - enthalpy(t0, res["cap"], res["v_head"])
    return float((res["e_in"] - stored - L_MASS * res["lost_kg"]) / res["e_in"])


def heatup_time_hand(gauge_kpa=100.0, power_w=1000.0, eta=0.8, m_water=1.0, c_pot=700.0, t0_c=25.0):
    """Hand formula for the time to reach boiling, ignoring the steam in the headspace."""
    cap = m_water * CP_W + c_pot
    return cap * (tsat_k(P_ATM + gauge_kpa) - (t0_c + 273.15)) / (eta * power_w)


def cooker_hold_minutes(open_minutes, gauge_kpa, **kw):
    """Mini-project helper: minutes at pressure (after the regulator starts venting) that match
    a recipe saying the open pot needs `open_minutes` of simmering after it starts boiling."""
    ref = open_pot(stop_at_done=False, d_target=1e9, t_max=open_pot()["t_boil"] + open_minutes * 60.0, **kw)
    target = float(ref["done"][-1])
    res = simulate(gauge_kpa=gauge_kpa, d_target=target, **kw)
    return float((res["t_done"] - res["t_boil"]) / 60.0)


def blocked_vent(power_w=1000.0, p_stop_kpa=300.0, **kw):
    """Failure case: the vent is blocked and the heater stays on full. Model result only."""
    return simulate(power_w=power_w, vent=False, p_stop_kpa=p_stop_kpa, stop_at_done=False, **kw)


def pressure_rise_rate_kpa_per_s(temp_k, dtemp_dt):
    """dP/dt = (dPsat/dT)(dT/dt), with dPsat/dT = Psat L / (R T^2) from Clausius-Clapeyron."""
    return float(psat_kpa(temp_k) * L_MOL / (R * temp_k ** 2) * dtemp_dt)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    ck = simulate(gauge_kpa=100.0)
    op = open_pot()
    print(f"cooker: boils at {ck['t_boil'] / 60:.2f} min, done at {ck['t_done'] / 60:.2f} min, "
          f"water lost {ck['lost_kg'] * 1000:.0f} g, plateau {ck['temp_c'][-1]:.2f} C")
    print(f"open pot: boils at {op['t_boil'] / 60:.2f} min, done at {op['t_done'] / 60:.2f} min, "
          f"water lost {op['lost_kg'] * 1000:.0f} g")
    print(f"hand heat-up time {heatup_time_hand() / 60:.2f} min versus simulated {ck['t_boil'] / 60:.2f} min")
    print(f"energy balance closure {energy_closure(ck):.2e}")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ck_long = simulate(gauge_kpa=100.0, stop_at_done=False, t_max=2900.0)
    op_long = open_pot(stop_at_done=False, t_max=2900.0)
    for res, name in ((ck_long, "cooker, 100 kPa gauge"), (op_long, "open pot")):
        axes[0].plot(res["t"] / 60, res["temp_c"], label=name)
        axes[1].plot(res["t"] / 60, res["done"], label=name)
    axes[1].axhline(D_TARGET, color="red", ls="--", label="lentils done (40)")
    axes[0].set_xlabel("time (min)")
    axes[0].set_ylabel("water temperature (degrees C)")
    axes[0].set_title("Heating: the cooker plateaus hotter")
    axes[1].set_xlabel("time (min)")
    axes[1].set_ylabel("doneness (equivalent boil minutes)")
    axes[1].set_title("Cooking progress race")
    for a in axes:
        a.grid(alpha=0.3)
        a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "heating_and_cooking.png", dpi=120)

    gauges = np.arange(0, 151, 25)
    done_times = [(open_pot() if g == 0 else simulate(gauge_kpa=float(g)))["t_done"] / 60 for g in gauges]
    print("gauge kPa -> total time to done (min):", [f"{g}:{t:.1f}" for g, t in zip(gauges, done_times)])
    powers = [500, 750, 1000, 1500, 2000]
    for pw in powers:
        r = simulate(gauge_kpa=100.0, power_w=float(pw))
        print(f"power {pw:4d} W: boils at {r['t_boil'] / 60:5.2f} min, done at {r['t_done'] / 60:5.2f} min, lost {r['lost_kg'] * 1000:4.0f} g")

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(gauges, done_times, "o-")
    ax2.set_xlabel("regulator gauge pressure (kPa), 0 = open pot")
    ax2.set_ylabel("time until lentils are done (min)")
    ax2.set_title("Sensitivity to valve pressure")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "sensitivity_pressure.png", dpi=120)

    for g in (50.0, 75.0, 100.0, 150.0):
        print(f"40 min open-pot recipe -> hold {cooker_hold_minutes(40.0, g):5.2f} min at {g:.0f} kPa gauge "
              f"(Q10 shortcut: {40.0 / 2 ** ((boil_c(g) - 100.0) / 10.0):5.2f} min)")

    bl = blocked_vent()
    print(f"blocked vent: absolute pressure reaches {bl['p_abs'][-1]:.0f} kPa after {bl['t'][-1] / 60:.2f} min")
    i200 = int(np.argmax(bl["p_abs"] >= 200.0))
    rate = pressure_rise_rate_kpa_per_s(bl["temp_c"][i200] + 273.15, bl["temp_c"][i200 + 1] - bl["temp_c"][i200])
    print(f"pressure rise rate near 200 kPa absolute: {rate:.2f} kPa/s ({rate * 60:.0f} kPa/min)")
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(bl["t"] / 60, bl["p_abs"], label="vent blocked (model)")
    ax3.axhline(P_ATM + 100.0, color="green", ls="--", label="regulator setting (201 kPa abs)")
    ax3.set_xlabel("time (min)")
    ax3.set_ylabel("absolute pressure (kPa)")
    ax3.set_title("Why safety valves exist: no vent, pressure keeps rising")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "blocked_vent.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real cookers lose heat, take time to cool, cook food that has an inside and an outside, and
# have several independent relief devices. This model has none of that. Use it to understand,
# never to design or modify equipment.
