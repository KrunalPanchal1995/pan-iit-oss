"""Session 2 (Level 2): a particle in a box: energy levels, probability density and the photons it can emit.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: why a confined particle cannot have any energy it likes
# **A. Real-world problem.** An electron is trapped in a very thin layer of semiconductor, about a
# nanometre wide. It can only take certain energies, and when it drops from one to a lower one it
# emits a photon of a definite colour. Which energies are allowed, where is the electron likely to be,
# and what colour does it emit? This is the idea behind quantum dots in some displays.
#
# Educational model: an ideal one-dimensional box with infinitely high walls. Real traps have finite
# walls (Session 4 of the roadmap) and are not one-dimensional.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
H = 6.62607015e-34       # Planck constant (J s)
ME = 9.1093837015e-31    # electron mass (kg)
EV = 1.602176634e-19     # joule per electronvolt
C = 299792458.0          # speed of light (m/s)
NM = 1e-9                # metre per nanometre


# %% [markdown]
# ## Step 1: the allowed energies
# The wave function must be zero at both walls, so a whole number of half-wavelengths must fit in
# the box of width L: lambda_n = 2 L / n. The de Broglie relation p = h / lambda then gives the energy
# E = p^2 / (2 m):
#
#     E_n = n^2 h^2 / (8 m L^2),      n = 1, 2, 3, ...
#
# The lowest energy E_1 is not zero: a particle in a box can never be at rest.

# %%
def energy_ev(n, length_nm, mass=ME):
    """Energy of level n (1, 2, ...) in electronvolts for a box of width length_nm (nm)."""
    if int(n) != n or n < 1:
        raise ValueError("n must be a whole number of at least 1")
    if length_nm <= 0 or mass <= 0:
        raise ValueError("the width and the mass must be positive")
    length = length_nm * NM
    return n ** 2 * H ** 2 / (8 * mass * length ** 2) / EV


# %% [markdown]
# ## Step 2: where is the particle?
# The wave function is psi_n(x) = sqrt(2 / L) sin(n pi x / L), and the probability density is
# |psi_n|^2. The probability to find the particle between x1 and x2 is the integral of the
# density, which can be done exactly:
#
#     P = (x2 - x1) / L - [sin(2 n pi x2 / L) - sin(2 n pi x1 / L)] / (2 n pi)

# %%
def density_times_l(n, u):
    """|psi_n|^2 x L at the relative position u = x / L (between 0 and 1): equal to 2 sin^2(n pi u)."""
    return 2 * np.sin(n * np.pi * np.asarray(u, dtype=float)) ** 2


def probability_between(n, u1, u2):
    """Probability to find the particle between u1 L and u2 L, with 0 <= u1 <= u2 <= 1."""
    if not 0 <= u1 <= u2 <= 1:
        raise ValueError("need 0 <= u1 <= u2 <= 1")
    return (u2 - u1) - (np.sin(2 * n * np.pi * u2) - np.sin(2 * n * np.pi * u1)) / (2 * n * np.pi)


# %% [markdown]
# ## Step 3: the photon from a jump
# When the particle drops from level k to a lower level n, the energy difference leaves as one
# photon: E_photon = E_k - E_n and its wavelength is lambda = h c / E_photon, which in nanometres
# is about 1239.84 / (E_photon in eV).

# %%
def photon_wavelength_nm(k, n, length_nm, mass=ME):
    """Wavelength (nm) of the photon emitted in the jump from level k down to level n (k > n)."""
    if k <= n:
        raise ValueError("a photon is emitted only when the particle drops to a lower level (k > n)")
    de = (energy_ev(k, length_nm, mass) - energy_ev(n, length_nm, mass)) * EV
    return H * C / de / NM


def width_for_wavelength_nm(k, n, wavelength_nm, mass=ME):
    """Box width (nm) for which the jump k to n emits the wanted wavelength (the inverse problem)."""
    de_per_l2 = (energy_ev(k, 1.0, mass) - energy_ev(n, 1.0, mass))     # eV for L = 1 nm: scales as 1 / L^2
    e_wanted = H * C / (wavelength_nm * NM) / EV
    return (de_per_l2 / e_wanted) ** 0.5


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"E1 = {energy_ev(1, 1.0):.4f} eV, E2 = {energy_ev(2, 1.0):.4f} eV, E3 = {energy_ev(3, 1.0):.4f} eV  (L = 1 nm)")
    print(f"photon 2 -> 1: {photon_wavelength_nm(2, 1, 1.0):.0f} nm")
    print(f"P(middle third, n = 1) = {probability_between(1, 1 / 3, 2 / 3):.3f}")
    print(f"width for a 530 nm photon from 2 -> 1: {width_for_wavelength_nm(2, 1, 530):.3f} nm")

    u = np.linspace(0, 1, 400)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for n, col in ((1, "tab:blue"), (2, "tab:green"), (3, "tab:red")):
        ax.plot(u, density_times_l(n, u), color=col, label=f"n = {n}")
    ax.set_xlabel("position x / L (no unit)")
    ax.set_ylabel("probability density x L (no unit)")
    ax.set_title("Higher levels have more nodes (places where the particle is never found)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "density.png", dpi=120)

    L = np.linspace(0.3, 2.0, 200)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for n, col in ((1, "tab:blue"), (2, "tab:green"), (3, "tab:red")):
        ax2.plot(L, [energy_ev(n, x) for x in L], color=col, label=f"n = {n}")
    ax2.set_ylim(0, 40)
    ax2.set_xlabel("box width L (nm)")
    ax2.set_ylabel("energy of the level (eV)")
    ax2.set_title("A narrower box pushes every level up as 1 / L^2")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "levels_vs_width.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The walls here are infinitely high, so the particle can never leave. With a finite wall the wave
# function leaks into the wall, and a particle can even get through a thin one: Session 3.
