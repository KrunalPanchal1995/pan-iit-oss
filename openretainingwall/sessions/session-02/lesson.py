"""Session 2 (Level 2): Rankine earth pressure on a smooth vertical wall.

Run:  python start.py 2
Educational only: never use this to design or check a real wall.
"""
# %% [markdown]
# # Session 2: how hard does the soil push?
# **A. Real-world problem.** How big is the sideways push of 4 m of soil on a wall, where
# does it act, and what happens when a car parks behind the wall or the ground fills with water?
#
# **Plan.** (1) the coefficient Ka in two forms, (2) the triangular pressure and its resultant,
# (3) a surcharge, (4) water, (5) a design question, (6) how much Ka depends on phi.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

GAMMA_W = 9.81     # unit weight of water, kN/m^3


# %% [markdown]
# ## Step 1: the active coefficient Ka
# For a smooth vertical wall and level backfill, with soil friction angle phi:
#     Ka = tan^2(45 - phi/2) = (1 - sin phi) / (1 + sin phi).
# For phi = 30 degrees: sin 30 = 0.5, so Ka = 0.5 / 1.5 = 1/3.

# %%
def ka_tan(phi_deg):
    return float(np.tan(np.radians(45.0 - phi_deg / 2.0)) ** 2)


def ka_sin(phi_deg):
    s = np.sin(np.radians(phi_deg))
    return float((1.0 - s) / (1.0 + s))


# %% [markdown]
# ## Step 2: pressure, resultant, arm
# Horizontal pressure at depth z is p = Ka * gamma * z (kPa = kN per square metre). It is a
# triangle from 0 at the top to Ka gamma H at the base. The area of the triangle is the force per
# metre of wall: Pa = 0.5 Ka gamma H^2, acting H/3 above the base.

# %%
def pressure(z, phi, gamma):
    """Horizontal pressure (kPa) at depth z (m) below the surface."""
    return ka_sin(phi) * gamma * np.asarray(z, dtype=float)


def active_force(H, phi, gamma):
    """Resultant Pa in kN per metre run."""
    return 0.5 * ka_sin(phi) * gamma * H ** 2


def surcharge_force(H, phi, q):
    """Extra force Ka q H (kN/m) from a uniform surface load q (kPa); it acts at H/2."""
    return ka_sin(phi) * q * H


def max_height(Pa_limit, phi, gamma):
    """Inverse problem: tallest wall whose soil force stays within Pa_limit (kN/m)."""
    return float(np.sqrt(2.0 * Pa_limit / (ka_sin(phi) * gamma)))


# %% [markdown]
# ## Step 3: water, the warning
# Water pushes with the full hydrostatic pressure gamma_w * z whatever the soil. For a
# backfill that is saturated up to the top, the soil's effective weight drops to
# gamma' = gamma_sat - gamma_w, and the water adds 0.5 gamma_w H^2.

# %%
def saturated_force(H, phi, gamma_sat):
    """Soil (submerged) plus water force, kN/m, for backfill saturated to the top."""
    soil = 0.5 * ka_sin(phi) * (gamma_sat - GAMMA_W) * H ** 2
    water = 0.5 * GAMMA_W * H ** 2
    return soil, water, soil + water


# %% [markdown]
# ## Step 4: see it
# Left: the pressure triangle and its resultant for H = 4 m. Right: Ka against phi, which
# falls steeply: a small error in phi is a big error in the push.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    H, phi, gamma = 4.0, 30.0, 18.0
    print(f"Ka tan form = {ka_tan(30):.4f}, sin form = {ka_sin(30):.4f}")
    print(f"pressure at the base = {float(pressure(H, phi, gamma)):.1f} kPa, Pa = {active_force(H, phi, gamma):.1f} kN/m at {H / 3:.2f} m")
    print(f"surcharge 10 kPa adds {surcharge_force(H, phi, 10):.1f} kN/m")
    so, wa, tot = saturated_force(H, phi, 20.0)
    print(f"saturated: soil {so:.1f} + water {wa:.1f} = {tot:.1f} kN/m  (dry: {active_force(H, phi, gamma):.1f})")
    print(f"phi 25: Ka {ka_sin(25):.4f} Pa {active_force(H, 25, gamma):.1f};  phi 35: Ka {ka_sin(35):.4f} Pa {active_force(H, 35, gamma):.1f}")
    print(f"tallest wall for 60 kN/m: {max_height(60, phi, gamma):.2f} m")

    z = np.linspace(0, H, 50)
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.fill_betweenx(z, 0, pressure(z, phi, gamma), alpha=0.4)
    ax.plot(pressure(z, phi, gamma), z)
    ax.axhline(H - H / 3, color="crimson", ls="--")
    ax.text(1, H - H / 3 - 0.2, "Pa acts at H/3 above the base", color="crimson")
    ax.invert_yaxis()
    ax.set_xlabel("horizontal pressure p (kPa)")
    ax.set_ylabel("depth below the surface z (m)")
    ax.set_title("Triangular pressure: p = Ka gamma z")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "pressure_triangle.png", dpi=120)

    ph = np.linspace(15, 45, 61)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(ph, [ka_sin(p) for p in ph])
    ax2.plot([25, 35], [ka_sin(25), ka_sin(35)], "o")
    ax2.set_xlabel("soil friction angle phi (degrees)")
    ax2.set_ylabel("active coefficient Ka (no unit)")
    ax2.set_title("Ka falls steeply with phi")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "ka_vs_phi.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
