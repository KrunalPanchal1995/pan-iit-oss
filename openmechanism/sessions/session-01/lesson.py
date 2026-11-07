"""Session 1 (Level 1): a reaction network A -> B -> C as ODEs, and what an experiment measures.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a tiny reaction network and what an experiment can see
# **A. Real-world problem.** Burning a fuel is not one step. Molecules turn into other
# molecules, which turn into others. A list of such steps, each with a speed (a *rate
# constant*), is called a **mechanism**. Real mechanisms have hundreds of steps; we start with
# two: A -> B -> C. An experiment cannot watch every molecule, it measures one thing (say, how
# much B there is over time). Today you write the mechanism as equations, solve it two ways,
# and see what a measurement of B tells you. All numbers are toys.
#
# **Plan.** (1) write the equations, (2) solve them with small time steps, (3) compare with the
# exact formula, (4) make a pretend experiment with noise.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the mechanism as equations
# A turns into B at speed `k1 * A`; B turns into C at speed `k2 * B`. Here A, B, C are amounts
# in mol/L (toy numbers) and k1, k2 are rate constants in 1/s.
#
#     dA/dt = -k1 A          dB/dt = k1 A - k2 B          dC/dt = k2 B
#
# Starting with A = 1, B = 0, C = 0, the exact solution is
# `A = exp(-k1 t)` and, for k1 different from k2,
# `B = k1 / (k2 - k1) * (exp(-k1 t) - exp(-k2 t))`, and `C = 1 - A - B` because molecules
# are not lost.

# %%
def exact(t, k1, k2, a0=1.0):
    """Exact A, B, C at time(s) t (s). Handles the special case k1 == k2."""
    t = np.asarray(t, dtype=float)
    a = a0 * np.exp(-k1 * t)
    if abs(k2 - k1) < 1e-9:
        b = a0 * k1 * t * np.exp(-k1 * t)
    else:
        b = a0 * k1 / (k2 - k1) * (np.exp(-k1 * t) - np.exp(-k2 * t))
    return a, b, a0 - a - b


def peak_time(k1, k2):
    """Time (s) at which B is largest: ln(k2/k1) / (k2 - k1), or 1/k when the two are equal."""
    if abs(k2 - k1) < 1e-9:
        return 1.0 / k1
    return float(np.log(k2 / k1) / (k2 - k1))


# %% [markdown]
# ## Step 2: solving with small steps (Euler's method)
# We do not always have a formula. The idea of Euler's method: over a small time step `dt` the
# amounts change by (rate x dt). Repeat. It is easy to write and it gets better as `dt` shrinks.

# %%
def euler(k1, k2, dt, t_end, a0=1.0):
    """Return times and an array of shape (n, 3) with A, B, C, using steps of dt seconds."""
    n = int(round(t_end / dt))
    y = np.zeros((n + 1, 3))
    y[0] = [a0, 0.0, 0.0]
    for i in range(n):
        a, b, _ = y[i]
        y[i + 1] = y[i] + dt * np.array([-k1 * a, k1 * a - k2 * b, k2 * b])
    return np.arange(n + 1) * dt, y


# %% [markdown]
# ## Step 3: what an experiment measures
# A real experiment measures something like the concentration of B at a few times, with some
# scatter (noise). We imitate it: take the exact B, and add random noise of 0.01 mol/L.
# Then a *calibration* would ask: which k1, k2 make the model pass through these points?

# %%
def pretend_experiment(k1, k2, times, noise=0.01, seed=0):
    """Noisy measurements of B at the given times."""
    rng = np.random.default_rng(seed)
    _, b, _ = exact(times, k1, k2)
    return b + noise * rng.standard_normal(np.size(times))


def misfit(k1, k2, times, measured):
    """Root-mean-square difference between model B and the measurements (mol/L)."""
    _, b, _ = exact(times, k1, k2)
    return float(np.sqrt(np.mean((b - measured) ** 2)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    k1, k2 = 0.5, 1.5
    t = np.linspace(0, 8, 400)
    a, b, c = exact(t, k1, k2)
    print(f"k1 = {k1}, k2 = {k2}: B peaks at t = {peak_time(k1, k2):.4f} s with B = {b.max():.4f} mol/L")
    for dt in (0.5, 0.1, 0.01):
        te, y = euler(k1, k2, dt, 8.0)
        err = np.abs(y[:, 1] - exact(te, k1, k2)[1]).max()
        print(f"Euler dt = {dt:5.2f} s: largest error in B = {err:.4f} mol/L")

    times = np.array([0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])
    meas = pretend_experiment(k1, k2, times)
    print("misfit with the true k1, k2:", round(misfit(k1, k2, times, meas), 4), "mol/L")
    print("misfit with k1 = 1.0, k2 = 0.5:", round(misfit(1.0, 0.5, times, meas), 4), "mol/L")

    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.plot(t, a, label="A")
    ax.plot(t, b, label="B")
    ax.plot(t, c, label="C")
    te, y = euler(k1, k2, 0.5, 8.0)
    ax.plot(te, y[:, 1], "k--", lw=1, label="B by Euler, dt = 0.5 s")
    ax.axvline(peak_time(k1, k2), color="gray", ls=":")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("concentration (mol/L, toy)")
    ax.set_title("A -> B -> C: exact curves and a coarse Euler solution")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "abc_curves.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    ax2.plot(t, b, label="model with true k1, k2")
    ax2.plot(t, exact(t, 1.0, 0.5)[1], "--", label="model with k1 = 1.0, k2 = 0.5")
    ax2.errorbar(times, meas, yerr=0.01, fmt="o", color="k", label="pretend measurements of B")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("concentration of B (mol/L, toy)")
    ax2.set_title("What an experiment sees: B only, with noise")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "experiment_B.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real mechanisms have hundreds of reactions, with rate constants that depend on temperature.
# Session 2 adds that temperature dependence (the Arrhenius form).
