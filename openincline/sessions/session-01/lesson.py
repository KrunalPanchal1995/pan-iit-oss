"""Session 1 (Level 1): forces on a block on a ramp, and friction as a limit.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: forces on a ramp, and friction as a limit
# **A. Real-world problem.** A parked car on a hill, a box on a loading ramp, a book on a tilted
# desk. Tilt the surface a little and nothing moves; tilt it more and suddenly it slides.
# What decides the angle where the sliding starts?
#
# **Plan.** (1) split the weight into two parts, (2) find the most friction the surface can give,
# (3) compare, (4) draw the picture and the graph.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

G = 9.81  # gravity, m/s^2


# %% [markdown]
# ## Step 1: split the weight
# The weight m*g points straight down. On a ramp tilted by an angle t, it is easier to use two
# directions: along the slope and straight into the slope.
#
#     into the slope (balanced by the normal force N):   N = m g cos t
#     down the slope (what tries to make it slide):       F = m g sin t
#
# Check at t = 0 (flat table): N = m g and F = 0. At t = 90 degrees (a wall): N = 0 and F = m g.

# %%
def normal_force(m, theta_deg, g=G):
    """Push of the ramp on the block, perpendicular to the ramp (newtons)."""
    return m * g * np.cos(np.radians(theta_deg))


def along_slope(m, theta_deg, g=G):
    """Part of the weight pulling the block down the slope (newtons)."""
    return m * g * np.sin(np.radians(theta_deg))


# %% [markdown]
# ## Step 2: friction is a limit
# Friction does not have a fixed size. It pushes back exactly as much as needed to stop the block,
# up to a largest value: mu * N, where mu ("mu", the friction coefficient) has no unit and
# depends on the two surfaces. If the slope pull F is below mu*N, friction equals F and the net
# force is zero. If F would exceed mu*N, friction can only supply mu*N and the rest accelerates
# the block. (Session 1 uses one mu for both resting and sliding; Session 2 separates them.)

# %%
def friction_limit(m, theta_deg, mu, g=G):
    """Largest friction the surface can give (newtons)."""
    return mu * normal_force(m, theta_deg, g)


def slides(theta_deg, mu):
    """True if the block begins to slide: m g sin t > mu m g cos t, i.e. tan t > mu."""
    return bool(np.tan(np.radians(theta_deg)) > mu)


def friction_force(m, theta_deg, mu, g=G):
    """Friction that actually acts: only as large as needed, never above the limit."""
    return min(along_slope(m, theta_deg, g), friction_limit(m, theta_deg, mu, g))


def net_force(m, theta_deg, mu, g=G):
    """Net force down the slope (newtons). Zero while the block holds."""
    return along_slope(m, theta_deg, g) - friction_force(m, theta_deg, mu, g)


def acceleration(m, theta_deg, mu, g=G):
    """Acceleration down the slope (m/s^2)."""
    return net_force(m, theta_deg, mu, g) / m


def critical_angle(mu):
    """Angle (degrees) where sliding begins: tan t = mu."""
    return float(np.degrees(np.arctan(mu)))


# %% [markdown]
# ## Step 3: see it
# Left: the force on a 5 kg block against angle. The slope pull climbs, the friction limit falls,
# and they cross at the critical angle. Right: free-body diagrams just below and just above it.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    m, mu = 5.0, 0.5
    for t in (20, 26, 27, 35):
        print(f"angle {t:5.2f} deg: N = {normal_force(m, t):6.2f} N, slope pull = {along_slope(m, t):6.2f} N, "
              f"limit = {friction_limit(m, t, mu):6.2f} N, net = {net_force(m, t, mu):5.2f} N, "
              f"slides = {slides(t, mu)}")
    print(f"critical angle for mu = {mu}: {critical_angle(mu):.2f} degrees")

    ang = np.linspace(0, 60, 241)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(ang, along_slope(m, ang), label="slope pull m g sin t")
    ax.plot(ang, friction_limit(m, ang, mu), label="friction limit mu m g cos t")
    ax.plot(ang, normal_force(m, ang), ls=":", color="gray", label="normal force m g cos t")
    ax.axvline(critical_angle(mu), color="red", ls="--")
    ax.set_xlabel("ramp angle (degrees)")
    ax.set_ylabel("force (N)")
    ax.set_title("5 kg block, mu = 0.5: pull beats friction above 26.6 degrees")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "forces_vs_angle.png", dpi=120)

    fig2, axs = plt.subplots(1, 2, figsize=(8, 3.8))
    for ax2, t in zip(axs, (20, 35)):
        a = np.radians(t)
        down, nrm = np.array([np.cos(a), -np.sin(a)]), np.array([np.sin(a), np.cos(a)])
        c = np.array([0.0, 0.0])
        ax2.plot([-down[0], down[0]], [-down[1], down[1]], "k", lw=2)   # the ramp surface
        s = 0.02
        for vec, name, col in ((np.array([0, -1.0]) * m * G, "weight", "tab:blue"),
                               (nrm * normal_force(m, t), "normal", "tab:green"),
                               (-down * friction_force(m, t, mu), "friction", "tab:red")):
            ax2.arrow(c[0], c[1], s * vec[0], s * vec[1], head_width=0.04, color=col, length_includes_head=True)
            ax2.text(c[0] + s * vec[0] * 1.1, c[1] + s * vec[1] * 1.1, name, color=col, fontsize=9)
        ax2.plot(*c, "ks", ms=12)
        ax2.set_xlim(-1, 1)
        ax2.set_ylim(-1.2, 1.0)
        ax2.set_aspect("equal")
        ax2.set_title(f"{t} degrees: net = {net_force(m, t, mu):.1f} N")
        ax2.set_xlabel("x (arrow scale 0.02 m per N)")
        ax2.set_ylabel("y")
    fig2.tight_layout()
    fig2.savefig(OUT / "free_body.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
