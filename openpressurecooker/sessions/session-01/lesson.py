"""Session 1 (Level 1): pressure raises the boiling point, so a cooker cooks faster.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: why a pressure cooker cooks faster
# **A. Real-world problem.** Lentils take about 40 minutes in an open pot and about 10 minutes
# in a pressure cooker. The cooker does not have a stronger flame. What does the lid change?
#
# **Safety and scope.** This is a simplified teaching model, not a design tool. Never modify,
# block or remove the valves of real equipment; they are safety devices.
#
# **Plan.** (1) boiling point depends on pressure, (2) a cooker traps steam so pressure rises,
# (3) a hotter pot cooks faster, (4) draw it.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

P_ATM = 101.325   # standard atmosphere, kPa

# Approximate steam-table values: pressure (kPa, absolute) and boiling point (degrees C).
TABLE_P = np.array([50.0, 101.325, 200.0, 300.0, 400.0])
TABLE_T = np.array([81.3, 100.0, 120.2, 133.5, 143.6])


# %% [markdown]
# ## Step 1: boiling point from a table
# Water boils when its vapour pressure equals the pressure around it. At sea level that is
# 101.3 kPa and the boiling point is 100 degrees C. Higher pressure needs a higher temperature
# before bubbles can form. We read a small table of well-known (approximate) values and fill
# in the gaps by drawing straight lines between them (on a log-pressure scale).

# %%
def boiling_point(p_abs_kpa):
    """Boiling point in degrees C for an ABSOLUTE pressure between 50 and 400 kPa."""
    if not (TABLE_P[0] <= p_abs_kpa <= TABLE_P[-1]):
        raise ValueError("pressure outside the table (50 to 400 kPa absolute)")
    return float(np.interp(np.log(p_abs_kpa), np.log(TABLE_P), TABLE_T))


def gauge_to_abs(p_gauge_kpa):
    """A pressure gauge reads the excess over the air: absolute = gauge + atmosphere."""
    return p_gauge_kpa + P_ATM


# %% [markdown]
# ## Step 2: a cooker traps the steam
# In an open pot steam escapes, so the pressure stays at one atmosphere (gauge 0). In a cooker
# the lid seals, the steam collects, and a weighted valve lets out just enough to hold the
# pressure at a set value, for example 100 kPa above the air (gauge). Absolute pressure is then
# about 201 kPa, and the water can reach about 120 degrees C before it boils.

# %% [markdown]
# ## Step 3: hotter food cooks faster
# Cooking is chemistry (softening, breaking down), and chemistry speeds up with temperature.
# A common rule of thumb: the rate roughly doubles for every 10 degrees C. It is only a rule
# of thumb, but it gives the right idea.

# %%
def speed_factor(temp_c):
    """How many times faster than 100 degrees C (rule of thumb: doubles every 10 degrees C)."""
    return 2.0 ** ((temp_c - 100.0) / 10.0)


def cooking_time(open_pot_minutes, p_gauge_kpa):
    """Estimated time in a cooker held at gauge pressure p_gauge_kpa."""
    t = boiling_point(gauge_to_abs(p_gauge_kpa))
    return open_pot_minutes / speed_factor(t)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    pg = np.linspace(-50.0, 300.0, 200)
    pa = gauge_to_abs(pg)
    ok = (pa >= 50.0) & (pa <= 400.0)
    temps = np.array([boiling_point(x) for x in pa[ok]])

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(pa[ok], temps, "-", label="straight lines between table points")
    ax.plot(TABLE_P, TABLE_T, "o", label="approximate steam-table values")
    ax.plot([P_ATM], [100.0], "s", color="red", label="open pot: 101.3 kPa, 100 C")
    ax.set_xlabel("absolute pressure (kPa)")
    ax.set_ylabel("boiling point of water (degrees C)")
    ax.set_title("Higher pressure, higher boiling point")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "boiling_vs_pressure.png", dpi=120)

    gauges = [0, 50, 100, 150]
    times = [cooking_time(40.0, g) for g in gauges]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar([f"{g} kPa" for g in gauges], times, color=["#999999", "#6aa", "#2a9d8f", "#1b6f66"])
    for i, t in enumerate(times):
        ax2.text(i, t + 0.5, f"{t:.1f} min", ha="center", fontsize=9)
    ax2.set_xlabel("cooker gauge pressure (0 = open pot)")
    ax2.set_ylabel("lentil cooking time (minutes)")
    ax2.set_title("Estimated time if an open pot needs 40 min")
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "cooking_time.png", dpi=120)

    for g in gauges:
        t = boiling_point(gauge_to_abs(g))
        print(f"gauge {g:3d} kPa  absolute {gauge_to_abs(g):6.1f} kPa  boils at {t:6.1f} C  "
              f"speed x{speed_factor(t):.2f}  lentils {cooking_time(40.0, g):5.1f} min")

# %% [markdown]
# ## Where this stops
# The table and the doubling rule are rough. Session 2 derives the boiling-point curve from
# physics, and Session 3 simulates a whole cooker heating up. Never experiment with the valves
# of a real cooker; use the model instead.
