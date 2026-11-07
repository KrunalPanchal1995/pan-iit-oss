"""Session 3 (Level 3): an hourly winter simulation of a house with a heat pump.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate a winter, hour by hour
# **A. Real-world problem.** Session 2 used daily average temperatures and ignored the house's
# thermal mass, the capacity of the machine and its backup heater. Real winters have cold
# nights, and a house cools slowly. Today you simulate a whole heating season hour by hour,
# check the program against energy conservation and a hand calculation, test how insulation,
# supply temperature and tariff change the bill, and find out what happens on the coldest night
# when the heat pump is too small.
#
# Educational model only, not an installation design.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ETA = 0.45            # real COP as a fraction of Carnot (typical)
COP_MAX = 8.0
DEFROST_BELOW_C = 2.0  # below this outdoor temperature frost builds up on the outdoor coil
DEFROST_FACTOR = 0.90  # simple derate of the COP while that happens (illustrative)
TARIFF = 0.25          # illustrative money units per kWh


# %% [markdown]
# ## Step 1: the machine
# COP = eta x Carnot (kelvin), capped, and multiplied by a defrost factor below 2 C.
# Heating capacity also falls in the cold: here 2 percent per kelvin below 7 C (illustrative),
# never below 30 percent of the rated value (rated = capacity at 7 C outdoors).

# %%
def cop_hp(t_out_c, t_sup_c, eta=ETA):
    t_out = np.asarray(t_out_c, dtype=float)
    lift = np.maximum(t_sup_c - t_out, 5.0)
    cop = np.minimum(eta * (t_sup_c + 273.15) / lift, COP_MAX)
    return np.where(t_out < DEFROST_BELOW_C, cop * DEFROST_FACTOR, cop)


def capacity_kw(t_out_c, rated_kw):
    return rated_kw * np.maximum(1.0 + 0.02 * (np.asarray(t_out_c, dtype=float) - 7.0), 0.3)


# %% [markdown]
# ## Step 2: the weather
# Seeded synthetic winter: seasonal cosine (-3 C in mid season, 9 C at the ends), a daily
# swing of 3 K (coldest at 03:00), and day-to-day weather noise (an AR(1) series with a
# fixed seed, so every run gives the same winter).

# %%
def weather(n_days=151, seed=7):
    rng = np.random.default_rng(seed)
    noise = np.zeros(n_days + 1)
    for i in range(1, n_days + 1):
        noise[i] = 0.7 * noise[i - 1] + rng.normal(0.0, 2.4)
    h = np.arange(24 * n_days)
    seasonal = 3.0 + 6.0 * np.cos(2 * np.pi * h / (24 * n_days))
    daily = 3.0 * np.cos(2 * np.pi * ((h % 24) - 15) / 24)
    return seasonal + daily + np.interp(h / 24.0, np.arange(n_days + 1), noise)


def cold_week(hours=168):
    """A deterministic cold week (no random numbers) used by the live app: coldest near hour 100."""
    h = np.arange(hours, dtype=float)
    return -2.0 + 3.0 * np.cos(2 * np.pi * (h - 15) / 24) - 6.0 * np.exp(-(((h - 100) / 30) ** 2))


# %% [markdown]
# ## Step 3: the house as one thermal capacity (an RC model)
# C dT/dt = Q_heat - UA (T - T_out), with C in kWh per K and UA in kW per K. The time constant
# is tau = C / UA hours. For heat Q held constant during one step the exact solution is
#
#     T_next = T_eq + (T - T_eq) exp(-dt / tau),     T_eq = T_out + Q / UA
#
# so the simulation is stable for any step. The thermostat asks for the heat that would bring
# the house to the set point at the end of the step (never negative). The heat pump supplies up
# to its capacity; a backup resistance heater (up to backup_kw) supplies the rest.

# %%
def simulate(t_out, ua=0.20, cap_c=4.0, t_set=20.0, t_sup=35.0, rated_kw=9.0, backup_kw=9.0,
             eta=ETA, tariff=TARIFF, mode="heat_pump", dt=1.0, t0=None):
    """Hourly simulation. mode = 'heat_pump' or 'heater' (resistance heater only, max backup_kw)."""
    t_out = np.asarray(t_out, dtype=float)
    n = len(t_out)
    tau = cap_c / ua
    e = np.exp(-dt / tau)
    t_in = np.empty(n + 1)
    t_in[0] = t_set if t0 is None else t0
    q_hp, q_bu, elec, t_mean = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
    cop = cop_hp(t_out, t_sup, eta)
    cap = capacity_kw(t_out, rated_kw)
    for i in range(n):
        t_eq_wanted = (t_set - t_in[i] * e) / (1.0 - e)
        demand = max(ua * (t_eq_wanted - t_out[i]), 0.0)
        if mode == "heat_pump":
            q_hp[i] = min(demand, cap[i])
            q_bu[i] = min(demand - q_hp[i], backup_kw)
        else:
            q_bu[i] = min(demand, backup_kw)
        q = q_hp[i] + q_bu[i]
        t_eq = t_out[i] + q / ua
        t_in[i + 1] = t_eq + (t_in[i] - t_eq) * e
        t_mean[i] = t_eq + (t_in[i] - t_eq) * (tau / dt) * (1.0 - e)   # mean indoor T during the hour
        elec[i] = (q_hp[i] / cop[i] + q_bu[i]) * dt
    heat = float(((q_hp + q_bu) * dt).sum())
    total = float(elec.sum())
    return dict(t_in=t_in, t_out=t_out, q_hp=q_hp, q_bu=q_bu, elec=elec, cop=cop, t_mean=t_mean,
                heat_kwh=heat, elec_kwh=total, cost=total * tariff, backup_kwh=float((q_bu * dt).sum()),
                min_t_in=float(t_in.min()), seasonal_cop=heat / total if total > 0 else float("nan"),
                ua=ua, cap_c=cap_c, dt=dt)


# %% [markdown]
# ## Step 4: validate the simulation
# 1. **Energy conservation.** Stored energy change C (T_end - T_start) must equal the heat
#    supplied minus the heat lost through the walls, sum of UA (T_mean - T_out) dt.
# 2. **Steady state by hand.** With constant outdoor temperature and a big enough machine the
#    house settles at the set point; the heat needed is UA (T_set - T_out) and the electricity
#    is that divided by the COP.

# %%
def energy_residual(res):
    """Stored energy change minus (heat in - heat lost), in kWh. Should be about 0."""
    dt = res["dt"]
    stored = res["cap_c"] * (res["t_in"][-1] - res["t_in"][0])
    supplied = float(((res["q_hp"] + res["q_bu"]) * dt).sum())
    lost = float((res["ua"] * (res["t_mean"] - res["t_out"]) * dt).sum())
    return stored - (supplied - lost)


def steady_electric_kw(ua, t_set, t_out_c, t_sup_c, eta=ETA):
    """Hand calculation: electric power when the house sits at the set point."""
    return ua * (t_set - t_out_c) / float(cop_hp(t_out_c, t_sup_c, eta))


# %% [markdown]
# ## Step 5: the season, the sensitivity and the failure case

# %%
def size_rated_kw(ua, t_set, t_design_c):
    """Rated (7 C) capacity so that capacity at the design temperature equals the heat loss."""
    return ua * (t_set - t_design_c) / float(capacity_kw(t_design_c, 1.0))


if __name__ == "__main__":
    T = weather()
    print(f"winter: {len(T)} hours, mean {T.mean():.2f} C, coldest {T.min():.1f} C at hour {int(T.argmin())}")
    rated = size_rated_kw(0.20, 20.0, -10.0)
    hp = simulate(T, rated_kw=rated)
    ht = simulate(T, mode="heater", backup_kw=20.0)
    print(f"rated size for -10 C design: {rated:.2f} kW")
    print(f"heater   : {ht['elec_kwh']:.0f} kWh, cost {ht['cost']:.0f}, min indoor {ht['min_t_in']:.2f} C")
    print(f"heat pump: {hp['elec_kwh']:.0f} kWh, cost {hp['cost']:.0f}, seasonal COP {hp['seasonal_cop']:.2f}, "
          f"backup {hp['backup_kwh']:.1f} kWh, min indoor {hp['min_t_in']:.2f} C")
    print(f"energy residual: {energy_residual(hp):.2e} kWh")
    st = simulate(np.zeros(400), rated_kw=9.0)
    print(f"steady state at 0 C: sim {st['elec'][-1]:.4f} kW, hand {steady_electric_kw(0.2, 20.0, 0.0, 35.0):.4f} kW")
    print("sensitivity (season cost, heat pump / heater):")
    for ua in (0.12, 0.20, 0.30):
        a = simulate(T, ua=ua, rated_kw=size_rated_kw(ua, 20.0, -10.0))
        b = simulate(T, ua=ua, mode="heater", backup_kw=20.0)
        print(f"  UA {ua:.2f}: {a['cost']:.0f} / {b['cost']:.0f}")
    for ts in (30.0, 35.0, 45.0, 55.0):
        a = simulate(T, t_sup=ts, rated_kw=rated)
        print(f"  supply {ts:.0f} C: cost {a['cost']:.0f}, seasonal COP {a['seasonal_cop']:.2f}")
    for tar in (0.15, 0.25, 0.40):
        print(f"  tariff {tar:.2f}: heat pump {hp['elec_kwh'] * tar:.0f}, heater {ht['elec_kwh'] * tar:.0f}")
    # failure: undersized pump on the coldest night
    i0 = int(T.argmin())
    sl = slice(max(i0 - 48, 0), i0 + 24)
    for label, kw in (("sized", rated), ("undersized 5 kW, backup 9 kW", 5.0)):
        r = simulate(T[sl], rated_kw=kw if kw == rated else 5.0)
        print(f"  {label}: min indoor {r['min_t_in']:.2f} C, backup {r['backup_kwh']:.1f} kWh, elec {r['elec_kwh']:.1f} kWh")
    r = simulate(T[sl], rated_kw=5.0, backup_kw=0.0)
    print(f"  undersized 5 kW, no backup: min indoor {r['min_t_in']:.2f} C")

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # Figure 1: the coldest days of the winter, sized and undersized
    sl = slice(max(i0 - 72, 0), i0 + 48)
    hrs = np.arange(sl.start, sl.stop)
    fig, axs = plt.subplots(2, 1, figsize=(8.5, 6), sharex=True)
    axs[0].plot(hrs, T[sl], color="#2a6fa8", label="outdoor")
    for label, kw, bu, col in ((f"indoor, sized {rated:.1f} kW", rated, 9.0, "#2a9d8f"), ("indoor, 5 kW and no backup", 5.0, 0.0, "#d9534f")):
        r = simulate(T[sl], rated_kw=kw, backup_kw=bu)
        axs[0].plot(hrs, r["t_in"][1:], color=col, label=label)
    axs[0].set_ylabel("temperature (C)")
    axs[0].set_title("The coldest days: a small heat pump without backup loses the set point")
    axs[0].legend(fontsize=8)
    axs[0].grid(alpha=0.3)
    r = simulate(T[sl], rated_kw=5.0)
    axs[1].stackplot(hrs, r["q_hp"], r["q_bu"], labels=["heat pump heat", "backup resistance heat"], colors=["#2a9d8f", "#d9534f"])
    axs[1].set_xlabel("hour of the winter")
    axs[1].set_ylabel("heat delivered (kW)")
    axs[1].set_title("5 kW heat pump with a 9 kW backup: the backup takes over on the coldest night")
    axs[1].legend(fontsize=8, loc="upper left")
    axs[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "coldest_nights.png", dpi=120)

    # Figure 2: validation
    fig2, axs2 = plt.subplots(1, 2, figsize=(10, 4))
    outs = np.linspace(-10, 12, 12)
    sim_kw = [simulate(np.full(300, t), rated_kw=15.0)["elec"][-1] for t in outs]
    axs2[0].plot(outs, [steady_electric_kw(0.20, 20.0, t, 35.0) for t in outs], "-", label="hand calculation")
    axs2[0].plot(outs, sim_kw, "o", ms=5, label="simulation (after 300 h)")
    axs2[0].set_xlabel("constant outdoor temperature (C)")
    axs2[0].set_ylabel("electric power (kW)")
    axs2[0].set_title("Steady state: simulation versus UA (T_set - T_out) / COP")
    axs2[0].legend(fontsize=8)
    axs2[0].grid(alpha=0.3)
    uas = np.linspace(0.1, 0.4, 7)
    sim_e = [simulate(T, ua=u, rated_kw=size_rated_kw(u, 20.0, -10.0))["elec_kwh"] for u in uas]
    axs2[1].plot(uas, sim_e, "o-", label="heat pump electricity")
    axs2[1].set_xlabel("UA (kW per K)")
    axs2[1].set_ylabel("winter electricity (kWh)")
    axs2[1].set_title("Better insulation (smaller UA) cuts the bill")
    axs2[1].grid(alpha=0.3)
    axs2[1].legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "validation_and_ua.png", dpi=120)

# %% [markdown]
# ## Where this stops
# One lumped capacity, perfect set-point control, a fixed supply temperature, no hot water, no
# solar or internal gains, an invented capacity curve and defrost factor, and a synthetic
# winter. Real design needs a certified calculation and local weather data.
