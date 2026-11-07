"""Session 1 (Level 1): a pendulum and a mass on a spring swing back and forth.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: things that swing
# **A. Real-world problem.** A playground swing, a clock pendulum and a car's bouncing
# suspension all repeat the same motion again and again. How long does one swing take, how
# far does it go, and what does the graph of position against time look like? Today you
# measure three numbers for a pendulum and for a mass on a spring: the **period** T (seconds
# for one full swing), the **amplitude** A (largest distance from the middle) and the
# **frequency** f = 1 / T (swings per second, in hertz).

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81          # gravity, m/s^2


# %% [markdown]
# ## Step 1: two periods you can predict
# For small swings (a few degrees up to about 15 degrees):
#
#     spring:    T = 2 pi sqrt(m / k)     m = mass (kg), k = spring stiffness (N/m)
#     pendulum:  T = 2 pi sqrt(L / g)     L = string length (m), g = 9.81 m/s^2
#
# Notice what is missing: the pendulum period has no mass and no amplitude in it.

# %%
def spring_period(m, k):
    """Period (s) of a mass m (kg) on a spring of stiffness k (N/m)."""
    if m <= 0 or k <= 0:
        raise ValueError("mass and stiffness must be positive")
    return float(2 * np.pi * np.sqrt(m / k))


def pendulum_period(L, g=G):
    """Small-angle period (s) of a pendulum of length L (m). It does not depend on the mass."""
    if L <= 0 or g <= 0:
        raise ValueError("length and gravity must be positive")
    return float(2 * np.pi * np.sqrt(L / g))


def frequency(T):
    """Frequency in hertz (swings per second) from a period in seconds."""
    return 1.0 / T


# %% [markdown]
# ## Step 2: the graph of displacement against time
# Both motions are a cosine wave: the swing starts at its largest displacement and passes
# through the middle every half period. `x` is the displacement from the middle (m).

# %%
def spring_x(t, A, m, k):
    """Displacement (m) of the spring mass, released from rest at distance A."""
    return A * np.cos(np.sqrt(k / m) * t)


def pendulum_x(t, theta0_deg, L, g=G):
    """Small-angle sideways displacement L * theta (m) of the bob, released from rest."""
    th0 = np.radians(theta0_deg)
    return L * th0 * np.cos(np.sqrt(g / L) * t)


# %% [markdown]
# ## Step 3: measure a period from a graph
# Real data is a list of numbers, not a formula. Find the times when the curve crosses zero
# going upwards; the gap between two such times is one period.

# %%
def measure_period(t, x):
    """Average gap (s) between upward zero crossings of x(t); nan if fewer than two."""
    t, x = np.asarray(t, float), np.asarray(x, float)
    idx = np.where((x[:-1] < 0) & (x[1:] >= 0))[0]
    if len(idx) < 2:
        return float("nan")
    # linear interpolation inside the sample interval that contains each crossing
    tc = t[idx] - x[idx] * (t[idx + 1] - t[idx]) / (x[idx + 1] - x[idx])
    return float(np.mean(np.diff(tc)))


def amplitude(x):
    """Half of the distance between the highest and lowest displacement."""
    x = np.asarray(x, float)
    return float((x.max() - x.min()) / 2)


# %% [markdown]
# ## Step 4: see it
# Left: both graphs. Right: does mass change the period? For the pendulum no, for the spring yes.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t = np.linspace(0, 4, 2001)
    xs = spring_x(t, 0.05, 0.5, 20.0)
    xp = pendulum_x(t, 10.0, 1.0)
    print(f"spring  m=0.5 kg k=20 N/m : T formula {spring_period(0.5, 20):.4f} s, measured {measure_period(t, xs):.4f} s, "
          f"f = {frequency(spring_period(0.5, 20)):.3f} Hz, amplitude {amplitude(xs) * 100:.1f} cm")
    print(f"pendulum L=1 m, 10 degrees : T formula {pendulum_period(1.0):.4f} s, measured {measure_period(t, xp):.4f} s, "
          f"f = {frequency(pendulum_period(1.0)):.3f} Hz, amplitude {amplitude(xp) * 100:.1f} cm")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t, xs * 100, label="mass on spring (m = 0.5 kg, k = 20 N/m)")
    ax.plot(t, xp * 100, label="pendulum (L = 1 m, 10 degrees)")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("displacement (cm)")
    ax.set_title("Displacement against time: two cosine waves")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "swing_graphs.png", dpi=120)

    mass = np.linspace(0.1, 2.0, 40)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(mass, [spring_period(m, 20.0) for m in mass], label="spring (k = 20 N/m)")
    ax2.plot(mass, [pendulum_period(1.0) for _ in mass], label="pendulum (L = 1 m)")
    ax2.set_xlabel("mass (kg)")
    ax2.set_ylabel("period (s)")
    ax2.set_title("Mass changes the spring period, not the pendulum's")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "mass_test.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
