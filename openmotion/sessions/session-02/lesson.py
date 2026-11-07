"""Session 2 (Level 2): equations of motion, piecewise trips and a stopping-distance design.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: equations of motion, piecewise motion and stopping before a hurdle
# **A. Real-world problem.** A driver sees a hurdle 40 m ahead. The car is doing 20 m/s
# (72 km/h). The driver needs time to react and the brakes need distance to work. Does the car
# stop in time, and what is the fastest speed that is still safe? We also read a whole trip
# (speed up, cruise, brake) from its velocity graph.
#
# This is a simplified model: constant braking on a dry flat road. Real stopping distances depend
# on tyres, surface, load and the driver. Never use this lesson to decide how to drive.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the equations of motion (constant acceleration)
#
#     v = v0 + a t        dx = v0 t + (1/2) a t^2        v^2 = v0^2 + 2 a dx
#
# The third one has no time in it: it links speed and distance directly. Braking to rest from
# speed v with deceleration a (a positive number) takes dx = v^2 / (2 a).

# %%
def final_speed_squared(v0, a, dx):
    """v^2 = v0^2 + 2 a dx (a is signed: negative when slowing down)."""
    return v0 ** 2 + 2.0 * a * dx


def braking_distance(v, a):
    """Distance to stop from speed v (m/s) with deceleration a > 0 (m/s^2)."""
    return v ** 2 / (2.0 * a)


def stopping_distance(v, t_react, a):
    """Reaction distance (constant speed for t_react seconds) plus braking distance."""
    return v * t_react + braking_distance(v, a)


def max_safe_speed(D, t_react, a):
    """Largest speed that stops within D metres: solve v*tr + v^2/(2a) = D for v > 0."""
    return a * (-t_react + np.sqrt(t_react ** 2 + 2.0 * D / a))


# %% [markdown]
# ## Step 2: piecewise motion
# A trip in three pieces: speed up from rest at a_acc until the cruise speed v_c, hold v_c for
# t_c seconds, then brake to rest at a_brake. In each piece the equations above hold; the
# end of one piece is the start of the next.

# %%
def trip(a_acc, v_c, t_c, a_brake):
    """Times and distances of the three pieces."""
    t1, t3 = v_c / a_acc, v_c / a_brake
    d1, d2, d3 = 0.5 * v_c * t1, v_c * t_c, 0.5 * v_c * t3
    return {"t1": t1, "t2": t_c, "t3": t3, "d1": d1, "d2": d2, "d3": d3,
            "T": t1 + t_c + t3, "D": d1 + d2 + d3, "a_acc": a_acc, "a_brake": a_brake, "v_c": v_c}


def trip_state(t, tr):
    """Acceleration, velocity and position of the trip at times t (arrays)."""
    t = np.asarray(t, dtype=float)
    t1, t2, t3 = tr["t1"], tr["t2"], tr["t3"]
    a = np.zeros_like(t)
    v = np.zeros_like(t)
    x = np.zeros_like(t)
    for i, ti in enumerate(t):
        if ti <= t1:
            a[i], v[i], x[i] = tr["a_acc"], tr["a_acc"] * ti, 0.5 * tr["a_acc"] * ti ** 2
        elif ti <= t1 + t2:
            a[i], v[i], x[i] = 0.0, tr["v_c"], tr["d1"] + tr["v_c"] * (ti - t1)
        elif ti <= t1 + t2 + t3:
            s = ti - t1 - t2
            a[i], v[i] = -tr["a_brake"], tr["v_c"] - tr["a_brake"] * s
            x[i] = tr["d1"] + tr["d2"] + tr["v_c"] * s - 0.5 * tr["a_brake"] * s ** 2
        else:
            a[i], v[i], x[i] = 0.0, 0.0, tr["D"]
    return a, v, x


def displacement_from_velocity(t, v):
    """Area under the v-t graph (trapezoid rule) = displacement."""
    t, v = np.asarray(t, dtype=float), np.asarray(v, dtype=float)
    return float(np.sum(0.5 * (v[1:] + v[:-1]) * np.diff(t)))


def acceleration_intervals(t, a, tol=1e-9):
    """List of (t_start, t_end, kind) where kind is 'speeding up', 'cruising' or 'slowing down'."""
    out = []
    kinds = np.where(a > tol, "speeding up", np.where(a < -tol, "slowing down", "cruising"))
    start = 0
    for i in range(1, len(t) + 1):
        if i == len(t) or kinds[i] != kinds[start]:
            out.append((float(t[start]), float(t[i - 1]), str(kinds[start])))
            start = i
    return out


# %% [markdown]
# ## Step 3: see it
# Left: the v-t graph of the trip; the three shaded areas add up to the whole distance.
# Right: stopping distance against speed; the car with a reaction time needs more road than
# the braking alone, and the red line is the hurdle.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    tr = trip(2.0, 12.0, 10.0, 3.0)
    print(f"trip: pieces {tr['t1']:.0f} s, {tr['t2']:.0f} s, {tr['t3']:.0f} s; "
          f"distances {tr['d1']:.0f}, {tr['d2']:.0f}, {tr['d3']:.0f} m; total {tr['D']:.0f} m in {tr['T']:.0f} s")
    t = np.linspace(0, tr["T"], 801)
    a, v, x = trip_state(t, tr)
    print("area under v-t:", round(displacement_from_velocity(t, v), 3), "m; average speed",
          round(tr["D"] / tr["T"], 2), "m/s")
    for seg in acceleration_intervals(t, a):
        print("interval", seg)

    fig, ax = plt.subplots(1, 2, figsize=(9, 4))
    ax[0].plot(t, v, color="C1")
    for lo, hi, col in [(0, tr["t1"], "C0"), (tr["t1"], tr["t1"] + tr["t2"], "C2"), (tr["t1"] + tr["t2"], tr["T"], "C3")]:
        m = (t >= lo) & (t <= hi)
        ax[0].fill_between(t[m], v[m], alpha=0.3, color=col)
    ax[0].text(1.2, 3, "36 m", fontsize=9)
    ax[0].text(10, 5, "120 m", fontsize=9)
    ax[0].text(17.3, 3, "24 m", fontsize=9)
    ax[0].set_xlabel("time t (s)")
    ax[0].set_ylabel("velocity v (m/s)")
    ax[0].set_title("Trip: areas under v-t add to 180 m")
    vv = np.linspace(0, 30, 121)
    ax[1].plot(vv, braking_distance(vv, 6.0), label="braking only")
    ax[1].plot(vv, stopping_distance(vv, 0.8, 6.0), label="reaction 0.8 s + braking")
    ax[1].axhline(40, color="red", ls="--", label="hurdle at 40 m")
    vs = float(max_safe_speed(40, 0.8, 6.0))
    ax[1].plot([vs], [40], "ko")
    ax[1].annotate(f"{vs:.1f} m/s", (vs, 40), textcoords="offset points", xytext=(8, -16))
    ax[1].set_xlabel("speed v (m/s)")
    ax[1].set_ylabel("stopping distance (m)")
    ax[1].set_title("Stopping distance (a = 6 m/s^2)")
    ax[1].set_ylim(0, 120)
    ax[1].legend(fontsize=8, loc="upper left")
    for axis in ax:
        axis.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "trip_and_stopping.png", dpi=120)

    d = stopping_distance(20, 0.8, 6.0)
    print(f"20 m/s, 0.8 s, 6 m/s^2: reaction {20 * 0.8:.1f} m + braking {braking_distance(20, 6):.2f} m = {d:.2f} m")
    print(f"speed when passing 40 m: {np.sqrt(final_speed_squared(20, -6, 40 - 16)):.2f} m/s")
    print(f"largest safe speed for 40 m: {vs:.2f} m/s ({vs * 3.6:.1f} km/h)")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
