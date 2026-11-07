"""Session 2 (Level 2): angular momentum, torque and the precession-rate formula.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the precession formula and a design problem
# **A. Real-world problem.** A demonstrator holds a bicycle wheel by one end of its axle. The
# wheel is spun and the axle swings slowly round. Can we choose the spin rate so that the axle
# makes exactly one full circle every 4 seconds?
#
# **Plan.** (1) moment of inertia of a disc, (2) the rule torque = dL/dt, (3) the formula
# `Omega_p = m g r / (I w)`, (4) its assumptions, (5) invert it to choose the spin.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81      # m/s^2


# %% [markdown]
# ## Step 1: moment of inertia of a solid disc
# `I = m R^2 / 2` about its axle (kg m^2). Units: kg times metre squared. Mass far from the
# axle counts more (R is squared). A wheel with all its mass on the rim has `I = m R^2`,
# twice as much for the same mass and radius.

# %%
def disc_inertia(m, radius):
    """I = m R^2 / 2, kg m^2."""
    return m * radius ** 2 / 2


def ring_inertia(m, radius):
    """Wheel with all its mass on the rim: I = m R^2."""
    return m * radius ** 2


def angular_momentum(inertia, w):
    """L = I w, kg m^2/s."""
    return inertia * w


# %% [markdown]
# ## Step 2: torque = dL/dt, and the precession rate
# Newton's second law for rotation: the torque is the rate of change of the angular momentum
# vector. For a wheel with a horizontal axle held at one end, the weight `m g` acts at the
# centre, a distance `r` from the support, so `tau = m g r`. It is horizontal and at right
# angles to `L`, so it does not change the size of `L`, only its direction. In a short time `dt`
# the arrow turns by the angle `d(phi) = tau dt / L`. Dividing by dt:
#
#     Omega_p = d(phi)/dt = tau / L = m g r / (I w)
#
# Assumptions: the spin `w` is fast compared with the circling (`I w` much more than
# `sqrt(4 I1 m g r)`, checked below), the spin rate is steady, there is no friction, and
# the axle makes a steady angle with the vertical. Units: rad/s. One circle takes `2 pi / Omega_p` seconds.

# %%
def precession_rate(m, r, inertia, w, g=G):
    """Omega_p = m g r / (I w), rad/s."""
    return m * g * r / (inertia * w)


def precession_period(m, r, inertia, w, g=G):
    """Seconds for one full circle of the axle."""
    return 2 * np.pi / precession_rate(m, r, inertia, w, g)


def spin_for_period(m, r, inertia, period, g=G):
    """Spin w (rad/s) that gives one precession circle in `period` seconds (design problem)."""
    return m * g * r * period / (2 * np.pi * inertia)


def rpm(w):
    """rad/s to revolutions per minute."""
    return w * 60 / (2 * np.pi)


# %% [markdown]
# ## Step 3: when is "fast spin" fast enough?
# The exact steady precession of a symmetric top whose axis is at angle `theta` from the
# upward vertical (Session 3 derives it from the Lagrangian) solves
#
#     I1 cos(theta) Omega^2 - I3 w3 Omega + m g r = 0
#
# where `I1` is the moment of inertia about a perpendicular axis through the support (parallel
# axis theorem: `I1 = m R^2/4 + m r^2` for a disc) and `w3` is the spin component along the axle.
# The slow root is the precession we want. It exists only if `(I3 w3)^2 >= 4 I1 m g r cos(theta)`.
# At `theta = 90` degrees (horizontal axle) the Omega^2 term vanishes and the formula is exact.

# %%
def inertia_about_support(m, radius, r):
    """I1 = m R^2 / 4 + m r^2 (disc, axis through the support perpendicular to the axle)."""
    return m * radius ** 2 / 4 + m * r ** 2


def precession_exact(m, radius, r, w3, theta, g=G):
    """Slow root of I1 cos(theta) Om^2 - I3 w3 Om + m g r = 0. Returns nan if no steady precession."""
    i3 = disc_inertia(m, radius)
    i1 = inertia_about_support(m, radius, r)
    c = np.cos(theta)
    if abs(c) < 1e-12:
        return m * g * r / (i3 * w3)
    disc = (i3 * w3) ** 2 - 4 * i1 * c * m * g * r
    if disc < 0:
        return float("nan")
    return (i3 * w3 - np.sqrt(disc)) / (2 * i1 * c)


def fast_spin_ratio(m, radius, r, w3, g=G):
    """(I3 w3)^2 / (4 I1 m g r). Values well above 1 mean the fast-spin formula is good."""
    i3 = disc_inertia(m, radius)
    return (i3 * w3) ** 2 / (4 * inertia_about_support(m, radius, r) * m * g * r)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # the design problem: a 2 kg solid-disc wheel, R = 0.30 m, centre 0.25 m from the support
    m, R, r = 2.0, 0.30, 0.25
    I = disc_inertia(m, R)
    T = 4.0
    w = spin_for_period(m, r, I, T)
    print(f"I = {I:.4f} kg m^2; spin for one circle per {T:.0f} s: {w:.2f} rad/s = {rpm(w):.0f} rpm")
    print(f"check: Omega_p = {precession_rate(m, r, I, w):.4f} rad/s (target {2 * np.pi / T:.4f}), "
          f"period {precession_period(m, r, I, w):.3f} s")
    print(f"L = {angular_momentum(I, w):.3f} kg m^2/s, weight torque = {m * G * r:.3f} N m")
    print(f"fast-spin ratio = {fast_spin_ratio(m, R, r, w):.2f}")
    for k in (0.5, 1, 2):
        print(f"spin x{k}: period {precession_period(m, r, I, k * w):.2f} s")
    for th in (90, 60, 30):
        print(f"axle at {th} deg from vertical, w = {w:.1f}: exact {precession_exact(m, R, r, w, np.radians(th)):.4f} rad/s "
              f"(formula {precession_rate(m, r, I, w):.4f})")

    ws = np.linspace(5, 120, 300)
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.plot(ws, [precession_period(m, r, I, x) for x in ws], label="period 2 pi / Omega_p")
    ax.axhline(T, color="tab:red", ls="--", label="target 4 s")
    ax.plot([w], [T], "o", color="tab:red")
    ax.set_xlabel("spin w (rad/s)")
    ax.set_ylabel("time for one circle (s)")
    ax.set_title("Faster spin, slower precession")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "period_vs_spin.png", dpi=120)

    wl = np.linspace(20, 120, 200)
    fig2, ax2 = plt.subplots(figsize=(6.5, 4.2))
    ax2.plot(wl, [precession_rate(m, r, I, x) for x in wl], label="formula m g r / (I w)")
    ax2.plot(wl, [precession_exact(m, R, r, x, np.radians(60)) for x in wl], "--", label="exact, axle 60 deg from vertical")
    ax2.set_xlabel("spin w (rad/s)")
    ax2.set_ylabel("precession rate (rad/s)")
    ax2.set_title("Formula versus exact steady precession")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "rate_vs_spin.png", dpi=120)
