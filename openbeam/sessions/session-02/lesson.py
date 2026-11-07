"""Session 2 (Level 2): stiffness and strength of a beam: I, deflection, bending stress, and a design.

Run:  python start.py 2
Educational model only (small deflections, straight elastic beam). Never use it to design a real structure.
"""
# %% [markdown]
# # Session 2: how stiff, how strong, how light?
# **A. Real-world problem.** Two planks of the same wood and the same width span a stream.
# One lies flat, the other stands on edge. The one on edge hardly bends. Why, when both
# contain the same amount of wood? And if a building code says the beam may sag at most
# L/360 and the wood may not be stressed beyond a limit, what is the lightest beam that passes?
#
# **Plan.** (1) second moment of area I of a rectangle and an I-section, (2) deflection of a
# point-loaded beam, (3) bending stress, (4) search for the lightest section that passes.
# Units: N, m, Pa inside the functions; the printouts convert to mm and MPa.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
RHO = 7850.0     # steel density, kg/m^3 (used for mass per metre)


# %% [markdown]
# ## Step 1: the second moment of area I
# Material far from the middle line (the *neutral axis*) resists bending much more than material
# near it, because each small piece of area dA counts as y^2 dA.
#
#     rectangle b wide, h deep:   I = b h^3 / 12
#     I-section (flanges bf x tf, web tw, depth h):   I = [ bf h^3 - (bf - tw)(h - 2 tf)^3 ] / 12
#
# Depth enters as h^3: doubling the depth multiplies I by 8, doubling the width only by 2.

# %%
def I_rect(b, h):
    """Second moment of area of a solid rectangle, m^4 (b, h in m)."""
    return b * h ** 3 / 12.0


def I_isection(bf, tf, tw, h):
    """Second moment of area of a symmetric I-section, m^4 (all lengths in m)."""
    return (bf * h ** 3 - (bf - tw) * (h - 2 * tf) ** 3) / 12.0


def area_isection(bf, tf, tw, h):
    return 2 * bf * tf + tw * (h - 2 * tf)


# %% [markdown]
# ## Step 2: deflection of a point-loaded, simply supported beam
# With load P at distance a from the left support (b = L - a), E the modulus (Pa) and I (m^4),
# the curve (Euler-Bernoulli beam theory, small deflections) is, for x <= a:
#
#     v(x) = P b x (L^2 - b^2 - x^2) / (6 E I L)
#
# and for x > a the same formula with x measured from the right support and a and b swapped.
# For a centred load the maximum is  v_max = P L^3 / (48 E I)  at mid-span.

# %%
def deflection(x, P, a, L, E, I):
    """Downward deflection v(x) in m of a simply supported beam with a point load."""
    x = np.asarray(x, dtype=float)
    b = L - a
    left = P * b * x * (L ** 2 - b ** 2 - x ** 2) / (6 * E * I * L)
    xr = L - x
    right = P * a * xr * (L ** 2 - a ** 2 - xr ** 2) / (6 * E * I * L)
    return np.where(x <= a, left, right)


def max_deflection(P, a, L, E, I, n=2001):
    x = np.linspace(0, L, n)
    return float(deflection(x, P, a, L, E, I).max())


def centre_deflection(P, L, E, I):
    return P * L ** 3 / (48 * E * I)


# %% [markdown]
# ## Step 3: bending stress
# The bending moment M makes the top fibres squash and the bottom fibres stretch. At a distance
# y from the neutral axis the stress is sigma = M y / I. The largest value is at y = h / 2:
#
#     sigma_max = M_max (h/2) / I,      M_max = P a b / L.

# %%
def moment_max(P, a, L):
    return P * a * (L - a) / L


def bending_stress(M, y, I):
    """Stress in Pa at distance y (m) from the neutral axis."""
    return M * y / I


# %% [markdown]
# ## Step 4: the design problem
# Pass two tests: deflection <= L/360 and stress <= allowable. Among passing rectangles of
# fixed width, the lightest is the shallowest one that passes (mass per metre = rho * area).

# %%
def check_rect(P, a, L, E, b, h, sigma_allow, ratio=360.0):
    I = I_rect(b, h)
    d = max_deflection(P, a, L, E, I)
    s = bending_stress(moment_max(P, a, L), h / 2, I)
    return d, s, (d <= L / ratio and s <= sigma_allow)


def lightest_rect(P, a, L, E, b, sigma_allow, ratio=360.0):
    """Smallest depth h (m, steps of 1 mm) of a rectangle of width b that passes both tests."""
    for mm in range(10, 1500):
        h = mm / 1000.0
        if check_rect(P, a, L, E, b, h, sigma_allow, ratio)[2]:
            return h
    return None


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    P, L, E = 10e3, 4.0, 10e9             # N, m, Pa (timber-like)
    b, h = 0.100, 0.200
    I = I_rect(b, h)
    d = centre_deflection(P, L, E, I)
    s = bending_stress(P * L / 4, h / 2, I)
    print(f"I = {I * 1e12:.4g} mm^4, centre deflection {d * 1e3:.2f} mm, limit L/360 = {L / 360 * 1e3:.2f} mm, stress {s / 1e6:.2f} MPa")
    print("flat vs on edge, 100 x 200 mm: I ratio =", round(I_rect(0.1, 0.2) / I_rect(0.2, 0.1), 2))
    print("+20% area as depth: I x", round(I_rect(0.1, 0.24) / I, 3), " as width: I x", round(I_rect(0.12, 0.2) / I, 3))
    hh = lightest_rect(P, L / 2, L, E, b, 12e6)
    print(f"lightest 100 mm wide rectangle: h = {hh * 1e3:.0f} mm", check_rect(P, L / 2, L, E, b, hh, 12e6))

    x = np.linspace(0, L, 401)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for a, c in ((1.0, "tab:orange"), (2.0, "tab:blue")):
        ax[0].plot(x, -1e3 * deflection(x, P, a, L, E, I), c, label=f"load at {a:g} m")
    ax[0].axhline(-1e3 * L / 360, color="r", ls="--", label="limit L/360")
    ax[0].set_xlabel("position along the beam x (m)")
    ax[0].set_ylabel("deflection (mm, downward is negative)")
    ax[0].set_title("Deflected shape, 100 x 200 mm timber")
    ax[0].grid(alpha=0.3)
    ax[0].legend(fontsize=8)
    hs = np.arange(0.12, 0.40, 0.005)
    dd = [1e3 * centre_deflection(P, L, E, I_rect(b, q)) for q in hs]
    ss = [bending_stress(P * L / 4, q / 2, I_rect(b, q)) / 1e6 for q in hs]
    ax[1].plot(hs * 1e3, dd, label="deflection (mm)")
    ax[1].plot(hs * 1e3, ss, label="max stress (MPa)")
    ax[1].axhline(L / 360 * 1e3, color="r", ls="--", label="deflection limit 11.1 mm")
    ax[1].axhline(12, color="g", ls=":", label="stress limit 12 MPa")
    ax[1].axvline(hh * 1e3, color="k", lw=0.8)
    ax[1].set_xlabel("beam depth h (mm), width 100 mm")
    ax[1].set_ylabel("deflection (mm) or stress (MPa)")
    ax[1].set_title("Deeper beams are much stiffer")
    ax[1].set_ylim(0, 30)
    ax[1].grid(alpha=0.3)
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "deflection_design.png", dpi=120)

    # I-section vs rectangle of the same area
    bf, tf, tw, H = 0.100, 0.010, 0.006, 0.200
    A = area_isection(bf, tf, tw, H)
    Ii = I_isection(bf, tf, tw, H)
    wr = A / H                      # solid rectangle with the same area AND the same depth
    Ir = I_rect(wr, H)
    print(f"I-section area {A * 1e6:.0f} mm^2, I {Ii * 1e12:.4g} mm^4; solid rectangle of same area and depth (width {wr * 1e3:.1f} mm) I {Ir * 1e12:.4g} mm^4; ratio {Ii / Ir:.2f}")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(["solid rectangle", "I-section"], [Ir * 1e12 / 1e6, Ii * 1e12 / 1e6], color=["tab:gray", "tab:blue"])
    ax2.set_ylabel("second moment of area I (10^6 mm^4)")
    ax2.set_title(f"Same area and depth: material far from the axis wins")
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "section_shapes.png", dpi=120)

# %% [markdown]
# ## Where this stops
# We used one load and a formula. Real beams carry distributed loads, change section along
# their length and meet many load cases. Session 3 solves those numerically and checks the
# solver against the formulas you just used.
