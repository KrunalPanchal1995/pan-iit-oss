"""Session 3 (Level 3): tunnelling through a barrier, solved exactly and numerically, and an STM estimate.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a particle gets through a wall it does not have the energy to climb
# **A. Real-world problem.** A scanning tunnelling microscope (STM) holds a sharp metal tip a
# fraction of a nanometre above a surface. Electrons cross the empty gap even though they do not have
# the energy to climb out of the metal, and the current changes enormously when the tip moves by one
# atomic diameter. How large is the tunnelling probability, how does it depend on the width, and can we
# trust a formula by checking it against a numerical solution?
#
# Educational model: one dimension, an electron, rectangular or smooth barriers made of flat
# slices, no electron-electron interaction. Not a model of a real STM.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
HBAR = 1.054571817e-34
ME = 9.1093837015e-31
EV = 1.602176634e-19
# hbar^2 / (2 m) in eV nm^2: with this constant, k = sqrt(E / HB2M) in 1/nm for E in eV
HB2M = HBAR ** 2 / (2 * ME) / EV * 1e18


# %% [markdown]
# ## Step 1: the exact formula for a rectangular barrier
# An electron with energy E (eV) meets a barrier of height V0 (eV) and width a (nm), with E below V0.
# Inside the barrier the wave does not oscillate: it decays as exp(-kappa x) with
#
#     kappa = sqrt((V0 - E) / HB2M)         (1/nm)
#
# and the transmission probability is exactly
#
#     T = 1 / (1 + V0^2 sinh^2(kappa a) / (4 E (V0 - E)))
#
# For a thick barrier (kappa a well above 1) this is close to T = 16 E (V0 - E) / V0^2 x exp(-2 kappa a):
# the probability falls exponentially with the width.

# %%
def transmission(e_ev, v0_ev, a_nm):
    """Exact transmission probability of a rectangular barrier (E below, equal to or above V0)."""
    if e_ev <= 0 or v0_ev <= 0 or a_nm < 0:
        raise ValueError("E and V0 must be positive and the width must not be negative")
    if abs(e_ev - v0_ev) < 1e-12 * v0_ev:
        return 1 / (1 + v0_ev * a_nm ** 2 / (4 * HB2M))                  # exact limit at E = V0
    if e_ev < v0_ev:
        kappa = np.sqrt((v0_ev - e_ev) / HB2M)
        return 1 / (1 + v0_ev ** 2 * np.sinh(kappa * a_nm) ** 2 / (4 * e_ev * (v0_ev - e_ev)))
    k2 = np.sqrt((e_ev - v0_ev) / HB2M)
    return 1 / (1 + v0_ev ** 2 * np.sin(k2 * a_nm) ** 2 / (4 * e_ev * (e_ev - v0_ev)))


def transmission_thick(e_ev, v0_ev, a_nm):
    """Thick-barrier approximation, valid for E below V0 and kappa a above about 1."""
    kappa = np.sqrt((v0_ev - e_ev) / HB2M)
    return 16 * e_ev * (v0_ev - e_ev) / v0_ev ** 2 * np.exp(-2 * kappa * a_nm)


# %% [markdown]
# ## Step 2: a numerical solution as an independent check
# Cut any barrier into thin flat slices, each with its own potential V_j. In slice j the wave
# is a mix of exp(+i k_j x) and exp(-i k_j x) with k_j = sqrt((E - V_j) / HB2M) (an imaginary
# number inside a barrier). Matching the wave and its slope at every interface and chaining the
# slices gives a 2 x 2 transfer matrix M, and the transmission is T = 1 / |M[0, 0]|^2. This works for any
# shape of barrier, and for a single flat slice it must reproduce the exact formula of Step 1.

# %%
def transfer_matrix_t(e_ev, slices):
    """Transmission through slices = [(V_j in eV, width_j in nm), ...] between two free regions (V = 0)."""
    if e_ev <= 0:
        raise ValueError("E must be positive")
    def kk(v):
        d = e_ev - v
        if abs(d) < 1e-9:
            d = 1e-9                                  # avoid a zero wave number at E = V
        return np.sqrt(complex(d / HB2M))
    def dmat(k):
        return np.array([[1, 1], [1j * k, -1j * k]], dtype=complex)
    ks = [kk(0.0)] + [kk(v) for v, _ in slices] + [kk(0.0)]
    m = np.eye(2, dtype=complex)
    for j in range(len(ks) - 1):
        m = m @ np.linalg.solve(dmat(ks[j]), dmat(ks[j + 1]))          # interface j -> j + 1
        if j < len(slices):
            kd = ks[j + 1] * slices[j][1]
            m = m @ np.diag([np.exp(1j * kd), np.exp(-1j * kd)])        # travel through slice j
    return float(1 / abs(m[0, 0]) ** 2)


def wkb_transmission(e_ev, v_of_x, a_nm, n=4000):
    """WKB estimate exp(-2 integral kappa dx) for a smooth barrier V(x) (eV) over 0 < x < a (nm)."""
    x = (np.arange(n) + 0.5) * a_nm / n
    v = np.array([v_of_x(xx) for xx in x])
    kappa = np.sqrt(np.clip(v - e_ev, 0, None) / HB2M)
    return float(np.exp(-2 * kappa.sum() * a_nm / n))


# %% [markdown]
# ## Step 3: how sensitive is a scanning tunnelling microscope?
# Between the tip and the surface the barrier is roughly the work function phi (a few eV) for an electron
# at the top of the metal (E close to 0 relative to the vacuum level: kappa = sqrt(phi / HB2M)). Moving
# the tip by a distance d changes the current by the factor exp(2 kappa d).

# %%
def stm_current_ratio(phi_ev, delta_nm):
    """Factor by which the tunnelling current changes when the gap grows by delta_nm."""
    return float(np.exp(-2 * np.sqrt(phi_ev / HB2M) * delta_nm))


def min_width_nm(e_ev, v0_ev, t_target):
    """Smallest barrier width (nm) with transmission at most t_target (bisection on the exact formula)."""
    lo, hi = 0.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if transmission(e_ev, v0_ev, mid) > t_target:
            lo = mid
        else:
            hi = mid
    return hi


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    e, v0, a = 1.0, 2.0, 0.5
    print(f"hbar^2/2m = {HB2M:.5f} eV nm^2, kappa = {np.sqrt((v0 - e) / HB2M):.3f} 1/nm")
    print(f"exact T = {transmission(e, v0, a):.5f}, thick-barrier T = {transmission_thick(e, v0, a):.5f}, "
          f"transfer matrix T = {transfer_matrix_t(e, [(v0, a)]):.5f}")
    para = lambda x: v0 * (1 - ((x - a / 2) / (a / 2)) ** 2)
    sl = [(para((j + 0.5) * a / 400), a / 400) for j in range(400)]
    print(f"parabolic barrier: transfer matrix {transfer_matrix_t(e, sl):.5f}, WKB {wkb_transmission(e, para, a):.5f}")
    print(f"STM: moving the tip 0.1 nm away (phi = 4.5 eV) changes the current by a factor {stm_current_ratio(4.5, 0.1):.3f} (1 / {1 / stm_current_ratio(4.5, 0.1):.1f})")

    widths = np.linspace(0.02, 1.5, 200)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.semilogy(widths, [transmission(e, v0, x) for x in widths], color="tab:blue", label="exact")
    ax.semilogy(widths, [transmission_thick(e, v0, x) for x in widths], "--", color="tab:red", label="thick-barrier approximation")
    ax.set_ylim(1e-8, 2)
    ax.set_xlabel("barrier width a (nm)")
    ax.set_ylabel("transmission probability T")
    ax.set_title("Tunnelling falls exponentially with the width (E = 1 eV, V0 = 2 eV)")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "transmission_vs_width.png", dpi=120)

    es = np.linspace(0.05, 5, 500)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(es, [transmission(x, 2.0, 0.5) for x in es], color="tab:blue", label="exact")
    ax2.plot(es, [transfer_matrix_t(x, [(2.0, 0.5)]) for x in es], ":", color="black", label="transfer matrix")
    ax2.axvline(2.0, color="gray", ls=":")
    ax2.set_xlabel("electron energy E (eV); the barrier height V0 = 2 eV is dotted")
    ax2.set_ylabel("transmission probability T")
    ax2.set_title("Above the barrier the transmission still oscillates (a = 0.5 nm)")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "transmission_vs_energy.png", dpi=120)

# %% [markdown]
# ## Where this stops
# One dimension, flat or smooth barriers, a steady stream of electrons. Real tunnelling happens in three
# dimensions with many electrons, and the barrier in an STM is not a rectangle. The roadmap follows a
# wave packet in time and compares it with these numbers.
