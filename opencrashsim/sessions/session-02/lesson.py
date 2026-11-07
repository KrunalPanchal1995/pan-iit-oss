"""Session 2 (Level 2): momentum, impulse, work-energy and a crumple-distance design.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: momentum, impulse and energy of a stop
# **A. Real-world problem.** Session 1 gave F = m v^2 / (2 d) from energy. There is a second,
# independent way to see a stop: *momentum and time*. A crash lasts a fraction of a second, and
# the same stop can be described by how long it takes. Today you connect both views and then
# solve a design problem: how much crumple distance keeps the driver's deceleration below
# 20 g from 50 km/h? And what changes at 100 km/h?
#
# **Plan.** (1) momentum and impulse, (2) work and energy, (3) show the two views agree,
# (4) a = v^2 / (2 d) and g-force, (5) design distance for a g limit, (6) the square law.
#
# *Simplified educational model. The 20 g figure is only a commonly quoted rough scale for
# brief loads; this lesson makes no injury predictions and is not a safety design tool.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81  # m/s^2


def kmh_to_ms(v_kmh):
    return v_kmh / 3.6


# %% [markdown]
# ## Step 1: momentum and impulse
# Momentum is p = m v (kg m/s). Newton's second law says F = dp/dt, so over a short time the
# *impulse* F*dt equals the change of momentum. For a constant force F lasting a time t:
#
#     F * t = m * v          (the car goes from m v to 0)

# %%
def momentum(m, v):
    return m * v


def force_from_time(m, v, t):
    """Constant force (N) that stops mass m (kg) at speed v (m/s) in time t (s)."""
    return m * v / t


# %% [markdown]
# ## Step 2: work and energy
# Work = force x distance. For a constant force F over a distance d: W = F*d. The work-energy
# theorem says W equals the loss of kinetic energy, (1/2) m v^2. So F = m v^2 / (2 d).

# %%
def kinetic_energy(m, v):
    return 0.5 * m * v * v


def force_from_distance(m, v, d):
    return kinetic_energy(m, v) / d


# %% [markdown]
# ## Step 3: the two views agree
# With constant deceleration a the average speed during the stop is v/2, so d = (v/2) t, i.e.
# t = 2 d / v. Put that time into F = m v / t and you get F = m v^2 / (2 d) again.
# Deceleration is a = F / m = v^2 / (2 d), and in "g" units it is a / g.

# %%
def stop_time(v, d):
    """Duration (s) of a constant-deceleration stop from speed v (m/s) in distance d (m)."""
    return 2.0 * d / v


def avg_decel(v, d):
    """Average deceleration (m/s^2) = v^2 / (2 d). Independent of the mass."""
    return v * v / (2.0 * d)


def g_force(a):
    """Express an acceleration (m/s^2) as a multiple of g."""
    return a / G


# %% [markdown]
# ## Step 4: the design problem (inverse use of the formula)
# Choose the smallest crumple distance so the average deceleration stays at or below a limit
# of `g_limit` g. Rearranging a = v^2/(2 d):  d = v^2 / (2 * g_limit * g).
# Because v is squared, doubling the speed needs *four times* the distance for the same g.

# %%
def distance_for_g(v, g_limit):
    return v * v / (2.0 * g_limit * G)


def max_speed_for_g(d, g_limit):
    """Highest speed (m/s) that a crumple distance d (m) can handle within g_limit."""
    return float(np.sqrt(2.0 * g_limit * G * d))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m = 1000.0
    for kmh in (50.0, 100.0):
        v = kmh_to_ms(kmh)
        d = distance_for_g(v, 20.0)
        print(f"{kmh:5.0f} km/h = {v:5.2f} m/s: KE {kinetic_energy(m, v) / 1000:6.1f} kJ, "
              f"distance for 20 g = {d:5.3f} m, stop time {stop_time(v, d) * 1000:5.1f} ms")
    v50 = kmh_to_ms(50.0)
    print(f"check, impulse view: F = m v / t = {force_from_time(m, v50, stop_time(v50, 0.5)) / 1000:.1f} kN; "
          f"energy view: {force_from_distance(m, v50, 0.5) / 1000:.1f} kN")
    print(f"ratio of distances 100 km/h to 50 km/h: {distance_for_g(kmh_to_ms(100), 20) / distance_for_g(v50, 20):.2f}")

    # Figure 1: deceleration (in g) against crumple distance for 50 and 100 km/h
    dist = np.linspace(0.2, 2.5, 200)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for kmh, col in ((50.0, "C0"), (100.0, "C3")):
        ax.plot(dist, g_force(avg_decel(kmh_to_ms(kmh), dist)), color=col, label=f"{kmh:.0f} km/h")
        dd = distance_for_g(kmh_to_ms(kmh), 20.0)
        ax.plot(dd, 20, "ko")
        ax.annotate(f"{dd:.2f} m", (dd, 20), textcoords="offset points", xytext=(6, 8), fontsize=8)
    ax.axhline(20, color="gray", ls="--", label="20 g (rough scale)")
    ax.set_ylim(0, 120)
    ax.set_xlabel("crumple distance d (m)")
    ax.set_ylabel("average deceleration (g)")
    ax.set_title("Deceleration against crumple distance")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "decel_vs_distance.png", dpi=120)

    # Figure 2: speed and position during a constant-deceleration stop from 50 km/h in 0.49 m
    d = distance_for_g(v50, 20.0)
    t = np.linspace(0, stop_time(v50, d), 100)
    a = avg_decel(v50, d)
    fig2, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
    a1.plot(t * 1000, v50 - a * t)
    a1.set_xlabel("time (ms)")
    a1.set_ylabel("car speed (m/s)")
    a1.set_title("Speed falls in a straight line")
    a1.grid(alpha=0.3)
    a2.plot(t * 1000, v50 * t - 0.5 * a * t ** 2)
    a2.set_xlabel("time (ms)")
    a2.set_ylabel("distance crushed (m)")
    a2.set_title(f"Reaches d = {d:.2f} m when it stops")
    a2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "stop_history.png", dpi=120)
