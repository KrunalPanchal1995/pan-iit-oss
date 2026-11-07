"""Session 3 (Level 3): a month of random usage with rooftop solar and net metering.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: simulate a month, add the sun, check against hand calculation
# **A. Real-world problem.** Will a small rooftop solar system cut a household's bill, and how
# sure can we be when weather and habits vary day to day? We simulate 30 days with random
# usage and cloud cover, subtract the solar power hour by hour, and bill the *net* energy
# (net metering). Then we check the model against a hand calculation and test its sensitivity.
#
# *Illustrative tariff and simplified solar model; not a quotation or design for any installation.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

H = np.arange(24)
SLABS = [(100.0, 3.0), (100.0, 5.0), (None, 7.5)]   # Rs per kWh, ILLUSTRATIVE
FIXED = 50.0
DAYS = 30
DERATE = 0.6      # losses: panel temperature, wiring, inverter, dust (illustrative)


# %% [markdown]
# ## Step 1: one day of load, one day of sun
# Load: the Session 2 household (fridge, fans, lights, TV, heater at 6:00 for `dur` hours).
# Solar: a half sine between 6:00 and 18:00, peak power = kWp x DERATE:
#
#     gen(t) = kWp x DERATE x sin(pi (t - 6) / 12)   for 6 <= t <= 18, else 0
#
# We evaluate it at the middle of each hour. Hand check of the daily energy: the sum of
# sin over 12 midpoints is 1 / sin(pi/24) = 7.661, close to the exact area 24/pi = 7.639.

# %%
def heater_hours_on(hour, start, dur):
    t = 0.0
    for shift in (0.0, -24.0):
        t += max(0.0, min(hour + 1, start + dur + shift) - max(hour, start + shift))
    return t


def load_day(dur=2.0, habit=1.0):
    """kW per hour. `habit` scales fans, lights and TV."""
    fans = np.where((H >= 11) & (H <= 18), 0.21, 0.0)
    lights = np.where((H >= 18) & (H <= 22), 0.06, 0.0)
    tv = np.where((H >= 19) & (H <= 22), 0.10, 0.0)
    heater = np.array([1.5 * heater_hours_on(h, 6.0, dur) for h in H])
    return 0.12 + habit * (fans + lights + tv) + heater


def solar_day(kwp, cloud=1.0):
    """kW per hour from a rooftop array of `kwp` kW peak; cloud in [0, 1] scales it."""
    t = H + 0.5
    s = np.where((t > 6) & (t < 18), np.sin(np.pi * (t - 6) / 12), 0.0)
    return kwp * DERATE * cloud * s


# %% [markdown]
# ## Step 2: bill with net metering
# Each hour the home *imports* max(load - gen, 0) and *exports* max(gen - load, 0). Under net
# metering the month is billed on imports minus exports, never below zero (extra credit is
# carried forward, not paid out, in this model). Without net metering you pay for all imports.

# %%
def slab_bill(kwh, rate_mult=1.0):
    bill, left = FIXED, max(kwh, 0.0)
    for size, rate in SLABS:
        used = left if size is None else min(left, size)
        bill += used * rate * rate_mult
        left -= used
    return bill


def simulate_month(seed=0, kwp=1.0, dur=2.0, usage=1.0, rate_mult=1.0, random=True):
    """Returns a dict of monthly results. random=False gives the average, cloud-free-noise case."""
    rng = np.random.default_rng(seed)
    imp = exp = load_t = gen_t = 0.0
    for _ in range(DAYS):
        if random:
            u_heat = rng.uniform(0.5, 1.5)               # heater time varies by +-50 %
            u_hab = rng.uniform(0.8, 1.2)                # other habits vary by +-20 %
            cloud = float(np.clip(rng.normal(0.85, 0.12), 0.3, 1.0))
        else:
            u_heat, u_hab, cloud = 1.0, 1.0, 0.85
        load = load_day(dur * u_heat * usage, usage * u_hab)
        gen = solar_day(kwp, cloud)
        imp += np.maximum(load - gen, 0).sum()
        exp += np.maximum(gen - load, 0).sum()
        load_t += load.sum()
        gen_t += gen.sum()
    net = imp - exp
    return {
        "load": load_t, "gen": gen_t, "import": imp, "export": exp, "net": net,
        "bill_net": slab_bill(net, rate_mult),                 # net metering
        "bill_no_credit": slab_bill(imp, rate_mult),           # exports earn nothing
        "bill_no_solar": slab_bill(load_t, rate_mult),
        "self_use": 1 - exp / gen_t if gen_t > 0 else 1.0,
    }


# %% [markdown]
# ## Step 3: sensitivity and spread
# Run many random months (different seeds) to see the spread of the bill, and sweep one input
# at a time (panel size, tariff, usage) to see which matters most.

# %%
def bill_spread(n=200, **kw):
    bills = np.array([simulate_month(s, **kw)["bill_net"] for s in range(n)])
    return float(bills.mean()), float(bills.std())


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    base = simulate_month(random=False, kwp=0.0)
    sol = simulate_month(random=False, kwp=1.0)
    print(f"no solar: load {base['load']:.1f} kWh, bill Rs {base['bill_net']:.1f}")
    print(f"1 kWp, average weather: gen {sol['gen']:.1f}, import {sol['import']:.1f}, export {sol['export']:.1f}, "
          f"net {sol['net']:.1f} kWh, bill Rs {sol['bill_net']:.1f} (no credit: Rs {sol['bill_no_credit']:.1f})")
    m, s = bill_spread(kwp=1.0)
    print(f"random months, 1 kWp: mean bill Rs {m:.1f}, std Rs {s:.1f}")
    print("hand check gen per day per kWp:", f"{DERATE * 7.6613:.4f}", "vs simulation:", f"{solar_day(1.0).sum():.4f}")

    ks = np.arange(0, 3.01, 0.25)
    fig, ax = plt.subplots(figsize=(7, 4))
    for mult in (0.8, 1.0, 1.2):
        ax.plot(ks, [simulate_month(random=False, kwp=k, rate_mult=mult)["bill_net"] for k in ks], "o-", ms=3, label=f"tariff x{mult}")
    ax.set_xlabel("rooftop array size (kWp)")
    ax.set_ylabel("monthly bill (Rs, illustrative tariff)")
    ax.set_title("Bill versus solar size (average weather, net metering)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "bill_vs_solar.png", dpi=120)

    bills = [simulate_month(s, kwp=1.0)["bill_net"] for s in range(300)]
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.hist(bills, bins=25, color="#2a9d8f")
    ax2.axvline(sol["bill_net"], color="red", ls="--", label=f"average-weather month Rs {sol['bill_net']:.0f}")
    ax2.set_xlabel("monthly bill (Rs)")
    ax2.set_ylabel("number of simulated months")
    ax2.set_title("300 random months, 1 kWp")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "bill_spread.png", dpi=120)

    load, gen = load_day(), solar_day(1.0, 0.85)
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.step(np.r_[H, 24], np.r_[load, load[-1]], where="post", label="load")
    ax3.fill_between(np.r_[H, 24], np.r_[gen, 0], step="post", alpha=0.4, color="#e9c46a", label="solar")
    ax3.set_xlabel("hour of day (h)")
    ax3.set_ylabel("power (kW)")
    ax3.set_title("One day: load and 1 kWp solar (85% sky)")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "day_load_solar.png", dpi=120)
