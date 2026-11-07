"""Session 1 (Level 1): a car with adjustable acceleration and its three graphs.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: position, velocity and acceleration are one story
# **A. Real-world problem.** A car pulls away from a junction, cruises, then brakes. Your phone
# or a speed camera records where it is at each moment. From that one record we want to know how
# fast it was going and whether it was speeding up or slowing down.
#
# **Plan.** (1) write the three quantities for constant acceleration, (2) measure the slope of
# the position graph and compare it with velocity, (3) measure the area under the velocity graph
# and compare it with the distance moved, (4) draw the three linked graphs.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the three quantities
# * position x (metres): where the car is on the road,
# * velocity v (metres per second): how fast x changes, and in which direction,
# * acceleration a (metres per second squared): how fast v changes.
#
# For a constant acceleration a, starting at x0 with velocity v0 at time t = 0:
#
#     a(t) = a        v(t) = v0 + a t        x(t) = x0 + v0 t + (1/2) a t^2
#
# Check by hand with x0 = 0, v0 = 4 m/s, a = 2 m/s^2 at t = 5 s:
# v = 4 + 2*5 = 14 m/s and x = 4*5 + 0.5*2*25 = 45 m.

# %%
def position(t, x0=0.0, v0=0.0, a=0.0):
    t = np.asarray(t, dtype=float)
    return x0 + v0 * t + 0.5 * a * t ** 2


def velocity(t, v0=0.0, a=0.0):
    t = np.asarray(t, dtype=float)
    return v0 + a * t


def acceleration(t, a=0.0):
    t = np.asarray(t, dtype=float)
    return a + 0.0 * t


# %% [markdown]
# ## Step 2: slope and area
# The slope of a graph is "rise over run". For the x-t graph the rise is a change in position
# and the run is a change in time, so the slope is a velocity. Likewise the slope of the v-t
# graph is an acceleration. Going the other way, the area under the v-t graph is
# (velocity) times (time) = a distance, and the area under the a-t graph is a change of velocity.

# %%
def slope(f, t, h=1e-3):
    """Slope of the graph of f at time t, from two points a tiny step h either side."""
    return float((f(t + h) - f(t - h)) / (2 * h))


def area(f, t0, t1, n=2000):
    """Area under the graph of f between t0 and t1 (trapezoid rule). Area below the axis counts negative."""
    t = np.linspace(t0, t1, n + 1)
    y = np.asarray(f(t), dtype=float)
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(t)))


def stop_time(v0, a):
    """Time when the velocity becomes zero (needs a != 0 and v0, a of opposite sign)."""
    return -v0 / a


# %% [markdown]
# ## Step 3: see it
# Three graphs stacked with the same time axis. Where the x-t curve is steep the v-t graph is
# high; where v-t is above zero, x-t rises. The shaded area under v-t up to 5 s is the 45 m.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    x0, v0, a = 0.0, 4.0, 2.0
    t = np.linspace(0, 8, 321)
    ts = 5.0
    xs, vs = float(position(ts, x0, v0, a)), float(velocity(ts, v0, a))
    print(f"t = {ts} s: x = {xs:.1f} m, v = {vs:.1f} m/s")
    print("slope of x-t at 5 s:", round(slope(lambda u: position(u, x0, v0, a), ts), 3), "m/s")
    print("area under v-t, 0 to 5 s:", round(area(lambda u: velocity(u, v0, a), 0, ts), 3), "m")

    fig, ax = plt.subplots(3, 1, figsize=(6, 7), sharex=True)
    ax[0].plot(t, position(t, x0, v0, a), color="C0")
    tang = xs + vs * (t - ts)
    ax[0].plot(t, tang, "k--", lw=1, label=f"tangent: slope {vs:.0f} m/s")
    ax[0].plot([ts], [xs], "ko")
    ax[0].set_ylim(-5, 110)
    ax[0].set_ylabel("position x (m)")
    ax[0].legend(loc="upper left")
    ax[1].plot(t, velocity(t, v0, a), color="C1")
    tt = np.linspace(0, ts, 100)
    ax[1].fill_between(tt, velocity(tt, v0, a), alpha=0.25, color="C1", label="area = 45 m")
    ax[1].set_ylabel("velocity v (m/s)")
    ax[1].legend(loc="upper left")
    ax[2].plot(t, acceleration(t, a), color="C2")
    ax[2].set_ylim(0, 4)
    ax[2].set_ylabel("acceleration a (m/s^2)")
    ax[2].set_xlabel("time t (s)")
    for axis in ax:
        axis.grid(alpha=0.3)
    ax[0].set_title("Car with v0 = 4 m/s and a = 2 m/s^2")
    fig.tight_layout()
    fig.savefig(OUT / "three_graphs.png", dpi=120)

    # braking: the car stops, and the equations then say it reverses
    v0b, ab = 10.0, -2.0
    tb = np.linspace(0, 8, 321)
    tstop = stop_time(v0b, ab)
    print(f"braking from {v0b} m/s at {ab} m/s^2: stops at t = {tstop} s, x = {float(position(tstop, 0, v0b, ab)):.1f} m")
    fig2, ax2 = plt.subplots(1, 2, figsize=(8, 3.5))
    ax2[0].plot(tb, position(tb, 0, v0b, ab))
    ax2[0].axvline(tstop, color="gray", ls=":")
    ax2[0].set_xlabel("time t (s)")
    ax2[0].set_ylabel("position x (m)")
    ax2[0].set_title("x-t: turns round at the stop")
    ax2[1].plot(tb, velocity(tb, v0b, ab), color="C1")
    ax2[1].axhline(0, color="k", lw=0.8)
    ax2[1].axvline(tstop, color="gray", ls=":")
    ax2[1].set_xlabel("time t (s)")
    ax2[1].set_ylabel("velocity v (m/s)")
    ax2[1].set_title("v-t: crosses zero at 5 s")
    for axis in ax2:
        axis.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "braking.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
