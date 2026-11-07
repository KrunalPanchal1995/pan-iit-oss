"""Session 1 (Level 1): smooth versus blow-up.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a quantity that stays finite, and one that does not
# **A. The question.** Fluid motion (air in a room, water in a pipe) is described by the
# Navier-Stokes equations. One of the seven Clay Millennium Prize problems asks: if you start
# a 3-D flow smoothly, does the solution stay smooth for ever, or can some quantity (such as
# the speed gradient) become infinite in finite time?
#
# **HONESTY NOTE.** That question is OPEN. Nobody has proved that smooth 3-D solutions
# always exist, and nobody has proved that they can fail to exist. This repo does not try to
# solve it. It teaches what the problem asks and what is known, and lets you experiment on
# simpler models.
#
# **Plan.** (1) see a toy equation that blows up in finite time, (2) see a similar one that
# cannot, (3) see how a smooth wave steepens and pushes its energy to small scales.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: dy/dt = y**p, a toy for "growth feeds on itself"
# y is a number that changes with time t. Its rate of change is y raised to the power p.
# For p = 2 the bigger y is, the faster it grows, and that is so strong that y reaches
# infinity at a finite time. Solving by hand (separate the variables) gives
#
#     y(t) = y0 / (1 - y0 t)        for p = 2, so y is infinite at  t* = 1 / y0.
#
# For a general p > 1 the blow-up time is t* = 1 / ((p - 1) * y0**(p - 1)).
# For p = 1 (dy/dt = y) the solution y0 * exp(t) is finite at every finite time.

# %%
def blowup_time(y0, p=2.0):
    """Exact time at which y' = y**p, y(0) = y0 > 0, becomes infinite (p > 1 only)."""
    if p <= 1:
        return float("inf")
    return 1.0 / ((p - 1.0) * y0 ** (p - 1.0))


def exact_y(t, y0, p=2.0):
    """Exact solution of y' = y**p (valid for t below the blow-up time when p > 1)."""
    if p == 1:
        return y0 * np.exp(t)
    return (y0 ** (1.0 - p) - (p - 1.0) * t) ** (-1.0 / (p - 1.0))


# %% [markdown]
# ## Step 2: check it with a computer
# We step y forward with the 4th-order Runge-Kutta method (RK4) and watch it grow. Near the
# blow-up y changes extremely fast, so the time step is chosen small in proportion to
# how fast y changes: dt = c * y**(1 - p). We stop when y passes a huge number `y_big`.
# For p = 2 the exact time at which y equals y_big is 1/y0 - 1/y_big.

# %%
def rk4_step(f, y, dt):
    k1 = f(y)
    k2 = f(y + 0.5 * dt * k1)
    k3 = f(y + 0.5 * dt * k2)
    k4 = f(y + dt * k3)
    return y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0


def time_to_reach(y0, p, y_big, c=0.02):
    """Integrate y' = y**p with adaptive steps; return (time, y) when y first passes y_big."""
    y, t = float(y0), 0.0
    while y < y_big:
        dt = c * y ** (1.0 - p)
        y = rk4_step(lambda v: v ** p, y, dt)
        t += dt
    return t, y


# %% [markdown]
# ## Step 3: a smooth wave that steepens
# Real fluids move themselves: the speed u carries itself along. A one-line model of this
# is the inviscid (no friction) Burgers equation, u_t + u u_x = 0. With u(x, 0) = sin x each
# point keeps its speed and moves in a straight line (a "characteristic"):
#
#     u(x, t) = sin(X)   where  x = X + t sin(X).
#
# For t < 1 this is one smooth curve. As t approaches 1 the slope at x = pi tends to minus
# infinity: a shock (jump) forms. Session 2 studies this properly. Here we ask what steepening
# does to the *energy*: a sine wave has all its energy at wavenumber 1 (one wave per box); a
# steep front needs many short waves, so energy moves to small scales. This "cascade to small
# scales" is the reason the Navier-Stokes question matters: tiny scales mean huge gradients.

# %%
def characteristic_profile(x, t, iters=60):
    """u(x, t) for the inviscid Burgers equation with u0 = sin x, valid for t < 1."""
    X = np.array(x, dtype=float)
    for _ in range(iters):               # Newton iterations for X + t sin X = x
        X = X - (X + t * np.sin(X) - x) / (1.0 + t * np.cos(X))
    return np.sin(X)


def small_scale_fraction(t, kmin=3, n=256):
    """Fraction of the energy carried by waves with wavenumber >= kmin (n grid points)."""
    x = 2 * np.pi * np.arange(n) / n
    uh = np.fft.fft(characteristic_profile(x, t)) / n
    k = np.fft.fftfreq(n, 1.0 / n)
    e = np.abs(uh) ** 2
    return float(e[np.abs(k) >= kmin].sum() / e.sum())


# %% [markdown]
# ## Step 4: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t = np.linspace(0, 1.6, 400)
    fig, ax = plt.subplots(figsize=(6, 4))
    for p, col in ((2.0, "tab:red"), (1.5, "tab:orange"), (1.0, "tab:blue")):
        tend = min(1.6, blowup_time(1.0, p) * 0.999)
        tt = t[t < tend]
        ax.plot(tt, exact_y(tt, 1.0, p), color=col, label=f"p = {p}")
    ax.axvline(1.0, color="gray", ls=":")
    ax.set_ylim(0, 30)
    ax.set_xlabel("time t (arbitrary units)")
    ax.set_ylabel("y (arbitrary units)")
    ax.set_title("y' = y^p with y0 = 1: p = 2 is infinite at t = 1")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "blowup_vs_smooth.png", dpi=120)
    for y0 in (0.5, 1.0, 2.0):
        tn, _ = time_to_reach(y0, 2.0, 1e6)
        print(f"y0 = {y0}: RK4 reaches 1e6 at t = {tn:.6f}; exact blow-up time {blowup_time(y0):.6f}")

    x = np.linspace(0, 2 * np.pi, 400)
    fig2, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
    for tt in (0.0, 0.5, 0.9, 0.99):
        a1.plot(x, characteristic_profile(x, tt), label=f"t = {tt}")
    a1.set_xlabel("position x (radians)")
    a1.set_ylabel("speed u (arbitrary units)")
    a1.set_title("A smooth wave steepens")
    a1.grid(alpha=0.3)
    a1.legend()
    ts = np.linspace(0, 0.99, 50)
    a2.plot(ts, [100 * small_scale_fraction(v) for v in ts])
    a2.set_xlabel("time t (arbitrary units)")
    a2.set_ylabel("energy in waves with k >= 3 (percent)")
    a2.set_title("Energy moves to small scales")
    a2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "steepening.png", dpi=120)
    print(f"small-scale energy: t=0.5 -> {100 * small_scale_fraction(0.5):.1f}%, "
          f"t=0.9 -> {100 * small_scale_fraction(0.9):.1f}%")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Remember: the real 3-D Navier-Stokes question is still open.
