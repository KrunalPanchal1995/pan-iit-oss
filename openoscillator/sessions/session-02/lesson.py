"""Session 2 (Level 2): simple harmonic motion, energy exchange and damping.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of a swing
# **A. Real-world problem.** A clock must tick once every second. A phone strapped to a
# spring must bounce at a chosen rate. A car must stop bouncing after one or two swings. In
# each case you need to *choose* a length, a stiffness or a damping value, and that needs
# equations with correct units. Today: one equation of motion, its cosine solution, where the
# energy goes, and what a friction-like damping force does to the swing.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81          # gravity, m/s^2


# %% [markdown]
# ## Step 1: simple harmonic motion
# A spring pulls back with force F = -k x. Newton's second law m x'' = -k x gives
# x(t) = A cos(w t) with the angular frequency w = sqrt(k / m) in rad/s, and T = 2 pi / w.
# A small-angle pendulum has the same form with w = sqrt(g / L), so T = 2 pi sqrt(L / g).
#
# The word *simple* means: the restoring force is proportional to the displacement.

# %%
def omega_spring(m, k):
    """Angular frequency (rad/s) of a mass m (kg) on a spring k (N/m)."""
    if m <= 0 or k <= 0:
        raise ValueError("mass and stiffness must be positive")
    return float(np.sqrt(k / m))


def omega_pendulum(L, g=G):
    """Small-angle angular frequency (rad/s) of a pendulum of length L (m)."""
    if L <= 0 or g <= 0:
        raise ValueError("length and gravity must be positive")
    return float(np.sqrt(g / L))


def period_from_omega(w):
    """Period (s) from angular frequency (rad/s)."""
    return float(2 * np.pi / w)


def x_shm(t, A, w):
    """Displacement A cos(w t) of an undamped oscillator released from rest at x = A."""
    return A * np.cos(w * np.asarray(t, float))


# %% [markdown]
# ## Step 2: energy goes back and forth
# Kinetic energy KE = 1/2 m v^2 (joules) is largest in the middle, where the mass is fastest.
# Spring potential energy PE = 1/2 k x^2 is largest at the ends. Their sum stays constant at
# 1/2 k A^2 when nothing rubs.

# %%
def energies(t, x, m, k):
    """Return (KE, PE, total) in joules for displacement samples x (m) at times t (s)."""
    t, x = np.asarray(t, float), np.asarray(x, float)
    v = np.gradient(x, t)                 # velocity from the slope of the graph
    ke = 0.5 * m * v ** 2
    pe = 0.5 * k * x ** 2
    return ke, pe, ke + pe


# %% [markdown]
# ## Step 3: design problems (run the equations backwards)
# Solve T = 2 pi sqrt(L / g) for L, and T = 2 pi sqrt(m / k) for k:
#
#     L = g (T / 2 pi)^2          k = m (2 pi / T)^2
#
# The *seconds pendulum* of old clocks has a full period of 2 s (one tick per half swing).

# %%
def length_for_period(T, g=G):
    """Pendulum length (m) that gives a small-angle full period T (s)."""
    if T <= 0:
        raise ValueError("period must be positive")
    return float(g * (T / (2 * np.pi)) ** 2)


def stiffness_for_period(T, m):
    """Spring stiffness (N/m) that gives period T (s) for a mass m (kg)."""
    if T <= 0 or m <= 0:
        raise ValueError("period and mass must be positive")
    return float(m * (2 * np.pi / T) ** 2)


# %% [markdown]
# ## Step 4: damping
# A damping force -b v (b in kg/s) takes energy away. The equation m x'' + b x' + k x = 0 has
# three kinds of solution, decided by the damping ratio zeta = b / (2 sqrt(k m)):
#
# * zeta < 1, *underdamped*: it still swings, inside an envelope that shrinks like
#   exp(-b t / (2 m)); the swing is slightly slower, w_d = sqrt(w0^2 - (b / 2m)^2).
# * zeta = 1, *critically damped* (b = 2 sqrt(k m)): the fastest return with no swing.
# * zeta > 1, *overdamped*: a slow creep back.

# %%
def critical_damping(m, k):
    """The damping b (kg/s) that makes the motion critically damped."""
    return float(2 * np.sqrt(k * m))


def damping_ratio(m, k, b):
    """zeta = b / (2 sqrt(k m)); below 1 the system swings."""
    return float(b / critical_damping(m, k))


def damped_x(t, A, m, k, b):
    """Displacement for release from rest at x = A, for any damping b >= 0 (m x'' + b x' + k x = 0)."""
    t = np.asarray(t, float)
    g = b / (2 * m)                       # decay rate, 1/s
    w0 = np.sqrt(k / m)
    if abs(g - w0) < 1e-9 * w0:           # critical
        return A * (1 + g * t) * np.exp(-g * t)
    if g < w0:                            # underdamped
        wd = np.sqrt(w0 ** 2 - g ** 2)
        return A * np.exp(-g * t) * (np.cos(wd * t) + (g / wd) * np.sin(wd * t))
    s = np.sqrt(g ** 2 - w0 ** 2)         # overdamped: two decaying exponentials
    r1, r2 = -g + s, -g - s
    return A * (r2 * np.exp(r1 * t) - r1 * np.exp(r2 * t)) / (r2 - r1)


def envelope(t, A, m, k, b):
    """Upper envelope of the underdamped swing: A sqrt(1 + (g/wd)^2) exp(-b t / 2m)."""
    g = b / (2 * m)
    wd = np.sqrt(k / m - g ** 2)
    return A * np.sqrt(1 + (g / wd) ** 2) * np.exp(-g * np.asarray(t, float))


def damped_period(m, k, b):
    """Period (s) of the underdamped swing (nan if it does not swing)."""
    d = k / m - (b / (2 * m)) ** 2
    return float(2 * np.pi / np.sqrt(d)) if d > 0 else float("nan")


def time_to_fraction(m, b, frac):
    """Time (s) for the envelope to fall to the fraction frac of its start: -2 m ln(frac) / b."""
    return float(-2 * m * np.log(frac) / b)


# %% [markdown]
# ## Step 5: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m, k, A = 0.5, 20.0, 0.05
    t = np.linspace(0, 6, 3001)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t, 100 * damped_x(t, A, m, k, 0.5), label="underdamped b = 0.5 kg/s")
    ax.plot(t, 100 * envelope(t, A, m, k, 0.5), "k--", lw=0.8, label="envelope exp(-b t / 2m)")
    ax.plot(t, -100 * envelope(t, A, m, k, 0.5), "k--", lw=0.8)
    bc = critical_damping(m, k)
    ax.plot(t, 100 * damped_x(t, A, m, k, bc), label=f"critical b = {bc:.2f} kg/s")
    ax.plot(t, 100 * damped_x(t, A, m, k, 3 * bc), label=f"overdamped b = {3 * bc:.1f} kg/s")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("displacement (cm)")
    ax.set_title("Three kinds of damping, same spring")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "damping_kinds.png", dpi=120)

    x0 = x_shm(t, A, omega_spring(m, k))
    ke, pe, tot = energies(t, x0, m, k)
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.plot(t[:1500], 1000 * ke[:1500], label="kinetic energy")
    ax2.plot(t[:1500], 1000 * pe[:1500], label="spring potential energy")
    ax2.plot(t[:1500], 1000 * tot[:1500], "k--", label="total")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("energy (mJ)")
    ax2.set_title("Energy swaps between kinetic and potential")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "energy_swap.png", dpi=120)

    print(f"spring m = {m} kg, k = {k} N/m: w = {omega_spring(m, k):.3f} rad/s, T = {period_from_omega(omega_spring(m, k)):.4f} s")
    print(f"energy 1/2 k A^2 = {1000 * 0.5 * k * A ** 2:.3f} mJ; total from the graph ranges {1000 * tot[2:-2].min():.3f} to {1000 * tot[2:-2].max():.3f} mJ")
    print(f"seconds pendulum (T = 2 s): L = {length_for_period(2.0):.4f} m;  T = 1 s: L = {length_for_period(1.0):.4f} m")
    print(f"spring m = 0.5 kg with T = 1.0 s needs k = {stiffness_for_period(1.0, 0.5):.2f} N/m")
    print(f"critical damping b = {bc:.3f} kg/s; with b = 0.5: zeta = {damping_ratio(m, k, 0.5):.3f}, "
          f"damped T = {damped_period(m, k, 0.5):.4f} s, envelope time constant 2m/b = {2 * m / 0.5:.1f} s, "
          f"amplitude fraction after 5 s = {envelope(5.0, A, m, k, 0.5) / envelope(0.0, A, m, k, 0.5):.4f}")
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
