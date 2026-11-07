"""Session 2 (Level 2): Basquin's law, mean stress (Goodman), notches (K_t) and a shaft design.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the S-N curve as an equation, and what shifts it
# **A. Real-world problem.** A shaft carries a pulley load and turns at 1500 revolutions per
# minute (25 revolutions per second). Every revolution puts each surface point through one full
# pull-push cycle, so about 11 hours of running make a million cycles. What diameter keeps the shaft safe for 10^6 cycles
# and beyond, with a margin? On the way we meet two things that shorten life: a *mean* stress
# and a *notch* such as a hole or a sharp shoulder. All numbers are illustrative and the model
# is simplified; it is not for designing real parts.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

SU = 600.0     # ultimate strength, MPa (illustrative steel)
SE = 300.0     # endurance limit of a small polished test bar, MPa


# %% [markdown]
# ## Step 1: Basquin's relation for any part
# `S_a = A * N**b` through two anchors: `f*S_u` at 1000 cycles (f = 0.9) and the endurance limit
# `S_e` at 10^6 cycles. Then `b = -log10(f*S_u / S_e) / 3` and `A = (f*S_u)^2 / S_e`.
# A real part has a lower endurance limit than a polished test bar (rough surface, larger size);
# we pass that lower value in as `se`.

# %%
def basquin_constants(su=SU, se=SE, f=0.9):
    """Return (A, b) of S_a = A * N**b for ultimate strength su and endurance limit se (MPa)."""
    b = -np.log10(f * su / se) / 3.0
    a = (f * su) ** 2 / se
    return a, b


def life(sa, su=SU, se=SE):
    """Cycles to failure at fully reversed amplitude sa (MPa); inf at or below the endurance limit."""
    if sa <= se:
        return np.inf
    a, b = basquin_constants(su, se)
    return float((sa / a) ** (1.0 / b))


def stress_for_life(n, su=SU, se=SE):
    """Amplitude (MPa) that gives exactly n cycles (1e3 <= n <= 1e6 is where the line is anchored)."""
    a, b = basquin_constants(su, se)
    return float(a * n ** b)


# %% [markdown]
# ## Step 2: mean stress and the Goodman line
# A load that swings between 0 and a maximum has a mean as well as an amplitude. A tensile mean
# opens cracks and shortens life. The Goodman line joins `S_e` (on the amplitude axis) and `S_u`
# (on the mean axis):
#
#     S_a / S_e + S_m / S_u = 1
#
# A point below the line is "safe for indefinite life" in this model. To use the S-N curve with
# a mean stress, convert to an equivalent fully reversed amplitude:
# `S_eq = S_a / (1 - S_m / S_u)`.

# %%
def goodman_sum(sa, sm, su=SU, se=SE):
    """S_a/S_e + S_m/S_u. Less than 1: indefinite life predicted; equal to 1: on the line."""
    return sa / se + sm / su


def equivalent_amplitude(sa, sm, su=SU):
    """Fully reversed amplitude with the same damage as (sa, sm), by Goodman. Needs sm < su."""
    if sm >= su:
        raise ValueError("mean stress must be below the ultimate strength")
    return sa / (1.0 - sm / su)


def life_with_mean(sa, sm, su=SU, se=SE):
    """Cycles to failure for amplitude sa and mean sm, using Goodman and Basquin."""
    return life(equivalent_amplitude(sa, sm, su), su, se)


# %% [markdown]
# ## Step 3: a notch raises the local stress (K_t)
# Near a hole or a sharp corner the stress is higher than the nominal value `S_nom = F / A_net`
# by a *stress concentration factor* `K_t`, so `S_local = K_t * S_nom`. For a small hole in a
# wide plate pulled in one direction the exact elastic result (Kirsch) for the stress around the
# edge is `S_theta = S * (1 - 2 cos 2 theta)`, where theta is measured from the load direction.
# The largest value, at theta = 90 degrees, is 3 S. So K_t = 3 for a hole in a wide plate. We
# apply K_t to both amplitude and mean (a simple, conservative choice; real designs use a
# smaller fatigue notch factor K_f).

# %%
def hole_hoop_stress(theta_deg, r_over_a=1.0, sigma=1.0):
    """Kirsch hoop stress at polar position (r/a, theta) for a hole of radius a in a wide plate
    under uniaxial stress sigma along theta = 0."""
    th = np.radians(theta_deg)
    q = 1.0 / r_over_a ** 2
    return sigma / 2 * (1 + q) - sigma / 2 * (1 + 3 * q * q) * np.cos(2 * th)


def stress_concentration_hole():
    """K_t of a hole in a wide plate: maximum hoop stress at the edge divided by the nominal stress."""
    theta = np.linspace(0, 180, 3601)
    return float(hole_hoop_stress(theta).max())


def life_with_notch(sa_nom, sm_nom, kt, su=SU, se=SE):
    """Life when the nominal amplitude and mean are both magnified by kt."""
    return life_with_mean(kt * sa_nom, kt * sm_nom, su, se)


# %% [markdown]
# ## Step 4: design a rotating shaft
# A shaft under a steady bending moment M that turns sees a fully reversed surface stress of
# amplitude `S_a = 32 M / (pi d^3)` (d in metres, M in N m, result in Pa). To survive 10^6 cycles
# and beyond with a safety factor `n` on stress, require `K_t * S_a <= S_e,part / n`, so
# `d = (32 M n K_t / (pi S_e,part))^(1/3)`. The part endurance limit is lower than the test bar's:
# we use S_e,part = 0.7 * S_e for surface finish and size (an illustrative factor).

# %%
def bending_stress_mpa(moment_nm, d_m):
    """Surface bending stress amplitude (MPa) of a round shaft of diameter d_m (m)."""
    return 32.0 * moment_nm / (np.pi * d_m ** 3) / 1e6


def design_diameter_mm(moment_nm, n=2.0, kt=1.0, se_part=0.7 * SE):
    """Smallest diameter (mm) with safety factor n on stress at the endurance limit."""
    d = (32.0 * moment_nm * n * kt / (np.pi * se_part * 1e6)) ** (1.0 / 3.0)
    return d * 1000.0


def shaft_life(moment_nm, d_mm, kt=1.0, su=SU, se_part=0.7 * SE):
    """Cycles to failure of the shaft (inf if below the part endurance limit)."""
    return life(kt * bending_stress_mpa(moment_nm, d_mm / 1000.0), su, se_part)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    a, b = basquin_constants()
    n = np.logspace(3, 7, 200)
    fig, ax = plt.subplots(figsize=(6.5, 4.4))
    ax.loglog(n, np.where(n < 1e6, a * n ** b, SE), label="Basquin line, polished bar")
    a2, b2 = basquin_constants(SU, 0.7 * SE)
    ax.loglog(n, np.where(n < 1e6, a2 * n ** b2, 0.7 * SE), "--", label="same steel, real part (S_e x 0.7)")
    ax.set_xlabel("cycles to failure N")
    ax.set_ylabel("stress amplitude S_a (MPa)")
    ax.set_title(f"Log-log S-N curve: slope b = {b:.3f} (bar), {b2:.3f} (part)")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "sn_loglog.png", dpi=120)

    sm = np.linspace(0, SU, 100)
    fig2, ax2 = plt.subplots(figsize=(6, 4.2))
    ax2.plot(sm, SE * (1 - sm / SU), label="Goodman line")
    ax2.fill_between(sm, 0, SE * (1 - sm / SU), alpha=0.15, label="indefinite life predicted")
    ax2.plot([150], [100], "ko")
    ax2.annotate("(150, 100): sum = %.2f" % goodman_sum(100, 150), (150, 100), textcoords="offset points", xytext=(8, 8), fontsize=8)
    ax2.set_xlabel("mean stress S_m (MPa)")
    ax2.set_ylabel("stress amplitude S_a (MPa)")
    ax2.set_title("Goodman diagram")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "goodman.png", dpi=120)

    th = np.linspace(0, 180, 361)
    fig3, ax3 = plt.subplots(figsize=(6, 4.0))
    ax3.plot(th, hole_hoop_stress(th), label="edge of the hole (r = a)")
    ax3.plot(th, hole_hoop_stress(th, 2.0), label="r = 2a")
    ax3.axhline(1, color="gray", ls=":")
    ax3.set_xlabel("angle from the load direction (degrees)")
    ax3.set_ylabel("hoop stress / nominal stress")
    ax3.set_title("Hole in a wide plate: peak 3 at 90 degrees")
    ax3.grid(alpha=0.3)
    ax3.legend(fontsize=8)
    fig3.tight_layout()
    fig3.savefig(OUT / "hole_stress.png", dpi=120)

    print(f"Kt of a hole = {stress_concentration_hole():.3f}")
    print(f"b (bar) = {b:.4f}, b (part) = {b2:.4f}")
    print(f"Goodman sum at (Sa, Sm) = (100, 150): {goodman_sum(100, 150):.3f}")
    for kt in (1.0, 2.0):
        print(f"design diameter M = 200 N m, n = 2, Kt = {kt}: {design_diameter_mm(200, 2, kt):.2f} mm")
    print(f"27 mm shaft stress = {bending_stress_mpa(200, 0.027):.1f} MPa")
    print(f"20 mm shaft life = {shaft_life(200, 20):,.0f} cycles")

# %% [markdown]
# ## Where this stops
# Real endurance limits come from tests of the actual part. Aluminium has no true endurance
# limit. Variable loads need counting and adding up damage: Session 3.
