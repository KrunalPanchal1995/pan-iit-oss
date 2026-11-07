"""Session 2 (Level 2): boiling point from the Clausius-Clapeyron relation, and a valve design.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the boiling-point curve from physics
# **A. Real-world problem.** Session 1 read boiling points from a table. Where do the table
# numbers come from, and what valve weight holds a cooker at 100 kPa above the air?
#
# **Safety and scope.** Educational model only. Never modify, block or remove the valves of
# real equipment.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R = 8.314             # gas constant, J/(mol K)
L_MOL = 40700.0       # molar latent heat of vaporisation of water near 100 C, J/mol (about 40.7 kJ/mol)
P_ATM = 101.325       # kPa
T_REF = 373.15        # K, boiling point at P_ATM
G = 9.81              # m/s^2

# Approximate steam-table values (kPa absolute, degrees C) to compare with.
TABLE = [(50.0, 81.3), (101.325, 100.0), (200.0, 120.2), (300.0, 133.5), (400.0, 143.6)]


# %% [markdown]
# ## Step 1: Clausius-Clapeyron
# For a liquid in equilibrium with its vapour, treating the vapour as an ideal gas and the
# latent heat L as constant:
#
#     ln(P2 / P1) = (L / R) * (1/T1 - 1/T2)        (T in kelvin, any pressure unit)
#
# Take (P1, T1) = (101.325 kPa, 373.15 K). Solving for T2 gives the boiling point at P2.

# %%
def boiling_point_k(p_abs_kpa, latent=L_MOL):
    """Boiling point in kelvin at an absolute pressure (kPa), from Clausius-Clapeyron."""
    if p_abs_kpa <= 0:
        raise ValueError("absolute pressure must be positive")
    return 1.0 / (1.0 / T_REF - R * np.log(p_abs_kpa / P_ATM) / latent)


def boiling_point_c(p_abs_kpa, latent=L_MOL):
    return float(boiling_point_k(p_abs_kpa, latent) - 273.15)


def vapour_pressure_kpa(temp_c, latent=L_MOL):
    """The inverse: pressure (kPa absolute) at which water boils at temp_c."""
    return float(P_ATM * np.exp(latent / R * (1.0 / T_REF - 1.0 / (temp_c + 273.15))))


# %% [markdown]
# ## Step 2: gauge versus absolute, and the Q10 rule of thumb
# A gauge reads pressure above the atmosphere: P_abs = P_gauge + 101.325 kPa. The physics
# (boiling point) needs the ABSOLUTE pressure.
#
# Rule of thumb for cooking: rate roughly doubles per 10 degrees C, so
# rate factor = 2^((T - 100) / 10). It is only a rule of thumb.

# %%
def gauge_to_abs(p_gauge_kpa):
    return p_gauge_kpa + P_ATM


def rate_factor(temp_c, q10=2.0):
    return float(q10 ** ((temp_c - 100.0) / 10.0))


# %% [markdown]
# ## Step 3: the weight on the valve (design)
# A weighted valve sits on a small opening of diameter d. It lifts, and steam escapes, when the
# steam pressure force on the opening equals the weight:
#
#     P_gauge * A = m * g       with  A = pi d^2 / 4
#
# so P_gauge = m g / A, and for a wanted gauge pressure the mass is m = P_gauge * A / g.

# %%
def valve_gauge_kpa(mass_kg, diameter_m):
    area = np.pi * diameter_m ** 2 / 4.0
    return float(mass_kg * G / area / 1000.0)


def valve_mass_kg(p_gauge_kpa, diameter_m):
    area = np.pi * diameter_m ** 2 / 4.0
    return float(p_gauge_kpa * 1000.0 * area / G)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    pa = np.linspace(40.0, 420.0, 200)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(pa, [boiling_point_c(x) for x in pa], label="Clausius-Clapeyron (L = 40.7 kJ/mol)")
    ax.plot([p for p, _ in TABLE], [t for _, t in TABLE], "o", label="approximate steam table")
    ax.set_xlabel("absolute pressure (kPa)")
    ax.set_ylabel("boiling point (degrees C)")
    ax.set_title("Boiling point against pressure")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "clausius_clapeyron.png", dpi=120)

    gauge = np.linspace(0.0, 250.0, 100)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for d in (3.0, 4.0, 5.0):
        ax2.plot([valve_mass_kg(g, d / 1000.0) * 1000.0 for g in gauge], gauge, label=f"opening {d:.0f} mm")
    ax2.axhline(100.0, color="red", ls="--", label="100 kPa gauge target")
    ax2.set_xlabel("valve mass (g)")
    ax2.set_ylabel("gauge pressure held (kPa)")
    ax2.set_title("Valve design: mass needed for a gauge pressure")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "valve_design.png", dpi=120)

    print("P_abs (kPa)   CC (C)   table (C)   error (C)")
    for p, t in TABLE:
        print(f"{p:9.1f}   {boiling_point_c(p):7.2f}   {t:7.1f}   {boiling_point_c(p) - t:+7.2f}")
    t100 = boiling_point_c(gauge_to_abs(100.0))
    print(f"gauge 100 kPa -> absolute {gauge_to_abs(100.0):.1f} kPa -> {t100:.2f} C, rate x{rate_factor(t100):.2f}")
    print(f"mass for 100 kPa gauge on a 4 mm opening: {valve_mass_kg(100.0, 0.004) * 1000:.1f} g")

# %% [markdown]
# ## Where this stops
# L is not exactly constant and steam is not exactly ideal, so errors grow far from 100 C.
# Session 3 uses this boiling-point law inside a full heating and cooking simulation.
