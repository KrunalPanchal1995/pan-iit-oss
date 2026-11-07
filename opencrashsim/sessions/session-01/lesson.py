"""Session 1 (Level 1): why a car crumples. Stopping over a longer distance means a smaller force.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: why a car crumples
# **A. Real-world problem.** A car hits a wall. The wall does not move, so the car must stop
# within whatever distance the car itself provides. If the front of the car is rigid, the car stops in
# a few centimetres and the force is huge. If the front *crumples*, the car stops over half a
# metre and the force is much smaller. Today you find the one relation behind that:
#
#     F = m v^2 / (2 d)
#
# **Plan.** (1) turn km/h into m/s, (2) compute the energy of a moving car, (3) turn that
# energy into an average stopping force for a chosen crumple distance d, (4) plot force
# against distance.
#
# *This is a simplified educational model, not a crashworthiness design tool.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81  # m/s^2, gravitational acceleration used to express forces as "g"


# %% [markdown]
# ## Step 1: speed in the right unit
# The formulas need SI units, so speeds must be in metres per second.
# 1 km/h = 1000 m / 3600 s = 1/3.6 m/s, so divide km/h by 3.6 (50 km/h = 13.89 m/s).

# %%
def kmh_to_ms(v_kmh):
    return v_kmh / 3.6


# %% [markdown]
# ## Step 2: the energy that must go somewhere
# A moving car carries kinetic energy KE = (1/2) m v^2 (joules). To stop, all of it must be
# turned into something else: here, the work done by crushing metal.

# %%
def kinetic_energy(m, v):
    """Kinetic energy in joules for mass m (kg) and speed v (m/s)."""
    return 0.5 * m * v * v


# %% [markdown]
# ## Step 3: average force over a stopping distance
# A constant force F acting over a distance d does work F*d. Setting work = kinetic energy:
#
#     F * d = (1/2) m v^2     so     F = m v^2 / (2 d)
#
# Doubling the distance halves the force. That is the whole idea of a crumple zone.
# Dividing by m gives the deceleration a = v^2 / (2 d): the mass cancels, so a heavy and a
# light car stopped over the same distance feel the same number of g.

# %%
def stopping_force(m, v, d):
    """Average force (newtons) needed to stop mass m (kg) moving at v (m/s) in distance d (m)."""
    if np.any(np.asarray(d) <= 0):
        raise ValueError("stopping distance must be positive")
    return m * v * v / (2.0 * d)


def deceleration_g(m, v, d):
    """The same stop, written as a deceleration in units of g (F = m a, so a = F / m)."""
    return stopping_force(m, v, d) / m / G


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    OUT.mkdir(exist_ok=True)
    m, v = 1000.0, kmh_to_ms(50.0)
    print(f"speed {v:.2f} m/s, kinetic energy {kinetic_energy(m, v) / 1000:.1f} kJ")
    for d in (0.05, 0.2, 0.5, 1.0):
        print(f"stop in {d:4.2f} m: force {stopping_force(m, v, d) / 1000:7.1f} kN = {deceleration_g(m, v, d):6.1f} g")

    # Figure 1: force against stopping distance (a hyperbola)
    dist = np.linspace(0.05, 1.0, 200)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(dist, stopping_force(m, v, dist) / 1000, color="C0")
    for d in (0.05, 0.2, 0.5):
        ax.plot(d, stopping_force(m, v, d) / 1000, "ko")
        ax.annotate(f"{stopping_force(m, v, d) / 1000:.0f} kN", (d, stopping_force(m, v, d) / 1000),
                    textcoords="offset points", xytext=(8, 4), fontsize=8)
    ax.set_xlabel("stopping distance d (m)")
    ax.set_ylabel("average stopping force F (kN)")
    ax.set_title("1000 kg car at 50 km/h: longer stop, smaller force")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "force_vs_distance.png", dpi=120)

    # Figure 2: the car-and-wall picture, rigid versus crumpling
    fig2, axs = plt.subplots(2, 1, figsize=(7, 4), sharex=True)
    for ax, (label, d) in zip(axs, [("rigid front: stops in 0.05 m", 0.05), ("crumple zone: stops in 0.50 m", 0.50)]):
        ax.add_patch(Rectangle((0, 0), 0.4, 1.0, color="0.7"))       # the wall
        ax.add_patch(Rectangle((0.4, 0.1), d, 0.8, color="C1", alpha=0.6))     # crushed length
        ax.add_patch(Rectangle((0.4 + d, 0.1), 3.5 - d, 0.8, color="C0", alpha=0.5))  # the rest of the car
        ax.set_xlim(0, 4.6)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_title(f"{label}: force {stopping_force(m, v, d) / 1000:.0f} kN", fontsize=9)
    axs[1].set_xlabel("position along the road (m); orange = crushed length d")
    fig2.tight_layout()
    fig2.savefig(OUT / "car_wall.png", dpi=120)
