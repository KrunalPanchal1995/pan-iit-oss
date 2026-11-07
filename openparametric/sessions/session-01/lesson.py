"""Session 1 (Level 2): a rule turns requirements into a part: the diameter of a shaft, rounded up to a preferred size.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: from a requirement to a size, by a rule
# **A. Real-world problem.** A motor must turn a machine with a torque of 200 N m. What diameter should the steel shaft have?
# A designer does not guess: there is a rule that links the torque, the strength of the steel and a safety margin to the smallest
# safe diameter, and a second rule that rounds it up to a size that can really be bought. If the requirement changes, the rules give a new
# part at once. How do such rules work, and how do we know the shaft is safe?
#
# Educational model: a solid round shaft in pure torsion (twisting) and nothing else. Not a design code; real shafts also bend,
# carry keyways and fatigue.

# %%
import math
import pathlib

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SHEAR_FRACTION = 0.577      # shear yield strength is about 0.577 times the tensile yield strength (von Mises)


# %% [markdown]
# ## Step 1: the stress rule
# When a solid round shaft of diameter d carries a torque T, the largest shear stress is at its surface:
#
#     tau = 16 T / (pi d^3)          (T in N mm, d in mm, tau in MPa = N/mm^2)
#
# The material may be loaded only to an allowable stress: the shear yield strength divided by a safety factor SF,
# tau_allow = 0.577 sigma_y / SF. Setting tau = tau_allow and solving for d gives the smallest safe diameter:
#
#     d_min = (16 T / (pi tau_allow))^(1/3)

# %%
def allowable_shear(yield_mpa, safety_factor):
    if yield_mpa <= 0 or safety_factor < 1:
        raise ValueError("the yield strength must be positive and the safety factor at least 1")
    return SHEAR_FRACTION * yield_mpa / safety_factor


def shear_stress(torque_nm, diameter_mm):
    """Largest shear stress (MPa) at the surface of a solid round shaft."""
    if torque_nm < 0 or diameter_mm <= 0:
        raise ValueError("the torque must not be negative and the diameter must be positive")
    return 16 * torque_nm * 1000 / (math.pi * diameter_mm ** 3)


def min_diameter(torque_nm, yield_mpa, safety_factor):
    """Smallest diameter (mm) for which the shear stress stays within the allowable value."""
    if torque_nm <= 0:
        raise ValueError("the torque must be positive")
    tau = allowable_shear(yield_mpa, safety_factor)
    return (16 * torque_nm * 1000 / (math.pi * tau)) ** (1 / 3)


# %% [markdown]
# ## Step 2: rounding up to a preferred size
# Shafts are sold in standard sizes. The preferred-number series R10 spaces sizes by a constant factor of 10^(1/10) = 1.259, rounded
# to convenient numbers: 1, 1.25, 1.6, 2, 2.5, 3.15, 4, 5, 6.3, 8, then the same times 10, 100 and so on. A second rule picks the
# smallest standard size that is **not smaller** than d_min (rounding down would break the safety margin).

# %%
R10 = [1.0, 1.25, 1.6, 2.0, 2.5, 3.15, 4.0, 5.0, 6.3, 8.0]


def preferred_sizes(lo=1.0, hi=1000.0):
    """All R10 sizes from lo to hi (mm)."""
    out, decade = [], 1.0
    while decade <= hi:
        out += [round(x * decade, 6) for x in R10 if lo <= x * decade <= hi]
        decade *= 10
    return out


def next_preferred(d_mm):
    """Smallest R10 size that is at least d_mm."""
    if d_mm <= 0:
        raise ValueError("the diameter must be positive")
    for size in preferred_sizes(0.1, 100000):
        if size >= d_mm * (1 - 1e-12):
            return size
    raise ValueError("no standard size is large enough")


# %% [markdown]
# ## Step 3: the rule chain, and a check of what we got
# Put the rules together: the requirement (torque, material, safety factor) gives d_min, the second rule gives the standard size, and a last step
# computes what we really have: the stress in the chosen shaft and the safety factor it gives, which is a little above the one we asked for.
# For a motor we are usually given power P (kW) and speed n (rpm) instead of the torque: T = 9549 P / n (N m).

# %%
def torque_from_power(power_kw, rpm):
    if power_kw <= 0 or rpm <= 0:
        raise ValueError("the power and the speed must be positive")
    return 9549.0 * power_kw / rpm


def design_shaft(torque_nm, yield_mpa=350.0, safety_factor=2.5):
    """Apply the rules: d_min, then the standard size, then check. Returns a dictionary."""
    d_min = min_diameter(torque_nm, yield_mpa, safety_factor)
    d = next_preferred(d_min)
    tau = shear_stress(torque_nm, d)
    return {"torque": torque_nm, "d_min": d_min, "d": d, "tau": tau,
            "sf_actual": SHEAR_FRACTION * yield_mpa / tau, "margin": d / d_min - 1,
            "mass_per_m": 7850 * math.pi / 4 * (d / 1000) ** 2}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    s = design_shaft(200.0)
    print(f"T = 200 N m, yield 350 MPa, SF 2.5: tau_allow = {allowable_shear(350, 2.5):.1f} MPa, d_min = {s['d_min']:.2f} mm, standard size {s['d']:g} mm")
    print(f"actual stress {s['tau']:.1f} MPa, actual safety factor {s['sf_actual']:.2f}, {s['margin'] * 100:.0f} percent above the minimum, {s['mass_per_m']:.2f} kg per metre")
    t15 = torque_from_power(15, 1450)
    print(f"15 kW at 1450 rpm: T = {t15:.1f} N m, shaft {design_shaft(t15)['d']:g} mm")
    print("R10 sizes from 10 to 100 mm:", preferred_sizes(10, 100))

    ts = [20 * k for k in range(1, 101)]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(ts, [min_diameter(t, 350, 2.5) for t in ts], color="tab:blue", label="smallest safe diameter (rule 1)")
    ax.step(ts, [next_preferred(min_diameter(t, 350, 2.5)) for t in ts], where="post", color="tab:red", label="standard size (rule 2)")
    ax.set_xlabel("torque T (N m)")
    ax.set_ylabel("shaft diameter (mm)")
    ax.set_title("Two rules in a row: minimum diameter, then standard size")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "diameter_vs_torque.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for sf, col in ((1.5, "tab:green"), (2.5, "tab:blue"), (4.0, "tab:red")):
        ax2.plot(ts, [design_shaft(t, 350, sf)["sf_actual"] for t in ts], color=col, label=f"asked for SF = {sf}")
    ax2.set_xlabel("torque T (N m)")
    ax2.set_ylabel("safety factor of the standard shaft")
    ax2.set_title("The standard size always gives at least the safety factor asked for")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "safety_factor.png", dpi=120)

# %% [markdown]
# ## Where this stops
# One rule decides one number. A real part has many numbers that depend on each other, and the right answer for one rule (strength) can be wrong for another (stiffness).
# Session 2 puts two competing rules on one part and lets the stricter one decide.
