"""Session 1 (Level 1): throw a ball. Horizontal and vertical motion are independent.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: throwing a ball
# **A. Real-world problem.** A fielder throws the ball to the wicket keeper, or a batter lofts
# it towards the boundary. How far does it go, how high does it get, and how long is it in the
# air? The surprising answer: sideways motion and up-and-down motion do not disturb each other,
# so we can handle them one at a time and then put them together.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81   # m/s^2, the acceleration of gravity near the ground


# %% [markdown]
# ## Step 1: split the launch velocity into two parts
# A ball leaves the hand at speed `v` and angle `a` above the ground. Its sideways (horizontal)
# part is `vx = v cos(a)` and its upward (vertical) part is `vy = v sin(a)`.

# %%
def components(speed, angle_deg):
    """Return (vx, vy) in m/s for a launch speed (m/s) and angle (degrees above horizontal)."""
    a = np.radians(angle_deg)
    return speed * np.cos(a), speed * np.sin(a)


# %% [markdown]
# ## Step 2: the two motions, separately
# Sideways nothing pushes the ball (we ignore air), so `x = vx * t`: constant speed.
# Up and down gravity pulls with `g`, so `y = vy * t - g t^2 / 2`: slows on the way up,
# speeds up on the way down. Neither formula contains the other's variable. That is the
# independence of the two motions.

# %%
def position(t, speed, angle_deg):
    """Ball position (x, y) in metres at time t (seconds), launched from the ground."""
    vx, vy = components(speed, angle_deg)
    t = np.asarray(t, dtype=float)
    return vx * t, vy * t - 0.5 * G * t ** 2


def fall_height(t, start_height):
    """Height of a ball dropped from rest at start_height (m) after t seconds."""
    return start_height - 0.5 * G * np.asarray(t, dtype=float) ** 2


# %% [markdown]
# ## Step 3: time in the air, peak height and range
# Going up, the ball stops rising when `vy - g t = 0`, at `t = vy / g`. It takes just as long
# to come down, so the time of flight is `T = 2 vy / g`. The peak height is
# `H = vy^2 / (2 g)`. During T the ball moves sideways at `vx`, so the range is `R = vx T`.

# %%
def flight(speed, angle_deg):
    """Return (range m, peak height m, time of flight s) on level ground, no air."""
    vx, vy = components(speed, angle_deg)
    time = 2 * vy / G
    return float(vx * time), float(vy ** 2 / (2 * G)), float(time)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    rng, peak, tof = flight(20.0, 30.0)
    print(f"v = 20 m/s at 30 degrees: range {rng:.2f} m, peak {peak:.2f} m, time {tof:.2f} s")

    # figure 1: a family of throws at the same speed
    fig, ax = plt.subplots(figsize=(7.5, 4))
    for ang in (15, 30, 45, 60, 75):
        r, h, T = flight(20.0, ang)
        t = np.linspace(0, T, 100)
        x, y = position(t, 20.0, ang)
        ax.plot(x, y, label=f"{ang} deg: range {r:.1f} m, peak {h:.1f} m")
        print(f"{ang:2d} degrees: range {r:6.2f} m  peak {h:6.2f} m  time {T:5.2f} s")
    ax.set_xlabel("horizontal distance x (m)")
    ax.set_ylabel("height y (m)")
    ax.set_title("Throws at 20 m/s: the 45 degree throw goes farthest")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "throw_family.png", dpi=120)

    # figure 2: independence. One ball dropped, one thrown sideways, from the same height.
    fig2, ax2 = plt.subplots(figsize=(6, 4.2))
    t = np.arange(0, 2.01, 0.25)
    drop_y = fall_height(t, 20.0)
    throw_x = 10.0 * t
    ax2.plot(np.zeros_like(t), drop_y, "o-", label="dropped from rest")
    ax2.plot(throw_x, drop_y, "s-", label="thrown sideways at 10 m/s")
    for xi, yi in zip(throw_x, drop_y):
        ax2.plot([0, xi], [yi, yi], color="gray", lw=0.5)
    ax2.set_xlabel("horizontal distance x (m)")
    ax2.set_ylabel("height y (m)")
    ax2.set_title("Same height at every instant (grey lines are level)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "independence.png", dpi=120)

# %% [markdown]
# ## Where this stops
# No air, flat ground, ball launched from ground level. Session 2 adds the exact equations and
# launch height, Session 3 adds air.
