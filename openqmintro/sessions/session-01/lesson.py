"""Session 1 (Level 1): superposition and measurement with a two-state system and an interferometer.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: amplitudes, probabilities and a coin that is not a coin
# **A. Real-world problem.** A single photon enters a beam splitter and can leave by one of two
# exits. If we put a second beam splitter after a path-length difference, the photon always leaves
# by the same exit for one setting and never for another. A coin that is flipped at the first
# splitter could never do that. What is the photon, then, between the splitters?
#
# **Plan.** (1) describe the state by two amplitudes, (2) turn amplitudes into probabilities,
# (3) apply a splitter and a phase, (4) see the difference between a superposition and a random mixture.
#
# Educational model: a two-state system (two paths). Not a model of a real experiment's detail.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the state is a pair of amplitudes
# A two-state system has the states |0> (path 0) and |1> (path 1). Its state is a pair of
# complex numbers (a, b), called amplitudes. The probabilities of finding it in path 0 or 1 are
#
#     P0 = |a|^2        P1 = |b|^2        and they must add up to 1: |a|^2 + |b|^2 = 1
#
# A superposition is a state with both a and b different from zero.

# %%
def probabilities(state):
    """Return (P0, P1) for a state given as two amplitudes."""
    s = np.asarray(state, dtype=complex)
    if s.shape != (2,):
        raise ValueError("the state must have exactly two amplitudes")
    p = np.abs(s) ** 2
    if not np.isclose(p.sum(), 1.0, atol=1e-9):
        raise ValueError("the state is not normalised: |a|^2 + |b|^2 must be 1")
    return float(p[0]), float(p[1])


def prepare(theta_deg):
    """State cos(theta/2)|0> + sin(theta/2)|1> for an angle theta in degrees."""
    t = np.radians(theta_deg) / 2
    return np.array([np.cos(t), np.sin(t)], dtype=complex)


# %% [markdown]
# ## Step 2: a beam splitter and a phase
# A 50/50 beam splitter mixes the two paths, and a phase shift multiplies the amplitude of path 1
# by exp(i phi). As matrices acting on (a, b):
#
#     BS = 1/sqrt(2) [[1, 1], [1, -1]]        PHASE(phi) = [[1, 0], [0, exp(i phi)]]
#
# Applying BS twice with nothing in between gives the state back: the splitter undoes itself.

# %%
BS = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


def phase(phi_deg):
    return np.array([[1, 0], [0, np.exp(1j * np.radians(phi_deg))]], dtype=complex)


def interferometer(phi_deg, state=(1, 0)):
    """Send a state through BS, a phase phi on path 1, and BS again. Returns the final state."""
    s = np.asarray(state, dtype=complex)
    return BS @ phase(phi_deg) @ BS @ s


# %% [markdown]
# ## Step 3: a superposition is not a random mixture
# A classical coin that was flipped at the first splitter and is in path 0 or 1 with probability
# 1/2 each would leave the second splitter by either exit with probability 1/2, whatever the phase.
# The photon does not: the amplitudes add, and for a photon entering path 0
#
#     P0(out) = cos^2(phi / 2)        P1(out) = sin^2(phi / 2)
#
# The probability depends on phi because the two amplitudes can add (phi = 0) or cancel (phi = 180 degrees).
# More generally, a state prepared at the angle theta that meets only the phase and the second splitter
# leaves by exit 0 with P0 = (1 + sin(theta) cos(phi)) / 2.

# %%
def p_out(phi_deg, state=(1, 0)):
    return probabilities(interferometer(phi_deg, state))


def after_phase_and_splitter(state, phi_deg):
    """Probabilities of the two exits for a state that already exists and now meets a phase and a splitter.

    For the state prepared at angle theta this is P0 = (1 + sin(theta) cos(phi)) / 2.
    """
    return probabilities(BS @ phase(phi_deg) @ np.asarray(state, dtype=complex))


def classical_mixture_p0(phi_deg):
    """A classical 50/50 coin: the phase changes nothing."""
    return 0.5


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("equal superposition:", probabilities(prepare(90)))
    print("BS twice gives the state back:", np.allclose(BS @ BS @ np.array([1, 0]), [1, 0]))
    for phi in (0, 90, 180):
        print(f"phase {phi:3d} deg: P0(out) = {p_out(phi)[0]:.3f}  (coin: {classical_mixture_p0(phi):.3f})")
    rng = np.random.default_rng(1)
    shots = rng.random(1000) < p_out(60)[0]
    print(f"1000 simulated photons at 60 degrees: {shots.mean():.3f} (theory {p_out(60)[0]:.3f})")

    phis = np.linspace(0, 360, 361)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(phis, [p_out(x)[0] for x in phis], color="tab:blue", label="photon (amplitudes add)")
    ax.plot(phis, [classical_mixture_p0(x) for x in phis], "--", color="tab:gray", label="classical coin")
    ax.set_xlabel("phase shift phi (degrees)")
    ax.set_ylabel("probability of exit 0")
    ax.set_title("Interference: the probability depends on the phase")
    ax.set_xticks(range(0, 361, 90))
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "interference.png", dpi=120)

    thetas = np.linspace(0, 180, 181)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(thetas, [probabilities(prepare(t))[0] for t in thetas], color="tab:blue", label="P0")
    ax2.plot(thetas, [probabilities(prepare(t))[1] for t in thetas], color="tab:orange", label="P1")
    ax2.set_xlabel("preparation angle theta (degrees)")
    ax2.set_ylabel("probability")
    ax2.set_title("The preparation angle sets the two probabilities, which always add to 1")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "preparation.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Two states are the smallest case. Session 2 gives a particle a whole range of positions in a
# box and shows why its energy cannot be anything it likes.
