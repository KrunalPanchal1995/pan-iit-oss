"""Session 2 (Level 2): COP, the Carnot limit, house heat loss and sizing.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: COP, the Carnot limit and sizing a heat pump
# **A. Real-world problem.** A family wants to heat a house with a heat pump. How big must it
# be so the house stays warm on the coldest design night? How much electricity will it use over
# the winter compared with a resistance heater? And how cold must it get outside before the
# heat pump is no longer clearly better?
#
# **Plan.** (1) COP and the Carnot limit, (2) real COP against outdoor temperature, (3) house
# heat loss and sizing, (4) seasonal energy and cost, (5) a design question solved backwards.
#
# Educational model only, not an installation design.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
ETA = 0.45            # real COP as a fraction of Carnot: typical, 0.4 to 0.5
COP_MAX = 8.0         # real machines never reach the huge Carnot values for tiny temperature gaps
TARIFF = 0.25         # illustrative price, money units per kWh of electricity


# %% [markdown]
# ## Step 1: COP and the Carnot limit
# A heat pump takes heat Q_cold from outside and uses work W; it delivers Q_hot = Q_cold + W
# (energy is conserved). Its cooling COP is Q_cold / W (what a fridge cares about) and its
# heating COP is Q_hot / W. Dividing Q_hot = Q_cold + W by W gives
#
#     COP_heating = COP_cooling + 1
#
# An ideal (reversible, Carnot) machine moves heat so that Q_hot / Q_cold = T_hot / T_cold
# (kelvin). Then W = Q_hot - Q_cold = Q_hot (1 - T_cold / T_hot), so
#
#     COP_heating(Carnot) = T_hot / (T_hot - T_cold)        T in kelvin

# %%
def kelvin(t_celsius):
    return np.asarray(t_celsius, dtype=float) + 273.15


def cop_heating_from_cooling(cop_cooling):
    return cop_cooling + 1.0


def carnot_cop_cooling(t_cold_c, t_hot_c):
    return kelvin(t_cold_c) / (kelvin(t_hot_c) - kelvin(t_cold_c))


def carnot_cop_heating(t_hot_c, t_cold_c):
    lift = kelvin(t_hot_c) - kelvin(t_cold_c)
    if np.any(lift <= 0):
        raise ValueError("t_hot must be above t_cold")
    return kelvin(t_hot_c) / lift


def real_cop(t_out_c, t_sup_c, eta=ETA, cop_max=COP_MAX):
    """Real COP = eta x Carnot, limited to cop_max when the temperature gap is small."""
    return np.minimum(eta * carnot_cop_heating(t_sup_c, t_out_c), cop_max)


# %% [markdown]
# ## Step 2: the house loses heat, so the heat pump must replace it
# Heat leaks out through walls, roof, windows and air changes. For a steady indoor
# temperature T_in and outdoor T_out the loss is
#
#     Q_loss = UA (T_in - T_out)
#
# where UA (kW per K) adds up area times U-value over the whole envelope. The heat pump must
# deliver at least Q_loss. Sizing uses a **design temperature**: a cold outdoor temperature
# that is rarely reached. Electricity used = Q / COP.

# %%
def heat_loss_kw(ua, t_in_c, t_out_c):
    """Steady heat loss in kW (zero if it is warmer outside than inside)."""
    return ua * np.maximum(np.asarray(t_in_c, dtype=float) - t_out_c, 0.0)


def electric_kw(q_kw, cop):
    return q_kw / cop


# %% [markdown]
# ## Step 3: a winter of daily temperatures, and the energy bill
# Illustrative heating season of 151 days (mid October to mid March). The daily mean
# temperature is a cosine: warmest at the two ends, coldest in the middle, between 9 C and
# -3 C. For each day the house needs 24 h x Q_loss kWh; a heater uses that much electricity, a
# heat pump uses it divided by that day's COP.

# %%
def season_temps(n_days=151, t_mean=3.0, amp=6.0):
    d = np.arange(n_days)
    return t_mean + amp * np.cos(2 * np.pi * (d + 0.5) / n_days)


def season_energy(ua, t_in_c=20.0, t_sup_c=35.0, eta=ETA, tariff=TARIFF, temps=None):
    """Heat needed, electricity for a heater and for a heat pump (kWh), seasonal COP, costs."""
    temps = season_temps() if temps is None else np.asarray(temps, dtype=float)
    heat = 24.0 * heat_loss_kw(ua, t_in_c, temps)           # kWh per day
    cop = real_cop(temps, t_sup_c, eta)
    hp = heat / cop
    out = dict(heat_kwh=float(heat.sum()), heater_kwh=float(heat.sum()), hp_kwh=float(hp.sum()))
    out["seasonal_cop"] = out["heat_kwh"] / out["hp_kwh"]
    out["heater_cost"] = out["heater_kwh"] * tariff
    out["hp_cost"] = out["hp_kwh"] * tariff
    return out


# %% [markdown]
# ## Step 4: a design question solved backwards
# At which outdoor temperature does the COP fall to a chosen value c? Set
# eta T_hot / (T_hot - T_cold) = c and solve for T_cold:
#
#     T_cold = T_hot (1 - eta / c)       (kelvin)
#
# With c = 1 the heat pump would only match a resistance heater; in this simple model that
# happens at a ridiculously low temperature, so in practice what ends a heat pump's usefulness
# is its capacity, not its COP.

# %%
def outdoor_temp_for_cop(cop_target, t_sup_c, eta=ETA):
    """Outdoor temperature (C) at which eta x Carnot equals cop_target."""
    return float(kelvin(t_sup_c) * (1.0 - eta / cop_target) - 273.15)


def design_size_kw(ua, t_in_c, t_design_c):
    return float(heat_loss_kw(ua, t_in_c, t_design_c))


# %%
UA = 0.20     # kW per K: a moderately insulated 100 square metre house (illustrative)

if __name__ == "__main__":
    print(f"COP_cooling 3.0 -> COP_heating {cop_heating_from_cooling(3.0):.1f}")
    print(f"Carnot COP_h, 35 C supply, 0 C outdoors: {float(carnot_cop_heating(35, 0)):.2f}; real {float(real_cop(0, 35)):.2f}")
    q = design_size_kw(UA, 20.0, -10.0)
    print(f"design load at -10 C: {q:.2f} kW; electricity {float(electric_kw(q, real_cop(-10, 35))):.2f} kW (heat pump) vs {q:.2f} kW (heater)")
    s = season_energy(UA)
    print(f"season: heat {s['heat_kwh']:.0f} kWh; heater {s['heater_kwh']:.0f} kWh = {s['heater_cost']:.0f}; "
          f"heat pump {s['hp_kwh']:.0f} kWh = {s['hp_cost']:.0f}; seasonal COP {s['seasonal_cop']:.2f}")
    for c in (3.0, 2.0, 1.0):
        print(f"COP falls to {c:.0f} at outdoor {outdoor_temp_for_cop(c, 35):.1f} C (35 C supply), {outdoor_temp_for_cop(c, 55):.1f} C (55 C supply)")

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    to = np.linspace(-20, 15, 71)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].plot(to, carnot_cop_heating(35, to), "k--", label="Carnot limit, 35 C supply")
    axs[0].plot(to, real_cop(to, 35), label="real (0.45 x Carnot), 35 C supply")
    axs[0].plot(to, real_cop(to, 55), label="real, 55 C supply")
    axs[0].axhline(1, color="gray", ls=":", label="resistance heater")
    axs[0].set_ylim(0, 10)
    axs[0].set_xlabel("outdoor temperature (C)")
    axs[0].set_ylabel("heating COP (no unit)")
    axs[0].set_title("COP falls as it gets colder")
    axs[0].grid(alpha=0.3)
    axs[0].legend(fontsize=7)
    load = heat_loss_kw(UA, 20.0, to)
    axs[1].plot(to, load, label="heater electricity = house heat loss")
    axs[1].plot(to, electric_kw(load, real_cop(to, 35)), label="heat pump electricity (35 C supply)")
    axs[1].axvline(-10, color="red", ls="--", label="design temperature -10 C")
    axs[1].set_xlabel("outdoor temperature (C)")
    axs[1].set_ylabel("power (kW)")
    axs[1].set_title("Heat loss and electricity needed, UA = 0.20 kW/K")
    axs[1].grid(alpha=0.3)
    axs[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "cop_and_load.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.2, 4))
    t = season_temps()
    ax2.plot(t, color="#2a6fa8")
    ax2.set_xlabel("day of the heating season (0 = mid October)")
    ax2.set_ylabel("daily mean outdoor temperature (C)")
    ax2.set_title("Illustrative heating-season temperatures")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "season_temps.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Daily means hide the cold nights, the house has no thermal mass, the capacity of a real heat
# pump also falls in the cold, and there is no defrost. Session 3 simulates all of that hour by
# hour.
