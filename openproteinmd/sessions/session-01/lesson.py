"""Session 1 (Level 1): atoms as balls on springs, a Lennard-Jones pair, and motion that follows forces.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: balls, springs and the idea that motion follows forces
# **A. Real-world problem.** A protein is a long chain of atoms. Nobody can watch the atoms
# directly, so scientists *simulate* them on a computer: they write down the force on every
# atom and let Newton's law move the atoms a tiny step at a time. Today we do this for the
# smallest possible system, two atoms, using two force laws: a **spring** (a chemical bond)
# and the **Lennard-Jones** law (two atoms that attract when apart and repel when squeezed).
#
# **Important honesty note.** Everything in this repo is a *toy model* in made-up "reduced"
# units. It teaches how molecular dynamics works; it is not a real protein and not a tool for
# any medical or drug decision. General education only.
#
# **Reduced units.** We measure length in sigma, energy in epsilon and mass in m (the atom
# mass), so all three equal 1. Time then comes out in tau = sigma * sqrt(m / epsilon).

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R_MIN = 2 ** (1 / 6)                 # separation where the Lennard-Jones force is zero (sigma)
K_MATCH = 36 * 2 ** (2 / 3)          # spring constant that matches the LJ well at its bottom


# %% [markdown]
# ## Step 1: a spring and a Lennard-Jones pair
# Both are described by a potential energy V(r), where r is the distance between the two atoms.
# The force is minus the slope of V:  F(r) = -dV/dr.  Positive F pushes the atoms apart,
# negative F pulls them together.
#
#     spring:   V = (1/2) k (r - r0)^2          F = -k (r - r0)
#     LJ:       V = 4 [ (1/r)^12 - (1/r)^6 ]    F = 24 [ 2 (1/r)^12 - (1/r)^6 ] / r

# %%
def spring_potential(r, k=K_MATCH, r0=R_MIN):
    return 0.5 * k * (np.asarray(r, dtype=float) - r0) ** 2


def spring_force(r, k=K_MATCH, r0=R_MIN):
    return -k * (np.asarray(r, dtype=float) - r0)


def lj_potential(r):
    s6 = (1.0 / np.asarray(r, dtype=float)) ** 6
    return 4.0 * (s6 * s6 - s6)


def lj_force(r):
    r = np.asarray(r, dtype=float)
    s6 = (1.0 / r) ** 6
    return 24.0 * (2.0 * s6 * s6 - s6) / r


# %% [markdown]
# ## Step 2: let the force move the atoms
# Newton: acceleration = force / mass. For two equal atoms the *distance* r behaves like one
# ball of "reduced mass" mu = m/2 pushed by F(r). We step time forward in small steps dt:
#
#     v_new = v + (F / mu) * dt        r_new = r + v_new * dt

# %%
def simulate_pair(force, r_start, steps=2000, dt=0.002, mu=0.5):
    """Distance r(t) of a two-atom pair released at rest. Returns (times, r, v)."""
    t = np.arange(steps + 1) * dt
    r = np.empty(steps + 1)
    v = np.empty(steps + 1)
    r[0], v[0] = r_start, 0.0
    for i in range(steps):
        v[i + 1] = v[i] + force(r[i]) / mu * dt
        r[i + 1] = r[i] + v[i + 1] * dt
    return t, r, v


def measured_period(t, r):
    """Average time between successive maxima of r(t) (simple peak finder)."""
    peaks = [i for i in range(1, len(r) - 1) if r[i] > r[i - 1] and r[i] >= r[i + 1]]
    if len(peaks) < 2:
        return float("nan")
    return float((t[peaks[-1]] - t[peaks[0]]) / (len(peaks) - 1))


def spring_period(k, mu=0.5):
    """Exact period of a spring: 2 pi sqrt(mu / k)."""
    return 2 * np.pi * np.sqrt(mu / k)


# %% [markdown]
# ## Step 3: look at it
# The plots show the two energy curves, the two force curves and the motion. The spring and
# the LJ well agree near the bottom (that is how K_MATCH was chosen) but they disagree far
# away: a spring keeps pulling harder, LJ lets go.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    r = np.linspace(0.95, 2.5, 300)
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 4))
    axs[0].plot(r, lj_potential(r), label="Lennard-Jones V")
    axs[0].plot(r, spring_potential(r), "--", label="spring V (k = %.1f)" % K_MATCH)
    axs[0].axhline(0, color="gray", lw=0.5)
    axs[0].set_ylim(-1.5, 3)
    axs[0].set_xlabel("distance r (sigma)")
    axs[0].set_ylabel("potential energy V (epsilon)")
    axs[0].set_title("Energy: the well")
    axs[1].plot(r, lj_force(r), label="Lennard-Jones F")
    axs[1].plot(r, spring_force(r), "--", label="spring F")
    axs[1].axhline(0, color="gray", lw=0.5)
    axs[1].set_ylim(-8, 12)
    axs[1].set_xlabel("distance r (sigma)")
    axs[1].set_ylabel("force F (epsilon / sigma)")
    axs[1].set_title("Force = minus the slope of V")
    for a in axs:
        a.grid(alpha=0.3)
        a.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "potentials.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.5, 3.8))
    for name, f in (("spring", spring_force), ("Lennard-Jones", lj_force)):
        t, rr, _ = simulate_pair(f, R_MIN + 0.1)
        ax2.plot(t, rr, label="%s: period %.3f tau" % (name, measured_period(t, rr)))
    ax2.axhline(R_MIN, color="gray", ls=":")
    ax2.set_xlabel("time t (tau)")
    ax2.set_ylabel("distance r (sigma)")
    ax2.set_title("A pair released 0.1 sigma from the bottom of the well")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "pair_motion.png", dpi=120)
    print("LJ minimum at r = %.4f sigma, depth %.3f epsilon" % (R_MIN, lj_potential(R_MIN)))
    print("LJ at r=1.5: V = %.4f, F = %.4f" % (lj_potential(1.5), lj_force(1.5)))
    print("spring constant matching the LJ well: %.2f" % K_MATCH)
    print("exact spring period %.4f tau" % spring_period(K_MATCH))
    t, rr, _ = simulate_pair(spring_force, R_MIN + 0.1)
    print("simulated spring period %.4f tau" % measured_period(t, rr))
    t, rr, _ = simulate_pair(lj_force, R_MIN + 0.1)
    print("simulated LJ period %.4f tau" % measured_period(t, rr))
    t, rr, _ = simulate_pair(lj_force, R_MIN + 0.5, steps=4000)
    print("LJ large swing (0.5 sigma) period %.4f tau" % measured_period(t, rr))

# %% [markdown]
# ## Where this stops
# Two atoms cannot fold. Session 2 makes the stepping rule accurate (velocity Verlet) and adds
# a whole chain; Session 3 adds heat (a thermostat) and watches a chain collapse.
