"""Session 3 (Level 3): a 365 day simulation, reliability, validation and cost-optimal sizing.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a whole year, reliability and the cheapest design
# **A. Real-world problem.** A design that works on one dull day can still fail in a cloudy
# fortnight in winter. A sizing decision must hold up over a whole year of changing day length,
# clouds and demand. Today you simulate 8760 hours, count the hours when the home still needs
# the grid, check the simulator against exact energy rules, and search for the cheapest design
# that meets a reliability target. Costs are *illustrative units*, not market prices. This is an
# educational model, not an installation design.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
DAYS = 365
HOURS = np.arange(24) + 0.5                       # mid-hour times
COST_PV, COST_BATT = 1000.0, 400.0                # ILLUSTRATIVE cost units per kW and per kWh
LOL_LIMIT_KW = 0.001                              # import above this counts as a loss-of-load hour
DAY_SHAPE = 0.3 + 1.0 * np.exp(-0.5 * ((HOURS - 7.5) / 1.2) ** 2) + 1.6 * np.exp(-0.5 * ((HOURS - 19.0) / 2.0) ** 2)
DAY_SHAPE = DAY_SHAPE / DAY_SHAPE.sum()           # fractions of a day's energy in each hour (sum 1)


# %% [markdown]
# ## Step 1: clear-sky solar for every day of the year
# Day length and peak strength change with the season (a mid-latitude site, illustrative):
#
#     D(d) = 12 + 2.5 sin(2 pi (d - 80) / 365)           hours of daylight on day d
#     A(d) = 0.85 + 0.10 sin(2 pi (d - 80) / 365)        strength of noon sun (fraction of rating)
#     clear(d, t) = A(d) sin(pi (t - sunrise) / D)       per kW of array, between sunrise and sunset
#
# so a clear day gives A(d) x 2 D(d) / pi kWh per kW (the area of a half sine).

# %%
def clear_sky_per_kw(days=DAYS):
    """Array (days, 24): clear-sky output in kW per kW of array, midpoint of each hour."""
    d = np.arange(days)[:, None]
    season = np.sin(2 * np.pi * (d - 80) / 365.0)
    length = 12.0 + 2.5 * season
    strength = 0.85 + 0.10 * season
    sunrise = 12.0 - length / 2.0
    t = HOURS[None, :]
    inside = (t >= sunrise) & (t <= sunrise + length)
    return np.where(inside, strength * np.sin(np.pi * (t - sunrise) / length), 0.0)


def clear_day_energy_per_kw(day):
    """Analytic: kWh per kW on a clear day = A(d) x 2 D(d) / pi."""
    season = math.sin(2 * math.pi * (day - 80) / 365.0)
    return (0.85 + 0.10 * season) * 2 * (12.0 + 2.5 * season) / math.pi


# %% [markdown]
# ## Step 2: clouds as a seeded random model
# Each day gets a *cloud cover* B between 0 and 1. Clouds persist for a few days, so B comes from
# a correlated normal sequence z (z_d = 0.6 z_(d-1) + 0.8 e_d, e_d standard normal) turned into
# a uniform number with the normal distribution function. The day's **clearness**
#
#     K_d = 1 - 0.9 * c * B_d
#
# multiplies the clear-sky output. `c` (0 to 1) is the **cloudiness** setting: c = 0 is cloudless
# and c = 1 averages K = 0.55. The same `seed` always gives the same year.

# %%
def clearness(cloudiness, seed=1, days=DAYS):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(days)
    z = np.zeros(days)
    z[0] = e[0]
    for i in range(1, days):
        z[i] = 0.6 * z[i - 1] + 0.8 * e[i]
    b = np.array([0.5 * (1 + math.erf(v / math.sqrt(2))) for v in z])
    return 1.0 - 0.9 * cloudiness * b


def pv_unit_year(cloudiness, seed=1):
    """Hourly solar per kW of array for the whole year, flattened to 8760 values."""
    return (clear_sky_per_kw() * clearness(cloudiness, seed)[:, None]).ravel()


# %% [markdown]
# ## Step 3: a year of demand
# The user gives the daily energy of each day (from a bill). Hours follow the day shape of
# Session 2. A small seeded day-to-day wobble (about 10 percent) is added.

# %%
def monthly_to_daily(monthly_kwh):
    """12 monthly bills (kWh) -> 365 daily energies (kWh), same average inside each month."""
    lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    out = []
    for kwh, n in zip(monthly_kwh, lengths):
        out += [kwh / n] * n
    return np.array(out)


def default_daily(avg_kwh=10.0):
    d = np.arange(DAYS)
    return avg_kwh * (1 + 0.15 * np.cos(2 * np.pi * (d - 15) / 365.0))   # more use in winter


def load_year(daily_kwh, seed=2, wobble=0.10):
    rng = np.random.default_rng(seed)
    w = np.exp(wobble * rng.standard_normal(len(daily_kwh)) - 0.5 * wobble ** 2)
    return ((np.asarray(daily_kwh) * w)[:, None] * DAY_SHAPE[None, :]).ravel()


# %% [markdown]
# ## Step 4: the battery over 8760 hours (rules from Session 2)
# The battery carries its state of charge from hour to hour with no reset. We count:
# * **unmet energy** = grid import (kWh): what the solar-plus-battery system could not supply
# * **energy reliability** R = 1 - unmet / demand
# * **loss-of-load hours** (LOLH) = hours with import above 0.001 kW

# %%
def simulate_year(pv_kw, load_kw, cap_kwh, p_max_kw, eta, soc0=0.0):
    ec = ed = math.sqrt(eta)
    soc = soc0
    imp = [0.0] * len(load_kw)
    exp = [0.0] * len(load_kw)
    chg = 0.0
    dis = 0.0
    for i in range(len(load_kw)):
        net = pv_kw[i] - load_kw[i]
        if net >= 0.0:
            c = min(net, p_max_kw, (cap_kwh - soc) / ec) if cap_kwh > 0 else 0.0
            if c < 0.0:
                c = 0.0
            soc += ec * c
            chg += c
            exp[i] = net - c
        else:
            need = -net
            d = min(need, p_max_kw, soc * ed) if cap_kwh > 0 else 0.0
            if d < 0.0:
                d = 0.0
            soc -= d / ed
            dis += d
            imp[i] = need - d
    return {"imp": np.array(imp), "exp": np.array(exp), "charged": chg, "discharged": dis, "soc_final": soc, "soc0": soc0}


def metrics(res, pv_kw, load_kw):
    unmet = float(res["imp"].sum())
    demand = float(np.sum(load_kw))
    return {"unmet_kwh": unmet, "demand_kwh": demand, "reliability": 1 - unmet / demand,
            "lolh": int((res["imp"] > LOL_LIMIT_KW).sum()), "pv_kwh": float(np.sum(pv_kw)), "export_kwh": float(res["exp"].sum())}


def reliability_ceiling(pv_kw, load_kw):
    """No battery can create energy: unmet >= demand - solar, so R <= solar / demand (at most 1)."""
    return min(1.0, float(np.sum(pv_kw)) / float(np.sum(load_kw)))


def conservation_residual(res, pv_kw, load_kw, eta):
    """solar + import - (demand + export + change in stored energy + battery losses), kWh."""
    ec = ed = math.sqrt(eta)
    losses = res["charged"] * (1 - ec) + res["discharged"] / ed * (1 - ed)
    lhs = float(np.sum(pv_kw)) + float(res["imp"].sum())
    rhs = float(np.sum(load_kw)) + float(res["exp"].sum()) + (res["soc_final"] - res["soc0"]) + losses
    return lhs - rhs


def evaluate(peak_kw, cap_kwh, pv_unit, load_kw, eta=0.9):
    """Run a design (battery power limit = capacity / 2 per hour) and return metrics."""
    pv = peak_kw * pv_unit
    res = simulate_year(pv, load_kw, cap_kwh, cap_kwh / 2.0, eta)
    m = metrics(res, pv, load_kw)
    m.update(peak_kw=float(peak_kw), cap_kwh=float(cap_kwh), cost=COST_PV * peak_kw + COST_BATT * cap_kwh)
    return m


# %% [markdown]
# ## Step 5: search for the cheapest design that meets a target, and the Pareto front
# We try every (array, battery) pair on a grid. A design is on the **Pareto front** if no other
# design is both cheaper and more reliable.

# %%
PV_GRID = np.arange(0.5, 10.01, 0.5)
CAP_GRID = np.arange(0.0, 24.01, 1.0)


def search(pv_unit, load_kw, eta=0.9, pv_grid=PV_GRID, cap_grid=CAP_GRID):
    return [evaluate(p, c, pv_unit, load_kw, eta) for p in pv_grid for c in cap_grid]


def cheapest(designs, target):
    ok = [d for d in designs if d["reliability"] >= target]
    return min(ok, key=lambda d: d["cost"]) if ok else None


def pareto_front(designs):
    front, best_rel = [], -1.0
    for d in sorted(designs, key=lambda d: (d["cost"], -d["reliability"])):
        if d["reliability"] > best_rel + 1e-12:
            front.append(d)
            best_rel = d["reliability"]
    return front


def size_from_bill(monthly_kwh, target=0.85, cloudiness=0.5, seed=1):
    """Mini-project helper: cheapest design meeting `target` for a household's 12 monthly bills."""
    pv_unit = pv_unit_year(cloudiness, seed)
    load = load_year(monthly_to_daily(monthly_kwh))
    return cheapest(search(pv_unit, load), target)


# %%
if __name__ == "__main__":
    import time

    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    daily = default_daily(10.0)
    load = load_year(daily)
    pv_unit = pv_unit_year(0.5, 1)
    print(f"annual demand {load.sum():.0f} kWh; clear-sky per kW {clear_sky_per_kw().sum():.0f} kWh; with clouds {pv_unit.sum():.0f} kWh; mean K {clearness(0.5, 1).mean():.3f}")
    m = evaluate(4.0, 8.0, pv_unit, load)
    print({k: round(v, 3) for k, v in m.items()})
    res = simulate_year(4.0 * pv_unit, load, 8.0, 4.0, 0.9)
    print("conservation residual (kWh):", conservation_residual(res, 4.0 * pv_unit, load, 0.9))

    designs = search(pv_unit, load)
    front = pareto_front(designs)
    for tgt in (0.8, 0.9, 0.95, 0.99):
        b = cheapest(designs, tgt)
        print("target", tgt, "->", None if b is None else {k: round(v, 3) for k, v in b.items()})
    print("search time", round(time.time() - t0, 1), "s;", len(designs), "designs;", len(front), "on the front")

    # figure 1: a winter week and a summer week
    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharey=True)
    pv = 4.0 * pv_unit
    soc = np.zeros(len(load)); s = 0.0
    ec = ed = math.sqrt(0.9)
    for i in range(len(load)):
        net = pv[i] - load[i]
        if net >= 0:
            s += ec * min(net, 4.0, (8.0 - s) / ec)
        else:
            s -= min(-net, 4.0, s * ed) / ed
        soc[i] = s
    for ax, (name, d0) in zip(axes, [("winter week (from day 0)", 0), ("summer week (from day 170)", 170)]):
        a, b2 = d0 * 24, (d0 + 7) * 24
        h = np.arange(a, b2) / 24.0 - d0
        ax.plot(h, pv[a:b2], color="tab:orange", label="solar")
        ax.plot(h, load[a:b2], color="tab:blue", label="demand")
        ax.fill_between(h, 0, res["imp"][a:b2], color="tab:red", alpha=0.5, label="grid import")
        ax2 = ax.twinx()
        ax2.plot(h, soc[a:b2], color="tab:green", lw=1, label="battery (kWh)")
        ax2.set_ylabel("battery charge (kWh)")
        ax.set_title(name)
        ax.set_ylabel("power (kW)")
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=8, loc="upper right")
    axes[1].set_xlabel("day of the week")
    fig.tight_layout()
    fig.savefig(OUT / "two_weeks.png", dpi=110)

    # figure 2: Pareto cloud
    fig2, ax = plt.subplots(figsize=(6.6, 4.3))
    ax.scatter([d["cost"] for d in designs], [100 * (1 - d["reliability"]) for d in designs], s=10, c="lightgray", label="all designs tried")
    ax.plot([d["cost"] for d in front], [100 * (1 - d["reliability"]) for d in front], "o-", color="tab:green", label="Pareto front")
    for tgt, col in ((0.9, "tab:red"),):
        b = cheapest(designs, tgt)
        ax.plot(b["cost"], 100 * (1 - b["reliability"]), "*", ms=14, color=col, label=f"cheapest with R >= {tgt:.0%}")
    ax.set_xlabel("illustrative cost (cost units)")
    ax.set_ylabel("unmet demand (% of annual use)")
    ax.set_title("Cost versus reliability, one simulated year")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "pareto.png", dpi=120)

    # sensitivity
    print("cloudiness -> reliability of a 4 kW / 8 kWh design:")
    for c in (0.0, 0.25, 0.5, 0.75, 1.0):
        mm = evaluate(4.0, 8.0, pv_unit_year(c, 1), load)
        print("  c", c, "R", round(mm["reliability"], 3), "LOLH", mm["lolh"])
    print("demand scale -> reliability:")
    for sc in (0.7, 1.0, 1.3):
        mm = evaluate(4.0, 8.0, pv_unit, load * sc)
        print("  x", sc, "R", round(mm["reliability"], 3), "LOLH", mm["lolh"])
    print("seed -> reliability:", [round(evaluate(4.0, 8.0, pv_unit_year(0.5, sd), load)["reliability"], 3) for sd in (1, 2, 3, 4, 5)])

    # figure 3: an undersized array cannot be rescued by a bigger battery
    fig3, ax3 = plt.subplots(figsize=(6.4, 4))
    caps = np.arange(0, 41, 4)
    for pk in (1.0, 2.0, 4.0, 8.0):
        ax3.plot(caps, [100 * evaluate(pk, c, pv_unit, load)["reliability"] for c in caps], "o-", ms=3, label=f"array {pk:g} kW")
    ax3.set_xlabel("battery capacity (kWh)")
    ax3.set_ylabel("energy reliability (%)")
    ax3.set_title("More battery helps only until the array runs out")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "battery_vs_array.png", dpi=120)
    for pk in (1.0, 2.0, 4.0, 8.0):
        print("array", pk, [round(100 * evaluate(pk, c, pv_unit, load)["reliability"], 1) for c in (0, 8, 16, 40)])
    for pk in (1.0, 2.0):
        print("ceiling R <= solar/demand for", pk, "kW:", round(reliability_ceiling(pk * pv_unit, load), 3))

    bill = [320, 290, 280, 270, 300, 340, 360, 350, 310, 280, 290, 320]
    print("mini-project example", sum(bill), "kWh/yr:", {k: round(v, 3) for k, v in size_from_bill(bill, 0.85).items()})
    print("total time", round(time.time() - t0, 1), "s")
