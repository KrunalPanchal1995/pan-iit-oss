"""Session 2 (Level 2): hourly energy balance with a battery, and a sizing design problem.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the hourly energy balance with a battery
# **A. Real-world problem.** Session 1 showed that solar alone covers less than half of a
# home's demand, because the sun is up when nobody needs the power. A battery stores the midday
# surplus for the evening. How large must the array and the battery be so that the grid
# supplies only 10 percent of the home's energy? And what does each extra kW or kWh cost?
# All costs here are *illustrative units*, not market prices. Educational model only.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
H = (np.arange(24) + 0.5)                  # mid-hour times, 24 steps of 1 hour
DT = 1.0                                   # hours per step
COST_PV, COST_BATT = 1000.0, 400.0         # ILLUSTRATIVE cost units per kW and per kWh (not prices)


# %% [markdown]
# ## Step 1: hourly solar and demand
# Same shapes as Session 1, sampled at the middle of each hour. Energy in an hour = power x 1 h.

# %%
def pv_profile(peak_kw, sun=1.0):
    s = np.sin(np.pi * (H - 6.0) / 12.0)
    return peak_kw * sun * np.where((H >= 6.0) & (H <= 18.0), s, 0.0)


def load_profile(daily_kwh):
    shape = 0.3 + 1.0 * np.exp(-0.5 * ((H - 7.5) / 1.2) ** 2) + 1.6 * np.exp(-0.5 * ((H - 19.0) / 2.0) ** 2)
    return daily_kwh * shape / (shape.sum() * DT)


# %% [markdown]
# ## Step 2: the battery rules
# Let `net = pv - load` in one hour (kW).
# * **Surplus (net > 0):** charge the battery, limited by the power limit `p_max` and by the
#   free space. A fraction `eta_c` of the energy that goes in is stored.
# * **Deficit (net < 0):** discharge, limited by `p_max` and by what is stored. The house
#   receives `eta_d` times the energy taken out of the store.
# * Whatever the battery cannot cover is **imported** from the grid; surplus it cannot take is
#   **exported** (or wasted).
#
# Round-trip efficiency `eta = eta_c * eta_d`, so each way is `sqrt(eta)`.
# State of charge `soc` (kWh) obeys `soc_new = soc + eta_c * charge * dt - discharge * dt / eta_d`.

# %%
def run_day(pv, load, cap_kwh, p_max_kw, eta, soc0=0.0):
    """One pass over the hours. Returns a dict of hourly arrays (kW, kWh) and the final soc."""
    eta_c = eta_d = np.sqrt(eta)
    n = len(pv)
    soc = soc0
    charge = np.zeros(n); discharge = np.zeros(n); imp = np.zeros(n); exp = np.zeros(n); soc_end = np.zeros(n)
    for i in range(n):
        net = pv[i] - load[i]
        if net >= 0:
            c = min(net, p_max_kw, (cap_kwh - soc) / (eta_c * DT)) if cap_kwh > 0 else 0.0
            c = max(c, 0.0)
            soc += eta_c * c * DT
            charge[i] = c
            exp[i] = net - c
        else:
            need = -net
            d = min(need, p_max_kw, soc * eta_d / DT) if cap_kwh > 0 else 0.0
            d = max(d, 0.0)
            soc -= d * DT / eta_d
            discharge[i] = d
            imp[i] = need - d
        soc_end[i] = soc
    return {"charge": charge, "discharge": discharge, "imp": imp, "exp": exp, "soc": soc_end, "soc_final": soc}


def simulate(peak_kw, daily_kwh, cap_kwh, p_max_kw, eta, sun=1.0, days=3):
    """Repeat the same day `days` times starting empty and report the last day (a steady day)."""
    pv, load = pv_profile(peak_kw, sun), load_profile(daily_kwh)
    soc0 = 0.0
    for _ in range(days):
        r = run_day(pv, load, cap_kwh, p_max_kw, eta, soc0)
        start = soc0
        soc0 = r["soc_final"]
    r.update(pv=pv, load=load, soc_start=start)
    return r


# %% [markdown]
# ## Step 3: the numbers that matter
# * **Self-sufficiency** = 1 - (grid import / demand): the share of demand not taken from the grid.
# * **Energy conservation**: solar + import = demand + export + change in stored energy + battery losses.
# * **Illustrative cost** = 1000 x (array kW) + 400 x (battery kWh) *cost units*.

# %%
def summary(r, daily_kwh=None):
    pv_e, load_e = float(r["pv"].sum() * DT), float(r["load"].sum() * DT)
    imp_e, exp_e = float(r["imp"].sum() * DT), float(r["exp"].sum() * DT)
    return {"pv_kwh": pv_e, "load_kwh": load_e, "import_kwh": imp_e, "export_kwh": exp_e,
            "self_sufficiency": 1 - imp_e / load_e,
            "soc_max": float(r["soc"].max()), "soc_min": float(r["soc"].min())}


def conservation_residual(r, eta):
    """solar + import - (demand + export + delta stored + losses); should be 0 (kWh)."""
    eta_c = eta_d = np.sqrt(eta)
    loss = float((r["charge"] * (1 - eta_c)).sum() * DT + (r["discharge"] / eta_d * (1 - eta_d)).sum() * DT)
    d_store = r["soc_final"] - r["soc_start"]
    lhs = float(r["pv"].sum() * DT + r["imp"].sum() * DT)
    rhs = float(r["load"].sum() * DT + r["exp"].sum() * DT) + d_store + loss
    return lhs - rhs


def cost(peak_kw, cap_kwh):
    return COST_PV * peak_kw + COST_BATT * cap_kwh


# %% [markdown]
# ## Step 4: the design problem
# Find the cheapest (array kW, battery kWh) with self-sufficiency of at least 90 percent on a
# dull day (sun = 0.5, half the clear-day output) for a 10 kWh/day home, battery power limit = capacity / 2 per hour, efficiency 90 %.
# We simply try a grid of sizes and keep the cheapest that passes.

# %%
def cheapest_design(target, daily_kwh=10.0, eta=0.9, sun=0.5, pv_grid=None, cap_grid=None):
    pv_grid = np.arange(1.0, 8.01, 0.5) if pv_grid is None else pv_grid
    cap_grid = np.arange(0.0, 20.01, 1.0) if cap_grid is None else cap_grid
    best = None
    for pk in pv_grid:
        for cap in cap_grid:
            r = simulate(pk, daily_kwh, cap, cap / 2.0, eta, sun)
            ss = summary(r)["self_sufficiency"]
            c = cost(pk, cap)
            if ss >= target and (best is None or c < best[0]):
                best = (c, float(pk), float(cap), float(ss))
    return best


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    pk, cap, daily, eta, sun = 3.0, 6.0, 10.0, 0.9, 0.5
    r = simulate(pk, daily, cap, cap / 2, eta, sun)
    s = summary(r)
    print({k: round(v, 3) for k, v in s.items()}, "residual", round(conservation_residual(r, eta), 12))
    hours = np.arange(24)
    fig, axes = plt.subplots(2, 1, figsize=(8, 6.4), sharex=True)
    axes[0].plot(hours + 0.5, r["pv"], color="tab:orange", lw=2, label="solar")
    axes[0].plot(hours + 0.5, r["load"], color="tab:blue", lw=2, label="demand")
    axes[0].bar(hours + 0.5, r["imp"], width=0.8, color="tab:red", alpha=0.5, label=f"grid import {s['import_kwh']:.1f} kWh")
    axes[0].set_ylabel("power (kW)")
    axes[0].set_title("3 kW array, 6 kWh battery, 10 kWh/day home, dull day")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)
    axes[1].plot(np.r_[0, hours + 1], np.r_[r["soc_start"], r["soc"]], "g-o", ms=3)
    axes[1].set_ylabel("battery state of charge (kWh)")
    axes[1].set_xlabel("time of day (hours)")
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "energy_balance.png", dpi=120)

    pvs = np.arange(1, 8.01, 0.5)
    caps = [0, 3, 6, 12]
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    for c in caps:
        ax2.plot(pvs, [100 * summary(simulate(p, daily, c, c / 2, eta, sun))["self_sufficiency"] for p in pvs], label=f"battery {c} kWh")
    ax2.axhline(90, color="red", ls="--", label="90% target")
    ax2.set_xlabel("array size (kW)")
    ax2.set_ylabel("self-sufficiency (%)")
    ax2.set_title("Self-sufficiency, dull day (sun = 0.5)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "self_sufficiency.png", dpi=120)

    for tgt in (0.6, 0.8, 0.9):
        print("target", tgt, "->", cheapest_design(tgt))
    for p, c in ((2, 0), (3, 0), (3, 6), (6, 6), (6, 12)):
        rr = simulate(p, daily, c, c / 2, eta, sun)
        print(p, c, {k: round(v, 3) for k, v in summary(rr).items()})
    print("import vs eta at 3 kW / 6 kWh:", [round(summary(simulate(3, daily, 6, 3, e, sun))["import_kwh"], 3) for e in (1.0, 0.9, 0.8)])
    print("self-sufficiency with no battery vs 3 kW:", round(summary(simulate(3, daily, 0, 0, eta, sun))["self_sufficiency"], 3))
