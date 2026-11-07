"""Session 1 (Level 1): going round a bend needs an inward push.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: going round a bend needs an inward push
# **A. Real-world problem.** In a car going round a bend you feel pressed against the door, as if
# something throws you outward. Yet nothing pushes you outward: your body just wants to carry on
# straight (inertia), and the car turns *under* you. What does push the car inward, and how hard,
# for a given speed and radius?
#
# **Plan.** (1) compute the inward acceleration and force, (2) see what happens if the push stops
# (the object flies off straight), (3) check the formula against a numerical measurement.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the inward acceleration and force
# Going round a circle of radius `r` at constant speed `v`, the *direction* of the velocity keeps
# changing, so there is an acceleration even though the speed is constant. It points to the centre:
#
#     a = v**2 / r        (m/s^2)        F = m * a = m * v**2 / r        (newtons)
#
# Doubling the speed needs 4 times the push; halving the radius needs twice the push.

# %%
def centripetal_acceleration(v, r):
    """Inward acceleration (m/s^2) for speed v (m/s) on a circle of radius r (m)."""
    if r <= 0:
        raise ValueError("radius must be positive")
    return v * v / r


def centripetal_force(m, v, r):
    """Inward force (N) needed to keep mass m (kg) on that circle."""
    return m * centripetal_acceleration(v, r)


# %% [markdown]
# ## Step 2: what if the push stops?
# Cut the string of a ball whirled in a circle: there is no outward force, the ball moves in a
# straight line along the tangent. From the centre it looks like "flying outward", but it is
# simply going straight.

# %%
def released_position(r, v, t):
    """Ball on a circle of radius r (centre at the origin) is at (r, 0) moving in +y at speed v.
    The push stops at t = 0. Returns its (x, y) a time t later: a straight line."""
    return np.array([r, v * t])


def distance_from_centre(r, v, t):
    return float(np.hypot(*released_position(r, v, t)))


# %% [markdown]
# ## Step 3: check the formula numerically
# Put a car on a circle, record its position at three close moments and compute the acceleration
# from the second difference (position(t+dt) - 2 position(t) + position(t-dt)) / dt**2.
# It should come out as v**2 / r and point to the centre.

# %%
def numeric_acceleration(v, r, dt=1e-3):
    w = v / r                                  # angular speed in rad/s
    pos = lambda t: np.array([r * np.cos(w * t), r * np.sin(w * t)])
    a = (pos(dt) - 2 * pos(0.0) + pos(-dt)) / dt ** 2
    return a                                   # vector; at t = 0 the car is at (r, 0)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    r, v, m = 50.0, 10.0, 1000.0
    print(f"car {m:.0f} kg, v = {v} m/s, r = {r} m: a = {centripetal_acceleration(v, r):.2f} m/s^2, "
          f"F = {centripetal_force(m, v, r):.0f} N")
    print("double the speed: F =", round(centripetal_force(m, 2 * v, r)), "N")
    print("half the radius:  F =", round(centripetal_force(m, v, r / 2)), "N")
    na = numeric_acceleration(v, r)
    print("numeric acceleration vector:", np.round(na, 3), "-> magnitude", round(float(np.hypot(*na)), 3))
    print("after release, 3 s later the ball is at", released_position(r, v, 3.0), "i.e.",
          round(distance_from_centre(r, v, 3.0), 1), "m from the centre")

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(r * np.cos(th), r * np.sin(th), "k--", lw=1, label="circular path")
    ax.plot(r, 0, "o", color="tab:blue", ms=9)
    ax.annotate("", xy=(r - 18, 0), xytext=(r, 0), arrowprops=dict(arrowstyle="->", color="tab:red", lw=2))
    ax.text(r - 22, 6, "inward push\nF = m v^2 / r", color="tab:red", ha="right", fontsize=9)
    ts = np.linspace(0, 5, 20)
    line = np.array([released_position(r, v, t) for t in ts])
    ax.plot(line[:, 0], line[:, 1], "-", color="tab:green", lw=2, label="path if the push stops (straight)")
    ax.plot(0, 0, "+", color="k", ms=10)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Top view: the push bends the path;\nwithout it the car goes straight")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "circle_and_tangent.png", dpi=120)

    vs = np.linspace(0, 30, 100)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for rr in (25, 50, 100):
        ax2.plot(vs, centripetal_force(m, vs, rr) / 1000, label=f"r = {rr} m")
    ax2.set_xlabel("speed v (m/s)")
    ax2.set_ylabel("inward force F (kN), car of 1000 kg")
    ax2.set_title("Inward force grows with the square of the speed")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "force_vs_speed.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# We have not asked *what* provides the inward force. On a road it is the grip between tyres and
# surface, and it has a limit. That is Session 2.
