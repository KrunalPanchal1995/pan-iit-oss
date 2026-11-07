"""Session 1 (Level 1): a rule for how things change, and learning it from observations.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: the rule dx/dt = f(x)
# **A. Real-world problem.** A mass hangs on a spring and wobbles to a stop. To predict its
# future we do not need a formula for the whole path. We need a *rule*: "if the mass is HERE
# moving THIS fast, then in the next instant it changes THIS way". That rule is `dx/dt = f(x)`.
# A neural network can learn `f` from recorded positions. Today we draw the rule as arrows,
# follow the arrows to get a path, and read the rule back out of recorded points.
#
# **Plan.** (1) write the rule, (2) draw it as a field of arrows, (3) follow the arrows,
# (4) recover the arrows from observations, (5) plot.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
K_SPRING = 4.0      # spring stiffness divided by mass (1/s^2)
C_DAMP = 0.4        # friction divided by mass (1/s)


# %% [markdown]
# ## Step 1: the rule
# The state is two numbers: position `x` (m) and velocity `v` (m/s). The spring pulls back
# in proportion to the stretch and friction slows the motion:
#
#     dx/dt = v          (position changes at the speed v)
#     dv/dt = -k x - c v (velocity changes by the spring pull and the friction)
#
# Check by hand at x = 1 m, v = 0 with k = 4: dx/dt = 0 and dv/dt = -4 m/s^2.

# %%
def field(state, k=K_SPRING, c=C_DAMP):
    """The arrow (dx/dt, dv/dt) at a state (x, v). Works for one state or many rows."""
    s = np.asarray(state, float)
    return np.stack([s[..., 1], -k * s[..., 0] - c * s[..., 1]], axis=-1)


# %% [markdown]
# ## Step 2: follow the arrows
# Start at a state, take the arrow there, move a little way along it (`dt` seconds), repeat.
# This is the Euler method; Session 2 studies how accurate it is. For a small `dt` it traces
# the real path.

# %%
def follow_arrows(start, dt=0.005, n=1200, k=K_SPRING, c=C_DAMP):
    """Path of n + 1 states, each step: state + dt * arrow."""
    path = [np.asarray(start, float)]
    for _ in range(n):
        path.append(path[-1] + dt * field(path[-1], k, c))
    return np.array(path)


def exact_position(t, k=K_SPRING, c=C_DAMP):
    """Exact x(t) for a start at x = 1 m, v = 0 (valid while c < 2 sqrt(k): the mass overshoots)."""
    if c >= 2 * np.sqrt(k):
        raise ValueError("too much friction: no wobble, this formula does not apply")
    wd = np.sqrt(k - c * c / 4.0)
    return np.exp(-c * t / 2) * (np.cos(wd * t) + c / (2 * wd) * np.sin(wd * t))


def exact_state(t, k=K_SPRING, c=C_DAMP):
    """Exact (x, v) at time(s) t for a start at x = 1 m, v = 0: rows of [x, v]."""
    t = np.asarray(t, float)
    wd = np.sqrt(k - c * c / 4.0)
    v = -(k / wd) * np.exp(-c * t / 2) * np.sin(wd * t)
    return np.stack([exact_position(t, k, c), v], axis=-1)


def energy(state, k=K_SPRING):
    """Energy per unit mass: kinetic + spring (m^2/s^2). Friction makes it fall."""
    s = np.asarray(state, float)
    return 0.5 * (s[..., 1] ** 2 + k * s[..., 0] ** 2)


# %% [markdown]
# ## Step 3: read the rule from observations
# A sensor records the state every `dt` seconds. Two neighbouring snapshots tell us how fast
# the state changes: `(next - now) / dt`. These are *estimated arrows*. A neural network
# trained in Session 2 is simply a smooth function fitted to such arrows.

# %%
def estimated_arrows(path, dt):
    """Arrows estimated from consecutive snapshots: (path[i+1] - path[i]) / dt."""
    return (path[1:] - path[:-1]) / dt


def arrow_error(dt, k=K_SPRING, c=C_DAMP):
    """Largest relative gap between estimated arrows and the true rule at the half-way states."""
    path = exact_state(dt * np.arange(int(round(2.0 / dt)) + 1), k, c)     # recorded points of the true motion
    est = estimated_arrows(path, dt)
    mid = 0.5 * (path[1:] + path[:-1])
    true = field(mid, k, c)
    return float(np.abs(est - true).max() / np.abs(true).max())


# %% [markdown]
# ## Step 4: see it
# Grey arrows: the rule. Blue curve: the path obtained by following the arrows from
# (1 m, 0). Red arrows: the rule re-estimated from the recorded points alone.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    g = np.linspace(-1.4, 1.4, 12)
    v = np.linspace(-3.8, 3.8, 12)
    gx, gv = np.meshgrid(g, v)
    pts = np.stack([gx.ravel(), gv.ravel()], axis=1)
    arrows = field(pts)
    norm = np.hypot(arrows[:, 0] / 3.0, arrows[:, 1] / 8.0)      # draw unit-length arrows, direction only
    path = follow_arrows([1.0, 0.0])
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.quiver(pts[:, 0], pts[:, 1], arrows[:, 0] / 3.0 / norm, arrows[:, 1] / 8.0 / norm, color="0.7", angles="xy", scale=28)
    ax.plot(path[:, 0], path[:, 1], "b-", lw=2, label="follow the arrows")
    ax.plot(path[0, 0], path[0, 1], "ko", label="start")
    ax.set_xlabel("position x (m)")
    ax.set_ylabel("velocity v (m/s)")
    ax.set_title("The rule as arrows, and one path")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "spiral_field.png", dpi=120)
    print("start", path[0], " after 6 s", np.round(path[-1], 3), " energy", round(float(energy(path[0])), 3), "->", round(float(energy(path[-1])), 3))
    print("exact position at t = 3 s:", round(float(exact_position(3.0)), 4), "  followed arrows:", round(float(path[600, 0]), 4))

    dt = 0.25
    t = np.arange(0, 3.01, dt)
    rec = exact_state(t)
    est = estimated_arrows(rec, dt)
    mid = 0.5 * (rec[1:] + rec[:-1])
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    ax2.quiver(pts[:, 0], pts[:, 1], arrows[:, 0] / 3.0 / norm, arrows[:, 1] / 8.0 / norm, color="0.8", angles="xy", scale=28)
    ax2.plot(rec[:, 0], rec[:, 1], "ko-", ms=4, label="recorded points")
    ax2.quiver(mid[:, 0], mid[:, 1], est[:, 0], est[:, 1], color="red", angles="xy", scale_units="xy", scale=8, label="arrows read from points")
    ax2.set_xlabel("position x (m)")
    ax2.set_ylabel("velocity v (m/s)")
    ax2.set_title("Reading the rule from observations")
    ax2.legend(loc="upper right", fontsize=8)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "arrows_from_data.png", dpi=120)
    for dt in (0.25, 0.1, 0.02):
        print(f"recording every {dt} s: largest relative gap {arrow_error(dt):.3f}")

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
