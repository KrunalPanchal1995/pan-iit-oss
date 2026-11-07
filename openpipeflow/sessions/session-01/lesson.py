"""Session 1 (Level 1): a narrowing pipe speeds the water up and lowers its pressure.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a narrowing pipe speeds the water up and lowers its pressure
# **A. Real-world problem.** Put your thumb over the end of a garden hose and the water
# shoots out faster. Water cannot pile up inside the pipe, so where the pipe is narrower the
# water must move faster. And a faster stream has used some of its pressure to get fast.
#
# **Plan.** (1) continuity: how much faster?, (2) Bernoulli: how much pressure is traded?,
# (3) a pipe that narrows in the middle: speed and pressure along its length, (4) plot it.
# This is an idealised model: no friction (that comes in Session 2).

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

RHO = 998.0      # density of water at 20 C, kg/m^3


# %% [markdown]
# ## Step 1: continuity (water is not squeezed or lost)
# The volume flow rate Q (cubic metres per second) is the same at every cross-section of a
# steady pipe. A circle of diameter D has area A = pi D^2 / 4, so Q = A v and
#
#     A1 v1 = A2 v2     ->     v2 = v1 * (D1 / D2)^2
#
# Halve the diameter and the area drops to a quarter, so the speed rises four times.

# %%
def area(d):
    """Cross-section area (m^2) of a round pipe of diameter d (m)."""
    return np.pi * np.asarray(d, dtype=float) ** 2 / 4.0


def velocity(q, d):
    """Average speed (m/s) for flow rate q (m^3/s) in a pipe of diameter d (m)."""
    return q / area(d)


# %% [markdown]
# ## Step 2: Bernoulli (speed is paid for with pressure)
# For steady, incompressible, frictionless flow along a level pipe, the sum
# p + (1/2) rho v^2 stays constant. The second term is the *dynamic pressure*. If v goes up,
# p must go down by the same amount:
#
#     p2 = p1 + (1/2) rho (v1^2 - v2^2)

# %%
def pressure_after(p1, v1, v2, rho=RHO):
    """Static pressure (Pa) after the speed changes from v1 to v2 (m/s), level pipe, no friction."""
    return p1 + 0.5 * rho * (v1 ** 2 - v2 ** 2)


def total_pressure(p, v, rho=RHO):
    """p + 1/2 rho v^2 (Pa): constant along the pipe in the ideal model."""
    return p + 0.5 * rho * v ** 2


# %% [markdown]
# ## Step 3: a pipe that narrows in the middle
# The pipe has diameter D1 on the left, D2 on the right, and a smooth taper in between
# (a smoothstep curve from 40% to 60% of the length). At every x we apply continuity and then
# Bernoulli. Pressure is *gauge* pressure: measured above the outside air.

# %%
def diameter_profile(x, d1, d2, length=2.0):
    """Diameter (m) at distance x (m) along a pipe of the given length, narrowing smoothly."""
    t = np.clip((np.asarray(x, dtype=float) / length - 0.4) / 0.2, 0.0, 1.0)
    s = t * t * (3 - 2 * t)
    return d1 + (d2 - d1) * s


def profile(q, d1, d2, p1, length=2.0, n=201):
    """Return x, diameter, speed and gauge pressure along the pipe."""
    x = np.linspace(0.0, length, n)
    d = diameter_profile(x, d1, d2, length)
    v = velocity(q, d)
    p = pressure_after(p1, v[0], v)
    return x, d, v, p


# %% [markdown]
# ## Step 4: see it
# Left: pipe shape, speed and pressure share the same x axis. Right: how the speed gain
# depends on the diameter ratio D1/D2 (it is the square of the ratio).

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    q, d1, d2, p1 = 0.010, 0.100, 0.050, 100e3
    x, d, v, p = profile(q, d1, d2, p1)
    print(f"v1 = {v[0]:.3f} m/s, v2 = {v[-1]:.3f} m/s, p2 = {p[-1] / 1e3:.2f} kPa "
          f"(drop {(p[0] - p[-1]) / 1e3:.2f} kPa)")
    print(f"total pressure start {total_pressure(p[0], v[0]) / 1e3:.2f} kPa, "
          f"end {total_pressure(p[-1], v[-1]) / 1e3:.2f} kPa")

    fig, ax = plt.subplots(3, 1, figsize=(6, 6.5), sharex=True)
    ax[0].fill_between(x, -d / 2 * 1000, d / 2 * 1000, color="tab:blue", alpha=0.35)
    ax[0].set_ylabel("pipe radius (mm)")
    ax[0].set_title("Narrowing pipe: Q = 10 L/s, p1 = 100 kPa (gauge)")
    ax[1].plot(x, v, color="tab:green")
    ax[1].set_ylabel("speed (m/s)")
    ax[2].plot(x, p / 1e3, color="tab:red")
    ax[2].set_ylabel("gauge pressure (kPa)")
    ax[2].set_xlabel("distance along pipe (m)")
    for a in ax:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "narrowing_pipe.png", dpi=120)

    ratio = np.linspace(1, 3, 101)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(ratio, ratio ** 2)
    ax2.set_xlabel("diameter ratio D1 / D2 (no unit)")
    ax2.set_ylabel("speed ratio v2 / v1 (no unit)")
    ax2.set_title("Speed gain is the square of the diameter ratio")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "speed_gain.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
