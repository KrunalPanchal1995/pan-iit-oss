"""Session 2 (Level 2): the 24-hour load profile, slab tariff, peak demand and power factor.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: a day of load, and a bill with slabs
# **A. Real-world problem.** Two homes can use the same kWh and still stress the wires
# differently: one runs everything at once, the other spreads the load. And a bill is rarely
# "kWh x one rate": the price per unit steps up as you use more (slabs). Can you cut a bill by
# 20 percent, and how much usage must go?
#
# *The tariff below is an ILLUSTRATIVE teaching tariff, not any real utility's. Educational
# model, not an electrical design tool.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

HOURS = np.arange(24)
HEATER_KW = 1.5
SLABS = [(100.0, 3.0), (100.0, 5.0), (None, 7.5)]   # (slab size in kWh, Rs per kWh); None = the rest
FIXED = 50.0                                        # Rs per month, illustrative
DAYS = 30
VOLTS = 230.0


# %% [markdown]
# ## Step 1: when each appliance is on
# Each appliance has power (kW) and the hours it runs. The profile is the sum over appliances
# of power in each hour. One hour at P kW is P kWh, so daily energy = sum of the 24 values.
# The heater runs from `start` for `dur` hours; the overlap of the heater interval with each
# hour tells us the fraction of that hour it is on.

# %%
def overlap(hour, start, dur):
    """Hours of [hour, hour+1) that fall inside the interval [start, start+dur), wrapping at 24."""
    total = 0.0
    for shift in (0.0, -24.0):
        lo = max(hour, start + shift)
        hi = min(hour + 1, start + dur + shift)
        total += max(0.0, hi - lo)
    return total


def appliance_profiles(start=6.0, dur=2.0, scale=1.0, heater_kw=HEATER_KW):
    """kW in each hour for each appliance. `scale` multiplies fans, lights and TV."""
    h = HOURS
    return {
        "Fridge": np.full(24, 0.12),
        "Fans": np.where((h >= 11) & (h <= 18), 0.21, 0.0) * scale,
        "Lights": np.where((h >= 18) & (h <= 22), 0.06, 0.0) * scale,
        "TV": np.where((h >= 19) & (h <= 22), 0.10, 0.0) * scale,
        "Heater": np.array([heater_kw * overlap(x, start, dur) for x in h]),
    }


def load_profile(start=6.0, dur=2.0, scale=1.0, heater_kw=HEATER_KW):
    return sum(appliance_profiles(start, dur, scale, heater_kw).values())


def daily_kwh(profile):
    return float(np.sum(profile) * 1.0)   # 1 hour per entry


# %% [markdown]
# ## Step 2: slab bill, peak, power factor
# Bill = fixed charge + sum over slabs (kWh in the slab x its rate). Peak demand is the
# largest hourly load. For alternating current, real power P (kW) relates to apparent power
# S (kVA) by the power factor pf = P / S, and the current is I = P / (V x pf).

# %%
def slab_bill(kwh, slabs=SLABS, fixed=FIXED, rate_mult=1.0):
    if kwh < 0:
        raise ValueError("energy cannot be negative")
    bill, left = fixed, kwh
    for size, rate in slabs:
        used = left if size is None else min(left, size)
        bill += used * rate * rate_mult
        left -= used
    return float(bill)


def peak_kw(profile):
    return float(np.max(profile))


def apparent_kva(kw, pf):
    return kw / pf


def current_amps(kw, pf, volts=VOLTS):
    return kw * 1000.0 / (volts * pf)


def monthly_bill(profile, days=DAYS):
    return slab_bill(daily_kwh(profile) * days)


# %% [markdown]
# ## Step 3: the design problem, cut the bill by 20 percent
# Find the heater time that gives 80 percent of today's bill. The bill rises with usage, so
# bisection (halve the search interval until it fits) works.

# %%
def heater_hours_for_bill(target_bill, start=6.0, scale=1.0, hi=4.0):
    f = lambda d: monthly_bill(load_profile(start, d, scale)) - target_bill
    lo = 0.0
    if f(lo) > 0:
        return None            # impossible even with the heater off
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return 0.5 * (lo + hi)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    prof = appliance_profiles()
    total = load_profile()
    month = daily_kwh(total) * DAYS
    base = monthly_bill(total)
    print(f"daily {daily_kwh(total):.2f} kWh, month {month:.1f} kWh, bill Rs {base:.1f}")
    pk = peak_kw(total)
    print(f"peak {pk:.2f} kW, at pf 0.9: {apparent_kva(pk, 0.9):.2f} kVA, {current_amps(pk, 0.9):.2f} A")
    d = heater_hours_for_bill(0.8 * base)
    new = load_profile(6.0, d)
    print(f"heater time for -20% bill: {d:.3f} h  (bill Rs {monthly_bill(new):.1f}, target {0.8 * base:.1f})")
    print(f"energy cut needed: {100 * (1 - daily_kwh(new) / daily_kwh(total)):.1f} %")

    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.stackplot(np.r_[HOURS, 24], *[np.r_[v, v[-1]] for v in prof.values()], labels=list(prof.keys()), step="post")
    ax.set_xlabel("hour of day (h)")
    ax.set_ylabel("power (kW)")
    ax.set_title("24-hour load profile, stacked by appliance")
    ax.set_xlim(0, 24)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "load_profile.png", dpi=120)

    kwh = np.linspace(0, 400, 401)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.plot(kwh, [slab_bill(k) for k in kwh])
    ax2.plot([month], [base], "o", color="red", label=f"this home: {month:.0f} kWh, Rs {base:.0f}")
    ax2.axhline(0.8 * base, color="gray", ls="--", label="20% cut target")
    ax2.set_xlabel("energy per month (kWh)")
    ax2.set_ylabel("monthly bill (Rs, illustrative tariff)")
    ax2.set_title("Slab tariff: the slope steps up")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "slab_bill.png", dpi=120)
