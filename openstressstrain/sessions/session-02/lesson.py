"""Session 2 (Level 2): Hooke's law, factor of safety and a material-and-diameter design problem.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: Hooke's law and choosing a safe bar
# **A. Real-world problem.** A 20 kN load (about 2 tonnes) hangs from a 2 m rod. The rod may
# stretch by at most 1 mm and must have a factor of safety of 2 against yielding. Which material
# and which diameter?
#
# **Plan.** (1) Hooke's law, (2) the material table, (3) two limits: strength and stiffness,
# (4) pick the lightest bar that passes both.
#
# *Values below are round textbook-typical numbers for teaching. They are NOT design data;
# real alloys and tempers differ by large amounts. This is not a design tool.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# name: (E in MPa, yield in MPa, ultimate in MPa, density in kg/m^3)  -- typical, rounded
MATERIALS = {
    "steel (mild)": (200000.0, 250.0, 400.0, 7850.0),
    "aluminium alloy": (70000.0, 240.0, 290.0, 2700.0),
    "copper (annealed)": (110000.0, 70.0, 220.0, 8900.0),
    "polymer (nylon-like)": (2500.0, 50.0, 70.0, 1150.0),
}
LOAD_KN, LENGTH_MM, MAX_EXT_MM, FOS_REQ = 20.0, 2000.0, 1.0, 2.0


# %% [markdown]
# ## Step 1: Hooke's law
# In the elastic range stress is proportional to strain: **sigma = E * eps**. E (Young's modulus)
# is the stiffness of the material, in MPa (1 GPa = 1000 MPa). Combine with sigma = F/A and
# eps = dL/L:
#
#     dL = F * L / (A * E)        (extension of a bar under a pull F)
#
# Stiffness is E, not yield strength: steel and aluminium alloys can yield at similar stress, but
# steel stretches about three times less (E = 200 GPa against 70 GPa).

# %%
def area_circle(d_mm):
    return np.pi * d_mm ** 2 / 4.0


def stress(force_kn, d_mm):
    """MPa."""
    return force_kn * 1000.0 / area_circle(d_mm)


def extension(force_kn, length_mm, d_mm, e_mpa):
    """dL = F L / (A E), in mm."""
    return force_kn * 1000.0 * length_mm / (area_circle(d_mm) * e_mpa)


def factor_of_safety(sy_mpa, stress_mpa):
    """How many times larger the stress would have to be to reach yield."""
    return sy_mpa / stress_mpa


# %% [markdown]
# ## Step 2: the two limits give two minimum areas
# * Strength: stress <= yield / FoS  ->  A >= F * FoS / yield
# * Stiffness: dL <= dL_max  ->  A >= F * L / (E * dL_max)
#
# The bar must satisfy both, so the larger area wins. The diameter follows from A = pi d^2 / 4.

# %%
def diameter_from_area(a_mm2):
    return float(np.sqrt(4.0 * a_mm2 / np.pi))


def min_area_strength(force_kn, sy, fos=FOS_REQ):
    return force_kn * 1000.0 * fos / sy


def min_area_stiffness(force_kn, length_mm, e, dl_max=MAX_EXT_MM):
    return force_kn * 1000.0 * length_mm / (e * dl_max)


def design(name, force_kn=LOAD_KN, length_mm=LENGTH_MM, dl_max=MAX_EXT_MM, fos=FOS_REQ):
    """Smallest whole-millimetre diameter that passes both limits, and the mass of the bar."""
    e, sy, su, rho = MATERIALS[name]
    a_s = min_area_strength(force_kn, sy, fos)
    a_k = min_area_stiffness(force_kn, length_mm, e, dl_max)
    d_min = diameter_from_area(max(a_s, a_k))
    d = float(np.ceil(d_min))
    mass = rho * area_circle(d) * 1e-6 * length_mm * 1e-3   # mm^2 -> m^2, mm -> m
    return {"name": name, "d_strength": diameter_from_area(a_s), "d_stiffness": diameter_from_area(a_k),
            "limit": "strength" if a_s >= a_k else "stiffness", "d": d, "mass": mass,
            "stress": stress(force_kn, d), "ext": extension(force_kn, length_mm, d, e),
            "fos": factor_of_safety(sy, stress(force_kn, d))}


def best_design(**kw):
    rows = [design(n, **kw) for n in MATERIALS]
    return min(rows, key=lambda r: r["mass"]), rows


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    best, rows = best_design()
    print(f"{'material':22s} {'d_str':>7s} {'d_stiff':>8s} {'limit':>9s} {'d':>4s} {'mass kg':>8s} {'ext mm':>7s} {'FoS':>5s}")
    for r in rows:
        print(f"{r['name']:22s} {r['d_strength']:7.2f} {r['d_stiffness']:8.2f} {r['limit']:>9s} {r['d']:4.0f} "
              f"{r['mass']:8.2f} {r['ext']:7.3f} {r['fos']:5.2f}")
    print("lightest passing bar:", best["name"], f"d = {best['d']:.0f} mm, mass {best['mass']:.2f} kg")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for name, (e, sy, su, rho) in MATERIALS.items():
        ey = sy / e
        ax.plot([0, ey * 100], [0, sy], marker="o", ms=4, label=f"{name}, E = {e / 1000:g} GPa")
    ax.set_xlim(0, 3)
    ax.set_xlabel("strain (percent)")
    ax.set_ylabel("stress (MPa)")
    ax.set_title("Hooke's law: the slope is E (elastic part only, ends at yield)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "hooke_lines.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    x = np.arange(len(rows))
    ax2.bar(x - 0.2, [r["d_strength"] for r in rows], 0.4, label="needed for strength (FoS 2)")
    ax2.bar(x + 0.2, [r["d_stiffness"] for r in rows], 0.4, label="needed for stiffness (1 mm)")
    ax2.set_xticks(x)
    ax2.set_xticklabels([r["name"].split(" (")[0] for r in rows], fontsize=8)
    ax2.set_yscale("log")
    ax2.set_ylabel("minimum diameter (mm, log scale)")
    ax2.set_title("Which limit governs? 20 kN, 2 m, 1 mm, FoS 2")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "design_diameters.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# A real design checks buckling, joints, fatigue, temperature and the code rules, and uses
# certified material data. This lesson shows only the logic of two limits.
