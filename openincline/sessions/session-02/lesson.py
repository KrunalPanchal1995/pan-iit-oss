"""Session 2 (Level 2): equations of the ramp, static versus kinetic friction, and a design problem.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the equations, and two kinds of friction
# **A. Real-world problem.** A warehouse needs a ramp so that crates slide down by themselves
# and arrive at a gentle, known speed. Too shallow and the crate sticks; too steep and it crashes
# into the stop. Which angle, for which surface?
#
# **Plan.** (1) write the model with two friction coefficients, (2) find the acceleration,
# (3) plot friction and acceleration against angle, (4) solve the design problem backwards.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81  # gravity, m/s^2


# %% [markdown]
# ## Step 1: two friction coefficients
# A block at rest is held by *static* friction, which can reach at most mu_s * N. Once it slides,
# *kinetic* friction acts with a fixed size mu_k * N, usually a little smaller (mu_k <= mu_s).
#
#     N = m g cos t        slope pull = m g sin t
#     static: friction = slope pull   while   m g sin t <= mu_s m g cos t   i.e.  tan t <= mu_s
#     sliding: m a = m g sin t - mu_k m g cos t   so   a = g (sin t - mu_k cos t)
#
# Mass m cancels from a, and from the test tan t <= mu_s. That is why a heavy and a light
# crate of the same material start sliding at the same angle.

# %%
def normal_force(m, theta_deg, g=G):
    return m * g * np.cos(np.radians(theta_deg))


def friction_acting(m, theta_deg, mu_s, mu_k, g=G):
    """Friction force on a block released from rest (newtons): static while it holds, kinetic once it slips."""
    t = np.radians(theta_deg)
    if np.tan(t) <= mu_s:
        return m * g * np.sin(t)          # static friction equals the pull
    return mu_k * m * g * np.cos(t)       # kinetic friction


def accel_from_rest(theta_deg, mu_s, mu_k, g=G):
    """Acceleration down the slope (m/s^2) of a block released from rest. mu_k must not exceed mu_s."""
    t = np.radians(theta_deg)
    if np.tan(t) <= mu_s:
        return 0.0
    return float(g * (np.sin(t) - mu_k * np.cos(t)))


def slide_angle(mu_s):
    """Angle (degrees) where a block at rest first slips: tan t = mu_s."""
    return float(np.degrees(np.arctan(mu_s)))


def mu_s_from_angle(theta_deg):
    """Measure mu_s from the tilt angle at which slipping starts."""
    return float(np.tan(np.radians(theta_deg)))


# %% [markdown]
# ## Step 2: from acceleration to speed and distance
# Starting from rest with constant a: v = a t and distance x = (1/2) a t^2.

# %%
def speed_after(a, t):
    return a * t


def distance_after(a, t):
    return 0.5 * a * t * t


# %% [markdown]
# ## Step 3: the design problem, solved numerically
# We want a given acceleration a_target for a known mu_k. a(t) rises steadily with angle, so
# bisection (halve the search interval again and again) finds the angle. Afterwards we also
# check that the angle is steep enough for the crate to start at all (tan t > mu_s).

# %%
def angle_for_acceleration(a_target, mu_k, g=G, lo=0.0, hi=89.0, iters=60):
    """Angle (degrees) that gives sliding acceleration a_target for kinetic friction mu_k."""
    f = lambda d: g * (np.sin(np.radians(d)) - mu_k * np.cos(np.radians(d))) - a_target
    if f(lo) > 0 or f(hi) < 0:
        raise ValueError("target acceleration is outside what any angle can give")
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# %% [markdown]
# ## Step 4: see it
# Left: friction acting on a 10 kg crate against angle. It climbs with the pull, reaches mu_s N,
# then *drops* to mu_k N when slipping starts. Right: the acceleration, zero until the slide
# angle and then jumping up.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m, mu_s, mu_k = 10.0, 0.40, 0.30
    ang = np.linspace(0, 50, 501)
    fr = [friction_acting(m, d, mu_s, mu_k) for d in ang]
    ac = [accel_from_rest(d, mu_s, mu_k) for d in ang]
    print(f"slide angle for mu_s = {mu_s}: {slide_angle(mu_s):.2f} degrees")
    a30 = accel_from_rest(30, mu_s, mu_k)
    print(f"m = {m} kg, 30 degrees, mu_s = {mu_s}, mu_k = {mu_k}: a = {a30:.3f} m/s^2, "
          f"v(2 s) = {speed_after(a30, 2):.2f} m/s, distance(2 s) = {distance_after(a30, 2):.2f} m")
    a_t = 2 * 3.0 / 2.0 ** 2
    th = angle_for_acceleration(a_t, mu_k)
    print(f"design: 3 m in 2 s needs a = {a_t} m/s^2 -> angle {th:.2f} degrees "
          f"(starts since tan t = {np.tan(np.radians(th)):.3f} > {mu_s})")
    for d in (24, 25, 26):
        print(f"  integer angle {d}: a = {accel_from_rest(d, mu_s, mu_k):.3f} m/s^2, "
              f"distance in 2 s = {distance_after(accel_from_rest(d, mu_s, mu_k), 2):.2f} m")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(ang, fr, label="friction acting (N)")
    ax.plot(ang, [mu_s * normal_force(m, d) for d in ang], ls=":", color="gray", label="static limit mu_s N")
    ax.axvline(slide_angle(mu_s), color="red", ls="--", label="slide angle")
    ax.set_xlabel("ramp angle (degrees)")
    ax.set_ylabel("friction force (N)")
    ax.set_title("Friction rises, then drops when slipping starts (10 kg)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "friction_vs_angle.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(ang, ac, label="mu_s = 0.40, mu_k = 0.30")
    ax2.plot(ang, [accel_from_rest(d, 0.40, 0.40) for d in ang], ls="--", label="mu_s = mu_k = 0.40")
    ax2.axhline(a_t, color="green", ls=":", label="design target 1.5 m/s^2")
    ax2.plot([th], [a_t], "o", color="green")
    ax2.set_xlabel("ramp angle (degrees)")
    ax2.set_ylabel("acceleration from rest (m/s^2)")
    ax2.set_title("Acceleration jumps from 0 once the block slips")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "accel_vs_angle.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
