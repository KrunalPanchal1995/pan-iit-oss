"""Session 3 (Level 3): collisions of two smooth discs in two dimensions, validated by a contact simulation.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: off-centre hits, a time-stepping simulation and a crash estimate
# **A. Real-world problem.** Two billiard balls hit off-centre: the first one is deflected
# and the second one leaves at an angle. How do the speeds and angles depend on how far off-centre
# the hit is, and can we trust the formulas? We check them against a simulation in which the
# discs push on each other with a stiff spring. Then we use the same ideas on a car hitting a wall.
#
# Educational model: smooth (frictionless) discs, no spin, instant collision in the formulas and a linear
# spring in the simulation. Not a tool for real crash analysis.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the contact direction decides everything
# Disc 1 moves along +x. Disc 2 sits a distance b (the impact parameter) above that line. At the moment
# of contact the line from the centre of disc 1 to the centre of disc 2 has the angle phi with
# sin(phi) = b / (R1 + R2). Smooth discs push only along that line (the unit vector n), so
# only the part of the relative velocity along n changes:
#
#     v_n = (v1 - v2) . n
#     v1' = v1 - m2/(m1 + m2) (1 + e) v_n n
#     v2' = v2 + m1/(m1 + m2) (1 + e) v_n n
#
# The part of the velocity across n (along the contact surface) does not change at all.

# %%
def disc_collision(m1, m2, v1, v2, b, r1, r2, e=1.0):
    """Velocities (v1', v2') of two smooth discs after the collision. v1 and v2 are length-2 arrays.

    Disc 2 is offset by b (in the +y direction) from the line of motion of disc 1.
    """
    if m1 <= 0 or m2 <= 0 or r1 <= 0 or r2 <= 0:
        raise ValueError("masses and radii must be positive")
    if not 0 <= e <= 1:
        raise ValueError("e must be between 0 and 1")
    if abs(b) >= r1 + r2:
        raise ValueError("the discs miss each other: |b| must be below r1 + r2")
    v1, v2 = np.asarray(v1, float), np.asarray(v2, float)
    s = b / (r1 + r2)
    n = np.array([np.sqrt(1 - s * s), s])
    vn = float(np.dot(v1 - v2, n))
    if vn <= 0:
        raise ValueError("the discs are not approaching each other")
    return v1 - m2 / (m1 + m2) * (1 + e) * vn * n, v2 + m1 / (m1 + m2) * (1 + e) * vn * n


def ke_lost(m1, m2, v1, v2, b, r1, r2, e):
    """Kinetic energy lost: 1/2 mu (1 - e^2) v_n^2 with the reduced mass mu."""
    s = b / (r1 + r2)
    n = np.array([np.sqrt(1 - s * s), s])
    vn = float(np.dot(np.asarray(v1, float) - np.asarray(v2, float), n))
    return 0.5 * m1 * m2 / (m1 + m2) * (1 - e ** 2) * vn ** 2


def angle_deg(v):
    return float(np.degrees(np.arctan2(v[1], v[0])))


# %% [markdown]
# ## Step 2: a contact simulation as an independent check
# Instead of applying the formula, let the discs overlap a little and push each other with a stiff
# spring force k x overlap along the line of centres (and a damper c x approach speed to lose energy).
# We step the positions and velocities forward in small time steps and read the final velocities.
# The result must come out close to the formula. For the damper we use the damping ratio
# zeta = -ln(e) / sqrt(pi^2 + ln(e)^2), the textbook value for a linear spring and damper.

# %%
def simulate_contact(m1, m2, v1, v2, b, r1, r2, e=1.0, k=1e6, dt=2e-6, gap=0.01):
    """Time-step two discs through a spring-damper contact. Returns (v1', v2')."""
    mu = m1 * m2 / (m1 + m2)
    zeta = 0.0 if e >= 1 else -np.log(e) / np.sqrt(np.pi ** 2 + np.log(e) ** 2)
    c = 2 * zeta * np.sqrt(k * mu)
    u1, u2 = np.asarray(v1, float).copy(), np.asarray(v2, float).copy()
    s = b / (r1 + r2)
    n0 = np.array([np.sqrt(1 - s * s), s])
    # start the discs a little way before contact, along the approach path
    x1 = np.zeros(2)
    x2 = (r1 + r2 + gap) * n0
    in_contact = False
    for _ in range(2_000_000):
        d = x2 - x1
        dist = float(np.hypot(d[0], d[1]))
        n = d / dist
        overlap = r1 + r2 - dist
        f = np.zeros(2)
        if overlap > 0:
            in_contact = True
            f_mag = max(k * overlap + c * float(np.dot(u1 - u2, n)), 0.0)   # the contact can only push
            f = -f_mag * n                                                   # force on disc 1
        elif in_contact and np.dot(u1 - u2, d) <= 0:
            break                                                            # separated and moving apart
        u1 = u1 + f / m1 * dt
        u2 = u2 - f / m2 * dt
        x1 = x1 + u1 * dt
        x2 = x2 + u2 * dt
    return u1, u2


# %% [markdown]
# ## Step 3: a crash estimate with the work-energy idea
# A car of mass m driving at speed v into a rigid wall stops in a crumple distance d. All its kinetic
# energy is absorbed by the crumpling, so the average force and deceleration are
#
#     F = m v^2 / (2 d)          a = v^2 / (2 d)

# %%
def crash(mass, speed_kmh, crumple_m):
    v = speed_kmh / 3.6
    a = v ** 2 / (2 * crumple_m)
    return {"energy_kj": 0.5 * mass * v ** 2 / 1000, "decel": a, "decel_g": a / 9.81, "force_kn": mass * a / 1000}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m1 = m2 = 1.0
    r1 = r2 = 0.5
    v1, v2 = np.array([4.0, 0.0]), np.zeros(2)
    a, b = disc_collision(m1, m2, v1, v2, 0.5, r1, r2, 1.0)
    print(f"b = 0.5 m, e = 1: disc 1 leaves with {a.round(3)} ({np.hypot(*a):.2f} m/s at {angle_deg(a):.1f} deg), "
          f"disc 2 with {b.round(3)} at {angle_deg(b):.1f} deg; angle between them {angle_deg(b) - angle_deg(a):.1f} deg")
    sa, sb = simulate_contact(m1, m2, v1, v2, 0.5, r1, r2, 1.0)
    print(f"simulation:   disc 1 {sa.round(3)}, disc 2 {sb.round(3)}")
    cr = crash(1200, 50, 0.6)
    print(f"car 1200 kg at 50 km/h, crumple 0.6 m: {cr['energy_kj']:.0f} kJ, {cr['decel_g']:.1f} g, average force {cr['force_kn']:.0f} kN")

    bs = np.linspace(0, 0.95, 96)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for e, col in ((1.0, "tab:blue"), (0.5, "tab:red")):
        ax.plot(bs, [np.hypot(*disc_collision(m1, m2, v1, v2, x, r1, r2, e)[0]) for x in bs], color=col, label=f"disc 1, e = {e}")
        ax.plot(bs, [np.hypot(*disc_collision(m1, m2, v1, v2, x, r1, r2, e)[1]) for x in bs], "--", color=col, label=f"disc 2, e = {e}")
    ax.set_xlabel("impact parameter b (m), R1 + R2 = 1 m")
    ax.set_ylabel("speed after the collision (m/s)")
    ax.set_title("A glancing hit hands over little speed")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "speeds_vs_impact.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(bs, [angle_deg(disc_collision(m1, m2, v1, v2, x, r1, r2, 1.0)[0]) for x in bs], color="tab:blue", label="disc 1")
    ax2.plot(bs, [angle_deg(disc_collision(m1, m2, v1, v2, x, r1, r2, 1.0)[1]) for x in bs], color="tab:green", label="disc 2")
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.set_xlabel("impact parameter b (m), R1 + R2 = 1 m")
    ax2.set_ylabel("direction of motion after the collision (degrees)")
    ax2.set_title("Equal discs, e = 1: they leave at 90 degrees to each other")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "angles_vs_impact.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The model has no friction between the discs (so no spin), no air drag and a perfectly stiff or perfectly
# linear contact. A real car crash involves breaking structures, occupants and rotation. The roadmap adds
# spin and many bodies.
