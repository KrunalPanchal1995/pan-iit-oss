"""Session 1 (Level 1): momentum and the two extreme collisions, sticking together and bouncing apart.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: momentum is kept, energy may not be
# **A. Real-world problem.** Two carts roll toward each other on a smooth track. In one
# collision they stick together, in another they bounce apart. What happens to their speeds
# afterwards, and what is the same in both collisions?
#
# **Plan.** (1) define momentum and kinetic energy, (2) solve the sticking collision,
# (3) solve the perfectly bouncing collision, (4) compare what is conserved.
#
# Educational model: two bodies on a straight line, no friction, no outside forces during
# the collision. Not a tool for real crash analysis.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: momentum and kinetic energy
# Choose one direction as positive; a body moving the other way has a negative speed.
#
#     p = m v                 momentum (kg m/s)
#     KE = 1/2 m v^2          kinetic energy (J)
#
# During the short collision the bodies push on each other with equal and opposite forces, so
# the total momentum of the pair does not change: p_before = p_after.

# %%
def momentum(m, v):
    return m * v


def total_momentum(m1, v1, m2, v2):
    return momentum(m1, v1) + momentum(m2, v2)


def kinetic_energy(m, v):
    return 0.5 * m * v ** 2


def total_ke(m1, v1, m2, v2):
    return kinetic_energy(m1, v1) + kinetic_energy(m2, v2)


# %% [markdown]
# ## Step 2: the two extreme collisions
# **Sticking** (perfectly inelastic): the bodies leave together with one common speed. Momentum
# conservation gives it directly:
#
#     v = (m1 v1 + m2 v2) / (m1 + m2)
#
# **Bouncing** (perfectly elastic): the kinetic energy is also kept. Momentum and kinetic energy
# together give two speeds:
#
#     v1' = ((m1 - m2) v1 + 2 m2 v2) / (m1 + m2)
#     v2' = ((m2 - m1) v2 + 2 m1 v1) / (m1 + m2)

# %%
def stick(m1, v1, m2, v2):
    """Common speed after the bodies stick together."""
    if m1 <= 0 or m2 <= 0:
        raise ValueError("masses must be positive")
    return total_momentum(m1, v1, m2, v2) / (m1 + m2)


def bounce(m1, v1, m2, v2):
    """Speeds (v1', v2') after a perfectly elastic collision."""
    if m1 <= 0 or m2 <= 0:
        raise ValueError("masses must be positive")
    return ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2), ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)


def ke_lost_sticking(m1, v1, m2, v2):
    v = stick(m1, v1, m2, v2)
    return total_ke(m1, v1, m2, v2) - kinetic_energy(m1 + m2, v)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m1, v1, m2, v2 = 2.0, 4.0, 1.0, 0.0
    v = stick(m1, v1, m2, v2)
    a, b = bounce(m1, v1, m2, v2)
    print(f"before: p = {total_momentum(m1, v1, m2, v2):.2f} kg m/s, KE = {total_ke(m1, v1, m2, v2):.2f} J")
    print(f"sticking: v = {v:.3f} m/s, p = {total_momentum(m1, v, m2, v):.2f}, KE = {total_ke(m1, v, m2, v):.2f} J")
    print(f"bouncing: v1' = {a:.3f}, v2' = {b:.3f} m/s, p = {total_momentum(m1, a, m2, b):.2f}, KE = {total_ke(m1, a, m2, b):.2f} J")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    labels = ["before", "after sticking", "after bouncing"]
    p = [total_momentum(m1, v1, m2, v2), total_momentum(m1, v, m2, v), total_momentum(m1, a, m2, b)]
    ke = [total_ke(m1, v1, m2, v2), total_ke(m1, v, m2, v), total_ke(m1, a, m2, b)]
    x = np.arange(3)
    ax.bar(x - 0.2, p, 0.4, label="momentum (kg m/s)", color="tab:blue")
    ax.bar(x + 0.2, ke, 0.4, label="kinetic energy (J)", color="tab:orange")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("Momentum is kept in both; energy only when bouncing")
    ax.grid(alpha=0.3, axis="y")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "conserved.png", dpi=120)

    ratio = np.linspace(0.1, 10, 200)       # m2 / m1, with m1 = 1 kg, v1 = 4 m/s, body 2 at rest
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(ratio, [stick(1, 4, r, 0) for r in ratio], color="tab:red", label="sticking: common speed")
    ax2.plot(ratio, [bounce(1, 4, r, 0)[0] for r in ratio], color="tab:blue", label="bouncing: body 1 after")
    ax2.plot(ratio, [bounce(1, 4, r, 0)[1] for r in ratio], color="tab:green", label="bouncing: body 2 after")
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.set_xlabel("mass ratio m2 / m1 (no unit)")
    ax2.set_ylabel("speed after the collision (m/s)")
    ax2.set_title("A light body bounces back from a heavy one (m1 = 1 kg, v1 = 4 m/s)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "speeds_vs_mass_ratio.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Real collisions are between sticking and perfectly bouncing. Session 2 adds one number, the
# coefficient of restitution, that covers every case in between, and Session 3 leaves the straight line.
