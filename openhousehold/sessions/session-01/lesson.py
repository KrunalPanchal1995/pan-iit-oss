"""Session 1 (Level 1): power x time = energy, and energy x rate = cost.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: power times time is energy
# **A. Real-world problem.** Your electricity bill does not charge for *power* (how hard an
# appliance works at a moment). It charges for *energy* (how much work it did in total).
# A 1500 W heater that runs for 2 hours uses more than a 100 W TV that runs for 4 hours.
# Today you compute energy and cost for a small household, by hand and in Python.
#
# *Education only: simplified model, not advice for wiring or buying appliances.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# name, power in watts (W), hours switched on per day (h)
APPLIANCES = [
    ("Ceiling fans (3)", 210.0, 8.0),
    ("LED lights", 60.0, 5.0),
    ("Fridge (average)", 120.0, 24.0),
    ("TV", 100.0, 4.0),
    ("Water heater", 1500.0, 2.0),
]
RATE = 6.0   # Rs per kWh: a flat, ILLUSTRATIVE rate for Session 1 (not any real utility)


# %% [markdown]
# ## Step 1: energy = power x time
# Power is measured in watts (W) or kilowatts (kW, 1 kW = 1000 W). Energy is power times the
# time it is used. With power in kW and time in hours the answer is in **kilowatt-hours
# (kWh)**: the "unit" on your bill.
#
#     energy (kWh) = power (kW) x time (h)
#
# Check by hand: a 1.5 kW heater for 2 hours is 1.5 x 2 = 3 kWh. Half the time: 1.5 kWh.

# %%
def energy_kwh(power_w, hours):
    """Energy in kWh from power in watts and time in hours."""
    if np.any(np.asarray(power_w) < 0) or np.any(np.asarray(hours) < 0):
        raise ValueError("power and hours must be zero or positive")
    return power_w / 1000.0 * hours


def daily_energies(appliances=APPLIANCES):
    """Dictionary name -> kWh per day."""
    return {name: energy_kwh(w, h) for name, w, h in appliances}


# %% [markdown]
# ## Step 2: add up the household, then price it
# Energies add (powers at different times do not simply add: that is Session 2).
#
#     cost (Rs) = energy (kWh) x rate (Rs per kWh)

# %%
def total_energy(appliances=APPLIANCES):
    return float(sum(daily_energies(appliances).values()))


def cost(kwh, rate=RATE):
    return kwh * rate


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    e = daily_energies()
    total = total_energy()
    for name, v in e.items():
        print(f"{name:18s} {v:5.2f} kWh/day")
    print(f"total {total:.2f} kWh/day, cost Rs {cost(total):.2f} per day at Rs {RATE}/kWh")
    print("heater 1.5 kW for 2 h:", energy_kwh(1500, 2), "kWh; for 1 h:", energy_kwh(1500, 1), "kWh")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(list(e.keys()), list(e.values()), color="#2a9d8f")
    for i, v in enumerate(e.values()):
        ax.text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=9)
    ax.set_xlabel("energy per day (kWh)")
    ax.set_title(f"Where the day's {total:.2f} kWh goes")
    ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(OUT / "daily_energy_bars.png", dpi=120)

    t = np.linspace(0, 4, 50)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(t, energy_kwh(1500, t), label="1500 W heater")
    ax2.plot(t, energy_kwh(750, t), "--", label="750 W heater")
    ax2.plot([2, 1], [3.0, 1.5], "o", color="red")
    ax2.annotate("2 h: 3 kWh", (2, 3.0), textcoords="offset points", xytext=(6, 4))
    ax2.annotate("1 h: 1.5 kWh", (1, 1.5), textcoords="offset points", xytext=(6, 4))
    ax2.set_xlabel("time switched on (h)")
    ax2.set_ylabel("energy used (kWh)")
    ax2.set_title("Energy grows in a straight line with time")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "heater_energy_vs_time.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real bills use slabs, and power changes hour by hour. Session 2 adds the 24-hour profile.
