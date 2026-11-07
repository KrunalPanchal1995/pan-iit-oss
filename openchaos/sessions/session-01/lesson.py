"""Session 1 (Level 1): a single pendulum is predictable, a double pendulum is not.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: two almost identical starts drift apart
# **A. Real-world problem.** A grandfather clock swings the same way every time: if you know
# how it starts, you know where it will be in an hour. Hang a second pendulum from the end of
# the first and the motion looks random. Is it really random? Run the same experiment twice,
# with starting angles that differ by one hundred-millionth of a radian, and see.
#
# **Plan.** (1) simulate a single pendulum, (2) simulate a double pendulum, (3) start two
# copies almost identically, (4) measure how far apart they drift.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81      # gravity, m/s^2
LEN = 1.0     # every rod is 1 m long, every ball is 1 kg


# %% [markdown]
# ## Step 1: a single pendulum
# The angle `theta` is measured from hanging straight down. Gravity pulls it back with
#
#     theta'' = -(g / L) * sin(theta)       (rad/s^2)
#
# For small swings sin(theta) is about theta and the swing time (period) is T = 2 pi sqrt(L / g).
# For L = 1 m that is 2.006 s.
#
# We step forward in tiny time steps `h` with the Runge-Kutta 4 rule (RK4): it looks at the
# slope four times per step and takes a clever average. Session 2 explains why it is accurate.

# %%
def single_rate(state):
    """state = (theta, omega). Returns (theta', omega') for one pendulum."""
    theta, omega = state
    return np.array([omega, -(G / LEN) * np.sin(theta)])


def rk4_step(rate, state, h):
    """One RK4 step of size h (s) for any rate function."""
    k1 = rate(state)
    k2 = rate(state + 0.5 * h * k1)
    k3 = rate(state + 0.5 * h * k2)
    k4 = rate(state + h * k3)
    return state + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate(rate, state0, duration, h=0.005):
    """Return the times (s) and an array of states, one row per time."""
    n = int(round(duration / h))
    states = np.empty((n + 1, len(state0)))
    states[0] = state0
    for i in range(n):
        states[i + 1] = rk4_step(rate, states[i], h)
    return np.arange(n + 1) * h, states


def single_period(theta0, h=0.001):
    """Swing time (s) measured from the simulation: the time for the pendulum to come back to
    its release point, found where omega changes from positive to negative (first time it does)."""
    t, s = simulate(single_rate, [theta0, 0.0], 6.0, h)
    om = s[:, 1]
    # released with omega < 0 starting; omega goes + to - only back at the release side
    idx = np.where((om[:-1] > 0) & (om[1:] <= 0))[0]
    i = idx[0]
    return float(t[i] + h * om[i] / (om[i] - om[i + 1]))


# %% [markdown]
# ## Step 2: a double pendulum
# Now a second rod hangs from the first ball. There are two angles, `theta1` (upper rod) and
# `theta2` (lower rod), and two angular speeds. For equal balls and equal rods the two angular
# accelerations are (Session 2 derives them):
#
#     d = theta1 - theta2
#     theta1'' = [ -3 g sin(theta1) - g sin(theta1 - 2 theta2) - 2 sin(d) (omega2^2 + omega1^2 cos d) ] / (3 - cos 2d)
#     theta2'' = [ 2 sin(d) (2 omega1^2 + 2 g cos(theta1) + omega2^2 cos d) ] / (3 - cos 2d)

# %%
def double_rate(state):
    """state = (theta1, theta2, omega1, omega2). Equal masses, equal 1 m rods."""
    t1, t2, w1, w2 = state
    d = t1 - t2
    den = 3.0 - np.cos(2 * d)
    a1 = (-3 * G * np.sin(t1) - G * np.sin(t1 - 2 * t2) - 2 * np.sin(d) * (w2 ** 2 + w1 ** 2 * np.cos(d))) / den
    a2 = (2 * np.sin(d) * (2 * w1 ** 2 + 2 * G * np.cos(t1) + w2 ** 2 * np.cos(d))) / den
    return np.array([w1, w2, a1, a2])


def tip_positions(states):
    """Positions (x, y) in metres of the elbow ball and the end ball; y is up, pivot at (0, 0)."""
    t1, t2 = states[:, 0], states[:, 1]
    x1, y1 = LEN * np.sin(t1), -LEN * np.cos(t1)
    x2, y2 = x1 + LEN * np.sin(t2), y1 - LEN * np.cos(t2)
    return x1, y1, x2, y2


# %% [markdown]
# ## Step 3: two almost identical starts
# Release the double pendulum from rest with both rods at 120 degrees. Make a twin whose
# upper angle is larger by only 1e-8 rad (about the width of a hair compared with the size of
# the Earth). Then measure the distance between the two states as time goes on.

# %%
START = np.radians(120.0)


def twin_gap(rate, state0, delta, duration, h=0.005, index=0):
    """Absolute difference (rad) between the angle `index` of two runs whose first angle starts delta apart."""
    other = np.array(state0, dtype=float)
    other[0] += delta
    t, a = simulate(rate, state0, duration, h)
    _, b = simulate(rate, other, duration, h)
    return t, np.abs(a[:, index] - b[:, index]), a


def first_time_above(t, gap, limit):
    """First time (s) at which gap exceeds limit, or None if it never does."""
    idx = np.where(gap > limit)[0]
    return float(t[idx[0]]) if len(idx) else None


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"single pendulum, small swing (2 degrees): period {single_period(np.radians(2)):.3f} s "
          f"(formula 2 pi sqrt(L/g) = {2 * np.pi * np.sqrt(LEN / G):.3f} s)")
    delta = 1e-8
    t, gap1, _ = twin_gap(single_rate, [START, 0.0], delta, 20.0)
    t, gap2, run = twin_gap(double_rate, [START, START, 0.0, 0.0], delta, 20.0, index=1)
    print(f"start difference {delta:g} rad")
    for tt in (5, 10, 15, 20):
        i = int(tt / 0.005)
        print(f"  t = {tt:2d} s   single pendulum gap {gap1[i]:.2e} rad   double pendulum gap {gap2[i]:.2e} rad")
    print("double pendulum gap first exceeds 0.1 rad at t =", first_time_above(t, gap2, 0.1), "s")

    # Figure 1: the end-ball path of the two twin double pendulums
    other = np.array([START, START, 0.0, 0.0])
    other[0] += delta
    _, run_b = simulate(double_rate, other, 20.0, 0.005)
    fig, axs = plt.subplots(1, 2, figsize=(9, 4.5), sharex=True, sharey=True)
    for ax, k, name in ((axs[0], 8, "first 8 s"), (axs[1], 20, "first 20 s")):
        n = int(k / 0.005)
        _, _, xa, ya = tip_positions(run[:n])
        _, _, xb, yb = tip_positions(run_b[:n])
        ax.plot(xa, ya, lw=0.8, label="start A")
        ax.plot(xb, yb, lw=0.8, label="start B (1e-8 rad away)")
        ax.set_title(f"End-ball path, {name}")
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
        ax.set_xlabel("x (m)")
    axs[0].set_ylabel("y (m)")
    axs[0].legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "twin_paths.png", dpi=120)

    # Figure 2: how the gap grows
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.semilogy(t, np.maximum(gap1, 1e-16), label="single pendulum")
    ax2.semilogy(t, np.maximum(gap2, 1e-16), label="double pendulum")
    ax2.axhline(0.1, color="red", ls="--", label="0.1 rad: visibly different")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("angle gap between the twins (rad)")
    ax2.set_title("A tiny difference stays tiny, or explodes")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "gap_growth.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The double pendulum is not random: the rules are exact and the computer is exact enough.
# But a one-hundred-millionth error becomes a whole swing after a few seconds. Session 2 builds
# the equations and the checks that tell us the simulation is right; Session 3 measures the
# speed of the drift (the Lyapunov exponent).
