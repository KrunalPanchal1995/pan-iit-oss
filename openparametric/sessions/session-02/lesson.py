"""Session 2 (Level 3): two rules compete: strength and stiffness decide the thickness of a cantilever bracket, and the material choice.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: when two rules disagree, the stricter one wins
# **A. Real-world problem.** A bracket sticks out from a wall and carries a load at its tip. It must not break (strength) and it must not sag
# more than a given amount (stiffness). Each requirement gives its own minimum thickness, and the plate that is sold comes in fixed thicknesses.
# Which rule decides, does it change when the bracket gets longer, and is a steel or an aluminium bracket lighter?
#
# Educational model: a flat rectangular plate of width b and thickness t, fixed at one end (a cantilever) with a load F at the free end,
# elastic material. Not a design code: no stress concentration at the fixing, no buckling, no fatigue.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
MATERIALS = {"steel": {"E": 210000.0, "yield": 235.0, "rho": 7850.0},          # E and yield in MPa, rho in kg/m^3
             "aluminium": {"E": 69000.0, "yield": 240.0, "rho": 2700.0}}
PLATES = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]                              # thicknesses that are sold (mm)


# %% [markdown]
# ## Step 1: the two rules
# For a load F at distance L from the fixing of a plate of width b and thickness t (second moment of area I = b t^3 / 12):
#
#     strength:   the largest stress is at the fixing, sigma = M c / I = 6 F L / (b t^2).   Require sigma <= sigma_allow = yield / SF.
#                 t >= t_strength = sqrt(6 F L / (b sigma_allow))
#     stiffness:  the tip sinks by delta = F L^3 / (3 E I) = 4 F L^3 / (E b t^3).           Require delta <= delta_max.
#                 t >= t_stiffness = (4 F L^3 / (E b delta_max))^(1/3)
#
# Units: N, mm, MPa (= N/mm^2). The plate must satisfy both, so the required thickness is the larger of the two, and the rule that gives the larger one
# is the governing rule.

# %%
def t_strength(force_n, length_mm, width_mm, allow_mpa):
    if min(force_n, length_mm, width_mm, allow_mpa) <= 0:
        raise ValueError("force, length, width and allowable stress must be positive")
    return math.sqrt(6 * force_n * length_mm / (width_mm * allow_mpa))


def t_stiffness(force_n, length_mm, width_mm, e_mpa, delta_max_mm):
    if min(force_n, length_mm, width_mm, e_mpa, delta_max_mm) <= 0:
        raise ValueError("force, length, width, modulus and allowed deflection must be positive")
    return (4 * force_n * length_mm ** 3 / (e_mpa * width_mm * delta_max_mm)) ** (1 / 3)


def tip_deflection(force_n, length_mm, width_mm, thickness_mm, e_mpa):
    return 4 * force_n * length_mm ** 3 / (e_mpa * width_mm * thickness_mm ** 3)


def max_stress(force_n, length_mm, width_mm, thickness_mm):
    return 6 * force_n * length_mm / (width_mm * thickness_mm ** 2)


# %% [markdown]
# ## Step 2: the rule engine for one material
# Compute both thicknesses, take the larger, then round up to the next plate that is sold. Finally check the plate we really have: its
# stress, its deflection and its mass. A rule set like this is a small program that turns requirements into a part.

# %%
def next_plate(t_mm):
    for p in PLATES:
        if p >= t_mm * (1 - 1e-12):
            return p
    raise ValueError("no plate is thick enough: change the width, the length or the requirement")


def design(force_n, length_mm, width_mm, delta_max_mm, material="steel", safety_factor=1.5):
    if material not in MATERIALS:
        raise ValueError(f"unknown material '{material}'")
    if safety_factor < 1:
        raise ValueError("the safety factor must be at least 1")
    m = MATERIALS[material]
    allow = m["yield"] / safety_factor
    ts = t_strength(force_n, length_mm, width_mm, allow)
    tf = t_stiffness(force_n, length_mm, width_mm, m["E"], delta_max_mm)
    t_req = max(ts, tf)
    t = next_plate(t_req)
    return {"material": material, "t_strength": ts, "t_stiffness": tf, "governing": "strength" if ts >= tf else "stiffness",
            "t_required": t_req, "t": t, "stress": max_stress(force_n, length_mm, width_mm, t),
            "delta": tip_deflection(force_n, length_mm, width_mm, t, m["E"]), "sf_actual": m["yield"] / max_stress(force_n, length_mm, width_mm, t),
            "mass": width_mm * t * length_mm * m["rho"] * 1e-9}


# %% [markdown]
# ## Step 3: the governing rule changes with the length, and the lightest material
# Strength needs t proportional to sqrt(L) and stiffness needs t proportional to L, so the stiffness rule wins for long brackets and the strength rule for short ones. They meet at the critical length
#
#     L_c = [ (6 F / (b sigma_allow))^(3/2) E b delta_max / (4 F) ]^(2/3)
#
# Different materials need different thicknesses, so we run the same rules for each material and choose the one with the smallest mass. To check that the deflection formula is right we also
# integrate the beam equation E I y'' = M(x) = F (L - x) numerically, twice, along the plate.

# %%
def critical_length(force_n, width_mm, e_mpa, allow_mpa, delta_max_mm):
    return ((6 * force_n / (width_mm * allow_mpa)) ** 1.5 * e_mpa * width_mm * delta_max_mm / (4 * force_n)) ** (2 / 3)


def lightest(force_n, length_mm, width_mm, delta_max_mm, safety_factor=1.5):
    """Run the rules for every material and return (best, all results) by smallest mass."""
    results = {name: design(force_n, length_mm, width_mm, delta_max_mm, name, safety_factor) for name in MATERIALS}
    return min(results.values(), key=lambda r: r["mass"]), results


def tip_deflection_numeric(force_n, length_mm, width_mm, thickness_mm, e_mpa, n=4000):
    """Integrate E I y'' = F (L - x) twice from the fixed end with the trapezoid rule. Returns y(L) in mm."""
    x = np.linspace(0, length_mm, n + 1)
    ei = e_mpa * width_mm * thickness_mm ** 3 / 12
    curvature = force_n * (length_mm - x) / ei
    slope = np.concatenate([[0], np.cumsum((curvature[1:] + curvature[:-1]) / 2 * np.diff(x))])
    return float(np.sum((slope[1:] + slope[:-1]) / 2 * np.diff(x)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for mat in MATERIALS:
        r = design(500, 200, 40, 1.0, mat)
        print(f"{mat}: t_strength {r['t_strength']:.2f}, t_stiffness {r['t_stiffness']:.2f} -> {r['governing']} governs, plate {r['t']} mm, mass {r['mass']:.3f} kg, "
              f"stress {r['stress']:.0f} MPa, deflection {r['delta']:.2f} mm")
    best, _ = lightest(500, 200, 40, 1.0)
    print("lightest:", best["material"])
    print(f"critical length for steel: {critical_length(500, 40, 210000, 235 / 1.5, 1.0):.0f} mm")
    print(f"numeric tip deflection {tip_deflection_numeric(500, 200, 40, 12, 210000):.5f} mm, formula {tip_deflection(500, 200, 40, 12, 210000):.5f} mm")

    ls = np.linspace(40, 500, 93)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    st = MATERIALS["steel"]
    ax.plot(ls, [t_strength(500, x, 40, st["yield"] / 1.5) for x in ls], color="tab:blue", label="strength rule")
    ax.plot(ls, [t_stiffness(500, x, 40, st["E"], 1.0) for x in ls], color="tab:red", label="stiffness rule")
    ax.plot(ls, [max(t_strength(500, x, 40, st["yield"] / 1.5), t_stiffness(500, x, 40, st["E"], 1.0)) for x in ls], "k--", lw=1, label="required (the larger)")
    ax.axvline(critical_length(500, 40, st["E"], st["yield"] / 1.5, 1.0), color="0.5", ls=":")
    ax.set_xlabel("bracket length L (mm)")
    ax.set_ylabel("thickness (mm)")
    ax.set_title("Steel bracket, F = 500 N, width 40 mm, at most 1 mm sag")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "thickness_vs_length.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for name, col in (("steel", "tab:blue"), ("aluminium", "tab:green")):
        masses = []
        for x in ls:
            try:
                masses.append(design(500, x, 40, 1.0, name)["mass"])
            except ValueError:                       # no plate that is sold is thick enough
                masses.append(np.nan)
        ax2.plot(ls, masses, "o-", ms=3, color=col, label=name)
    ax2.set_xlabel("bracket length L (mm)")
    ax2.set_ylabel("mass of the bracket (kg)")
    ax2.set_title("Mass of the standard plate for each material")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "mass_by_material.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The rules here are written in the code, in a fixed order. A real part has dozens of rules that depend on each other, and they should be data that a program can sort, check and change.
# Session 3 stores the rules as text, finds the order in which they must be evaluated, rejects circular rules, and draws the part they generate.
