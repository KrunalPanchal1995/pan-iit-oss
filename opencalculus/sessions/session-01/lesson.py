"""Session 1 (Level 1): slope of a distance-time graph is speed; area under a speed-time graph is distance.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: slope is speed, area is distance
# **A. Real-world problem.** A car's speedometer tells you how fast you go, but not how far you
# have come. Its odometer tells you how far, but not how fast. Can one graph give you the other?
#
# **Plan.** (1) describe a car by its speed at a few moments, (2) turn that into distance by
# adding up areas, (3) turn distance back into speed by measuring slopes, (4) draw both graphs.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# The car starts at rest (or, in the second example, already moving at a starting speed v0).
# Its speed (m/s) is known at t = 0, 2, 4, 6 seconds and is a straight line between those moments.
KNOT_T = np.array([0.0, 2.0, 4.0, 6.0])


def knot_speeds(a, b, c, v0=0.0):
    """Speeds at the four moments: v0 at the start (0 = starts at rest), then a, b, c (m/s)."""
    return np.array([v0, a, b, c], dtype=float)


# %% [markdown]
# ## Step 1: speed at any moment
# Between two known moments the speed changes in a straight line. `np.interp` does exactly that.

# %%
def speed(t, v_knots):
    """Speed (m/s) at time t (s), straight lines between the knots."""
    return np.interp(t, KNOT_T, v_knots)


# %% [markdown]
# ## Step 2: distance = area under the speed graph
# Each slice between two knots is a trapezoid: width (seconds) times the average of its two
# parallel sides (m/s). Width * height has the unit s * m/s = m, a distance.
# For a car at a steady 10 m/s for 2 s: area = 2 * 10 = 20 m.
# A car that starts already moving has more area from the first slice: v0 = 8 m/s rising to
# 10 m/s in the first 2 s covers 2 * (8 + 10) / 2 = 18 m, where a car from rest covers 10 m.

# %%
def distance_at_knots(v_knots):
    """Total distance (m) at each knot: running sum of trapezoid areas."""
    widths = np.diff(KNOT_T)
    avg = (v_knots[:-1] + v_knots[1:]) / 2
    return np.concatenate([[0.0], np.cumsum(widths * avg)])


def distance(t, v_knots):
    """Distance travelled (m) up to time t (s): whole slices plus a part of one slice."""
    t = np.asarray(t, dtype=float)
    dists = distance_at_knots(v_knots)
    k = np.clip(np.searchsorted(KNOT_T, t, side="right") - 1, 0, len(KNOT_T) - 2)
    dt = t - KNOT_T[k]
    v0 = v_knots[k]
    slope = (v_knots[k + 1] - v_knots[k]) / (KNOT_T[k + 1] - KNOT_T[k])
    return dists[k] + v0 * dt + 0.5 * slope * dt ** 2


# %% [markdown]
# ## Step 3: speed = slope of the distance graph
# The slope of a graph is "rise over run". On the distance graph the rise is metres and the run
# is seconds, so the slope is m/s, a speed. We estimate it from two close moments.

# %%
def slope_of_distance(t, v_knots, h=1e-4):
    """Slope (m/s) of the distance graph at time t, from two moments 2h apart."""
    return float((distance(t + h, v_knots) - distance(t - h, v_knots)) / (2 * h))


# %% [markdown]
# ## Step 4: see it
# Left: speed against time, with the area up to t = 4 s shaded. Right: distance against time;
# the tangent line there has slope equal to the speed.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    v = knot_speeds(10.0, 14.0, 6.0)
    t = np.linspace(0, 6, 241)
    t0 = 4.0
    print("speeds at knots (m/s):", v)
    print("distance at knots (m):", distance_at_knots(v))
    print(f"distance at t = {t0} s: {float(distance(t0, v)):.2f} m")
    print(f"speed at t = {t0} s: {float(speed(t0, v)):.2f} m/s; slope of the distance graph there: {slope_of_distance(t0, v):.2f} m/s")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(t, speed(t, v), color="#1f77b4")
    tt = np.linspace(0, t0, 100)
    ax.fill_between(tt, speed(tt, v), alpha=0.3, label=f"area = {float(distance(t0, v)):.0f} m")
    ax.plot(KNOT_T, v, "o", color="#1f77b4")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("speed (m/s)")
    ax.set_title("Area under the speed graph is distance")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "speed_area.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(t, distance(t, v), color="#d62728", label="distance")
    sl = slope_of_distance(t0, v)
    d0 = float(distance(t0, v))
    ax2.plot([t0 - 1.5, t0 + 1.5], [d0 - 1.5 * sl, d0 + 1.5 * sl], "k--", label=f"tangent, slope {sl:.0f} m/s")
    ax2.plot([t0], [d0], "ko")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("distance (m)")
    ax2.set_title("Slope of the distance graph is speed")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "distance_slope.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
