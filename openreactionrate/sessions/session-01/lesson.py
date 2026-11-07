"""Session 1 (Level 1): reactions take time, and four things change the speed.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: reactions take time
# **A. Real-world problem.** Milk goes sour in a day on the table and in a week in the fridge.
# Hydrogen peroxide in a bottle lasts months, but a drop of a catalyst (even a bit of raw liver
# or manganese dioxide) makes it fizz at once. Chemical reactions have a *speed*. Today we draw
# the simplest picture of it: a concentration-versus-time curve for A -> B, and we see what a
# faster rate constant does to it.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the curve for A -> B
# Molecules of A turn into B. The more A there is, the more often A molecules collide with
# something useful, so the rate is proportional to the concentration of A:
#
#     rate = k [A]          [A] = A0 * exp(-k t)
#
# `k` is the *rate constant* (units 1/s). A big k means a fast reaction. B is what A has lost:
# [B] = A0 - [A].

# %%
def conc_A(t, A0, k):
    """Concentration of A (mol/L) at time t (s) for A -> B with rate constant k (1/s)."""
    return A0 * np.exp(-k * np.asarray(t, dtype=float))


def conc_B(t, A0, k):
    return A0 - conc_A(t, A0, k)


def half_life(k):
    """Time (s) for half of A to react. It does not depend on how much A you start with."""
    return float(np.log(2.0) / k)


def time_to_fraction(k, fraction):
    """Time (s) until the given fraction (0 to 1, exclusive of 1) of A has turned into B."""
    return float(np.log(1.0 / (1.0 - fraction)) / k)


# %% [markdown]
# ## Step 2: a catalyst and a hotter pot change k
# A catalyst (or a higher temperature) does not change what the reaction ends with; it changes
# k. We model "a catalyst that makes the step f times faster" simply as k -> f * k.

# %%
def with_catalyst(k, factor):
    return k * factor


# %% [markdown]
# ## Step 3: why the curve looks like that - count molecules
# Take 2000 molecules. In each tiny time step every remaining A molecule has the same small
# chance p of reacting (a "lucky collision"). Nobody tells the molecules to slow down; the curve
# bends because fewer A molecules are left to react.

# %%
def count_molecules(n=2000, p=0.05, steps=60, seed=1):
    """Number of A molecules left after each step (index 0 = start). p = chance per step."""
    rng = np.random.default_rng(seed)
    left = [n]
    for _ in range(steps):
        reacted = rng.random(left[-1]) < p
        left.append(left[-1] - int(reacted.sum()))
    return np.array(left)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t = np.linspace(0, 40, 400)
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for f, ls in ((1, "-"), (5, "--")):
        k = with_catalyst(0.10, f)
        ax.plot(t, conc_A(t, 1.0, k), ls, color="tab:blue", label=f"[A], k = {k:.2f} 1/s")
        ax.plot(t, conc_B(t, 1.0, k), ls, color="tab:orange", label=f"[B], k = {k:.2f} 1/s")
    ax.axhline(0.5, color="gray", ls=":")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("concentration (mol/L)")
    ax.set_title("A -> B: a 5 times larger k finishes 5 times sooner")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "a_to_b.png", dpi=120)

    steps = 60
    counts = count_molecules(2000, 0.05, steps)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    ax2.plot(range(steps + 1), counts / 2000, "o", ms=3, label="counted (2000 molecules)")
    ax2.plot(range(steps + 1), 0.95 ** np.arange(steps + 1), "-", label="(1 - p)^n, the smooth curve")
    ax2.set_xlabel("time step (each step is a short time)")
    ax2.set_ylabel("fraction of A left (no unit)")
    ax2.set_title("Random collisions give the smooth exponential curve")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "molecule_count.png", dpi=120)

    k = 0.10
    print(f"k = {k} 1/s: [A] at 10 s = {float(conc_A(10, 1.0, k)):.3f} mol/L (A0 = 1.0)")
    print(f"half-life = {half_life(k):.2f} s;  90% converted after {time_to_fraction(k, 0.9):.1f} s")
    k5 = with_catalyst(k, 5)
    print(f"with a 5x catalyst: half-life {half_life(k5):.2f} s;  90% after {time_to_fraction(k5, 0.9):.1f} s")
    print("counted fraction left after 60 steps:", counts[-1] / 2000, " smooth:", round(0.95 ** 60, 4))

# %% [markdown]
# ## Where this stops
# Here k was just a number we typed in. Session 2 asks where k comes from (temperature, activation
# energy, catalyst) and what happens if the rate depends on [A] differently.
