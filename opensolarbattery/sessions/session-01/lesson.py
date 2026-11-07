"""Session 1 (Level 1): one day of sunshine against one day of household demand.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a day of sun against a day of demand
# **A. Real-world problem.** A rooftop solar array makes power only when the sun is up, but a
# home uses power morning and evening. Where the solar curve is above the demand curve there is
# a *surplus*; where it is below there is a *deficit* that must come from somewhere else
# (the grid or a battery). Today you draw both curves and measure the two areas.
# This is an educational model, not an installation design.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
DT = 0.1                                   # time step of the fine grid, hours
T = (np.arange(240) + 0.5) * DT            # 240 mid-step times covering 0 to 24 h
SUNRISE, SUNSET = 6.0, 18.0                # a 12 hour day


# %% [markdown]
# ## Step 1: the solar curve
# A bell-shaped half sine between sunrise and sunset:
#
#     P_pv(t) = P_peak * sun * sin(pi (t - 6) / 12)     for 6 <= t <= 18, else 0
#
# `P_peak` is the array rating in **kW** (output in full sun at noon) and `sun` (0 to 1) says how
# clear the day is. Daily energy = area under the curve, in **kWh** (kW times hours).
# Remember: kW is the *rate* (like speed), kWh is the *total* (like distance).

# %%
def solar_power(t, peak_kw, sun=1.0):
    t = np.asarray(t, dtype=float)
    s = np.sin(np.pi * (t - SUNRISE) / (SUNSET - SUNRISE))
    return peak_kw * sun * np.where((t >= SUNRISE) & (t <= SUNSET), s, 0.0)


# %% [markdown]
# ## Step 2: the household demand curve
# A small base load all day, a morning bump (cooking, getting ready) and a bigger evening bump
# (lights, cooking, appliances). We draw the *shape* and then scale it so the area under the
# curve equals the daily energy you choose.

# %%
def demand_shape(t):
    t = np.asarray(t, dtype=float)
    return 0.3 + 1.0 * np.exp(-0.5 * ((t - 7.5) / 1.2) ** 2) + 1.6 * np.exp(-0.5 * ((t - 19.0) / 2.0) ** 2)


def demand_power(t, daily_kwh):
    """Household demand in kW so that the 24 hour area equals daily_kwh."""
    scale = daily_kwh / (demand_shape(T).sum() * DT)
    return scale * demand_shape(t)


# %% [markdown]
# ## Step 3: measure surplus and deficit
# * area under a curve  =  sum of (height x step width)
# * **surplus** = area where solar is above demand (extra energy, nowhere to go yet)
# * **deficit** = area where demand is above solar (energy that must come from elsewhere)
# * **direct use** = energy the home takes straight from the panels = area under the lower curve

# %%
def day_balance(peak_kw, daily_kwh, sun=1.0):
    pv = solar_power(T, peak_kw, sun)
    load = demand_power(T, daily_kwh)
    pv_kwh = float(pv.sum() * DT)
    load_kwh = float(load.sum() * DT)
    direct = float(np.minimum(pv, load).sum() * DT)
    surplus = float(np.maximum(pv - load, 0).sum() * DT)
    deficit = float(np.maximum(load - pv, 0).sum() * DT)
    return {"pv_kwh": pv_kwh, "load_kwh": load_kwh, "direct_kwh": direct, "surplus_kwh": surplus,
            "deficit_kwh": deficit, "solar_share": direct / load_kwh,
            "self_consumption": direct / pv_kwh if pv_kwh > 0 else 0.0}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    pk, daily = 4.0, 10.0
    b = day_balance(pk, daily)
    pv, load = solar_power(T, pk), demand_power(T, daily)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(T, pv, color="tab:orange", lw=2, label="solar output")
    ax.plot(T, load, color="tab:blue", lw=2, label="household demand")
    ax.fill_between(T, pv, load, where=pv > load, color="tab:green", alpha=0.35, label=f"surplus {b['surplus_kwh']:.1f} kWh")
    ax.fill_between(T, pv, load, where=load > pv, color="tab:red", alpha=0.30, label=f"deficit {b['deficit_kwh']:.1f} kWh")
    ax.set_xlim(0, 24)
    ax.set_xlabel("time of day (hours)")
    ax.set_ylabel("power (kW)")
    ax.set_title("A 4 kW array against a 10 kWh/day home, one clear day")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "day_curves.png", dpi=120)

    sizes = np.arange(0, 8.01, 0.5)
    stats = [day_balance(s, daily) for s in sizes]
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    ax2.plot(sizes, [s["solar_share"] * 100 for s in stats], "o-", label="share of demand met directly by solar")
    ax2.plot(sizes, [s["self_consumption"] * 100 for s in stats], "s-", label="share of solar used directly")
    ax2.set_xlabel("array size (kW)")
    ax2.set_ylabel("percent (%)")
    ax2.set_title("Bigger array: more demand met, but more solar wasted")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "share_vs_size.png", dpi=120)
    for k, v in b.items():
        print(f"{k:18s} {v:8.3f}")
    print("daily solar energy per kW (clear day):", round(float(solar_power(T, 1.0).sum() * DT), 3), "kWh; exact 24/pi =", round(24 / np.pi, 3))
    for s in (1, 2, 3, 4, 6, 8):
        print(s, "kW:", {k: round(v, 3) for k, v in day_balance(s, daily).items()})
