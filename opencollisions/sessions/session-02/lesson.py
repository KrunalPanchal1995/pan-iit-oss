"""Session 2 (Level 2): the coefficient of restitution, the energy lost and the ballistic pendulum.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: every collision between sticking and bouncing
# **A. Real-world problem.** A basketball dropped from 1 m comes back to 0.64 m. A bullet
# buried in a hanging block makes it swing up a few centimetres. What happens in collisions
# that are neither perfectly sticky nor perfectly bouncy, how much energy disappears, and
# how can a swing tell us the speed of a bullet?
#
# Educational model: straight line, no friction, instant collision. Not a tool for real crash analysis.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81   # gravitational acceleration (m/s^2)


# %% [markdown]
# ## Step 1: the coefficient of restitution
# The speed of approach before the collision and the speed of separation after it are linked by
# one number e between 0 and 1:
#
#     e = (v2' - v1') / (v1 - v2)
#
# e = 1 is a perfectly bouncing collision (energy kept), e = 0 is sticking. Together with
# momentum conservation this gives both final speeds:
#
#     v1' = (m1 v1 + m2 v2 + m2 e (v2 - v1)) / (m1 + m2)
#     v2' = (m1 v1 + m2 v2 + m1 e (v1 - v2)) / (m1 + m2)

# %%
def collide(m1, v1, m2, v2, e):
    """Speeds (v1', v2') after a 1D collision with restitution e (0 to 1)."""
    if m1 <= 0 or m2 <= 0:
        raise ValueError("masses must be positive")
    if not 0 <= e <= 1:
        raise ValueError("e must be between 0 and 1")
    s = m1 * v1 + m2 * v2
    return (s + m2 * e * (v2 - v1)) / (m1 + m2), (s + m1 * e * (v1 - v2)) / (m1 + m2)


# %% [markdown]
# ## Step 2: how much energy is lost
# Write the reduced mass mu = m1 m2 / (m1 + m2). The kinetic energy that disappears (into
# heat, sound and deformation) depends only on mu, on e and on the relative speed:
#
#     dKE = 1/2 mu (1 - e^2) (v1 - v2)^2

# %%
def energy_lost(m1, v1, m2, v2, e):
    mu = m1 * m2 / (m1 + m2)
    return 0.5 * mu * (1 - e ** 2) * (v1 - v2) ** 2


def ke(m, v):
    return 0.5 * m * v ** 2


# %% [markdown]
# ## Step 3: two measurements
# **Bouncing ball.** A ball dropped from height h and rebounding to h' hits the floor with
# speed sqrt(2 g h) and leaves with sqrt(2 g h'). The floor does not move, so
#
#     e = sqrt(h' / h)
#
# **Ballistic pendulum.** A bullet of mass m is buried in a block of mass M hanging on strings.
# The sticking collision (momentum) is followed by a swing up to a height h (energy):
#
#     v_bullet = (m + M) / m x sqrt(2 g h)

# %%
def restitution_from_heights(h_drop, h_rebound):
    if h_drop <= 0 or h_rebound < 0 or h_rebound > h_drop:
        raise ValueError("need 0 <= rebound height <= drop height, and a positive drop height")
    return (h_rebound / h_drop) ** 0.5


def bullet_speed(m, big_m, h):
    """Speed of a bullet of mass m (kg) embedded in a block of mass big_m (kg) that rises h metres."""
    return (m + big_m) / m * (2 * G * h) ** 0.5


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m1, v1, m2, v2, e = 2.0, 4.0, 1.0, -1.0, 0.5
    a, b = collide(m1, v1, m2, v2, e)
    print(f"v1' = {a:.3f} m/s, v2' = {b:.3f} m/s")
    print(f"momentum before {m1 * v1 + m2 * v2:.2f}, after {m1 * a + m2 * b:.2f} kg m/s")
    print(f"KE before {ke(m1, v1) + ke(m2, v2):.2f} J, after {ke(m1, a) + ke(m2, b):.2f} J, lost {energy_lost(m1, v1, m2, v2, e):.2f} J")
    print(f"ball: e = {restitution_from_heights(1.0, 0.64):.2f};  bullet: {bullet_speed(0.010, 2.0, 0.12):.0f} m/s")

    es = np.linspace(0, 1, 101)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(es, [collide(m1, v1, m2, v2, x)[0] for x in es], color="tab:blue", label="body 1 after (2 kg)")
    ax.plot(es, [collide(m1, v1, m2, v2, x)[1] for x in es], color="tab:green", label="body 2 after (1 kg)")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xlabel("coefficient of restitution e (no unit)")
    ax.set_ylabel("speed after the collision (m/s)")
    ax.set_title("From sticking (e = 0) to bouncing (e = 1)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "speeds_vs_e.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(es, [energy_lost(m1, v1, m2, v2, x) for x in es], color="tab:red")
    ax2.plot(0.5, energy_lost(m1, v1, m2, v2, 0.5), "o", color="black")
    ax2.set_xlabel("coefficient of restitution e (no unit)")
    ax2.set_ylabel("kinetic energy lost (J)")
    ax2.set_title("Energy lost falls to zero as e goes to 1")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "energy_lost_vs_e.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Only the speed along the line of motion is handled. When the bodies hit off-centre the
# direction changes too: Session 3 treats collisions of discs in two dimensions.
