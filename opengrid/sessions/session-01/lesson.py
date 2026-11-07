"""Session 1 (Level 1): supply must equal demand every second.

Run:  python start.py 1
Educational toy model only. It is not a tool for operating or planning a real grid.
"""
# %% [markdown]
# # Session 1: supply must equal demand, every second
# **A. Real-world problem.** Electricity cannot be stored in the wires. The power that
# generators push in must match the power that homes and factories draw out, second by second.
# If demand is higher than supply, the whole grid slows down a little and the frequency
# (50 Hz in India and Europe) sags. Grid operators watch that one number all day.
#
# **Plan.** (1) a demand curve through a day, (2) a small fleet of generators that ramp up and
# down, (3) the balance bar: supply minus demand, (4) how the imbalance moves the frequency.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

F0 = 50.0        # nominal grid frequency (Hz)
BASE = 1000.0    # size of our toy grid (MW)
STIFF = 21.0     # grid stiffness 1/R + D in per unit (droop R = 0.05 gives 20, damping D = 1 gives 1)


# %% [markdown]
# ## Step 1: a day of demand
# People wake up (morning bump), cook and light their homes (evening peak), and sleep (night
# dip). Our toy curve is a base level plus two smooth bumps, in megawatts (MW).

# %%
def demand_curve(hour):
    """Toy demand in MW at a time of day in hours (0 to 24)."""
    h = np.asarray(hour, dtype=float)
    morning = 150.0 * np.exp(-(((h - 8.0) / 2.5) ** 2))
    evening = 250.0 * np.exp(-(((h - 19.5) / 2.5) ** 2))
    return 500.0 + morning + evening


# %% [markdown]
# ## Step 2: generators that ramp
# Each unit has a size (MW) and a ramp rate (MW it can add or remove per hour). A nuclear or coal
# unit is cheap but slow; hydro and gas can follow demand quickly. We load units in merit order
# (cheapest first), but a unit can only move as fast as its ramp rate allows.

# %%
FLEET = [("nuclear", 400.0, 20.0), ("coal", 300.0, 60.0), ("gas", 300.0, 70.0), ("hydro", 200.0, 80.0)]


def dispatch(demand_now, previous, ramp_scale=1.0):
    """Choose each unit's output for the next hour.

    Step A: ask the units in merit order to cover demand. Step B: clip every unit to its ramp
    limit. Step C: let the fastest units (last in the list) take up any leftover difference
    inside their remaining ramp room. Returns (outputs array, supply MW).
    """
    prev = np.asarray(previous, dtype=float)
    cap = np.array([u[1] for u in FLEET])
    ramp = ramp_scale * np.array([u[2] for u in FLEET])
    want = np.zeros(len(FLEET))
    left = demand_now
    for i in range(len(FLEET)):
        want[i] = min(cap[i], max(left, 0.0))
        left -= want[i]
    out = np.clip(want, np.maximum(prev - ramp, 0.0), np.minimum(prev + ramp, cap))
    for i in reversed(range(len(FLEET))):
        gap = demand_now - out.sum()
        out[i] = np.clip(out[i] + gap, max(prev[i] - ramp[i], 0.0), min(prev[i] + ramp[i], cap[i]))
    return out, float(out.sum())


def run_day(step_hours=1.0, ramp_scale=1.0):
    """Dispatch through 24 hours. Returns hours, demand, supply, unit outputs (MW)."""
    hours = np.arange(0.0, 24.0 + 1e-9, step_hours)
    dem = demand_curve(hours)
    out = np.zeros((len(hours), len(FLEET)))
    out[0] = dispatch(dem[0], np.array([0.0, 0.0, 0.0, 0.0]), 1.0)[0]
    # start from a settled morning: run the first hour a few times so ramp limits do not bite
    for _ in range(40):
        out[0] = dispatch(dem[0], out[0], 1.0)[0]
    for k in range(1, len(hours)):
        out[k] = dispatch(dem[k], out[k - 1], ramp_scale)[0]
    return hours, dem, out.sum(axis=1), out


# %% [markdown]
# ## Step 3: balance and frequency
# The imbalance is supply minus demand. The whole grid behaves like a heavy flywheel: when
# supply is short it slows, when supply exceeds demand it speeds up. In Session 3 we derive this; for
# now we use its steady-state result: frequency change = f0 * imbalance / (BASE * STIFF).

# %%
def imbalance(supply, demand):
    """Supply minus demand (MW). Positive: too much power."""
    return supply - demand


def grid_frequency(supply, demand):
    """Toy steady frequency (Hz) for a given supply and demand (MW)."""
    return F0 * (1.0 + (supply - demand) / (BASE * STIFF))


# %% [markdown]
# ## Step 4: see it
# Top panel: the units stacked under the demand curve through the day.
# Bottom panel: the frequency, once for normal ramp rates and once for ramp rates cut to a quarter.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    hrs, dem, sup, units = run_day()
    freq = grid_frequency(sup, dem)
    _, dem2, sup2, _ = run_day(ramp_scale=0.25)
    print(f"with ramp rates cut to a quarter: largest gap {np.abs(sup2 - dem2).max():.1f} MW, "
          f"lowest frequency {grid_frequency(sup2, dem2).min():.3f} Hz")
    print(f"peak demand {dem.max():.0f} MW at hour {hrs[dem.argmax()]:.0f}; "
          f"minimum {dem.min():.0f} MW at hour {hrs[dem.argmin()]:.0f}")
    print(f"largest supply gap {np.abs(sup - dem).max():.1f} MW, lowest frequency {freq.min():.3f} Hz")

    fig, ax = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax[0].stackplot(hrs, units.T, labels=[u[0] for u in FLEET], alpha=0.7)
    ax[0].plot(hrs, dem, "k--", lw=2, label="demand")
    ax[0].set_ylabel("power (MW)")
    ax[0].set_title("Units follow the demand curve")
    ax[0].legend(loc="upper left", fontsize=8, ncol=3)
    ax[0].grid(alpha=0.3)
    ax[1].plot(hrs, freq, color="tab:red", label="normal ramp rates")
    ax[1].plot(hrs, grid_frequency(sup2, dem2), color="tab:blue", ls="--", label="ramp rates cut to a quarter")
    ax[1].legend(fontsize=8)
    ax[1].axhline(F0, color="gray", ls=":")
    ax[1].set_xlabel("time of day (hours)")
    ax[1].set_ylabel("frequency (Hz)")
    ax[1].set_title("Slow units let the frequency sag")
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "day_dispatch.png", dpi=120)

    d = np.linspace(-300, 300, 61)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(d, grid_frequency(BASE + d, BASE))
    ax2.axhline(F0, color="gray", ls=":")
    ax2.axvline(0, color="gray", ls=":")
    ax2.set_xlabel("supply minus demand (MW)")
    ax2.set_ylabel("steady frequency (Hz)")
    ax2.set_title("Frequency sags when demand exceeds supply")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "freq_vs_imbalance.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Change the ramp rates in `FLEET` and see when the frequency starts to sag. Then answer the
# four questions in the README (section F) and run the checkpoint.
