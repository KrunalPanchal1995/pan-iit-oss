"""Session 2 (Level 2): ratios, torque, compound trains, module and centre distance, a 1:20 design.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the mathematics of a gear train
# **A. Real-world problem.** A motor spins at 1200 rpm but a conveyor must turn at 60 rpm.
# We need a reduction of 1:20 from gears that actually exist: whole numbers of teeth, no
# pinion so small that its teeth are cut away, and a size that fits in a box.
#
# **Plan.** (1) stage and compound ratios, (2) speed, torque and power, (3) module, pitch
# diameter and centre distance, (4) the smallest integer-tooth design for 1:20.

# %%
import pathlib
from fractions import Fraction

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: ratios multiply
# For one mesh the *speed ratio* is `i = N_driven / N_driver` (more than 1 means a reduction).
# A compound train has several stages; two gears sit on the same shaft (so they turn together),
# and the stage ratios multiply: `i = (N2/N1) * (N4/N3)`. The output speed is `w_in / i`, the
# ideal output torque is `T_in * i`, and the power `T * w` is unchanged (ideal = no losses).
# The direction after k external meshes is `(-1)^k`.

# %%
def stage_ratio(n_driver, n_driven):
    return n_driven / n_driver


def compound_ratio(stages):
    """Overall speed ratio of a train given as [(N_driver, N_driven), ...]."""
    i = 1.0
    for n_driver, n_driven in stages:
        i *= stage_ratio(n_driver, n_driven)
    return i


def output_speed(w_in, stages):
    """Output speed (same unit as w_in); the sign is the direction, one external mesh per stage."""
    return (-1) ** len(stages) * w_in / compound_ratio(stages)


def output_torque_ideal(t_in, stages):
    """Ideal output torque (no losses), same sign convention as the speed."""
    return (-1) ** len(stages) * t_in * compound_ratio(stages)


# %% [markdown]
# ## Step 2: module, pitch diameter and centre distance
# Gears that mesh share the same tooth size, the *module* m (mm per tooth). The pitch circle
# of a gear with N teeth has diameter `d = m N`, and two meshing gears sit a centre distance
# `a = (d1 + d2) / 2 = m (N1 + N2) / 2` apart.

# %%
def pitch_diameter(module_mm, n_teeth):
    return module_mm * n_teeth


def centre_distance(module_mm, n1, n2):
    return module_mm * (n1 + n2) / 2


# %% [markdown]
# ## Step 3: the minimum number of teeth, and the contact ratio
# A gear cutter can remove the root of a tooth of a small pinion (*undercutting*). For the
# common 20 degree pressure angle the limit from geometry is `2 / sin^2(phi)` = 17.1 teeth, so
# 17 teeth is a commonly used practical guideline for a pinion. Meshing also needs the *contact
# ratio* (the average number of tooth pairs in contact) to be above 1, or the drive would
# jump from tooth to tooth.

# %%
def min_teeth_no_undercut(phi_deg=20.0):
    return 2.0 / np.sin(np.radians(phi_deg)) ** 2


def contact_ratio(n1, n2, phi_deg=20.0):
    """Contact ratio of a standard full-depth spur pair (addendum = module)."""
    phi = np.radians(phi_deg)
    r1, r2 = n1 / 2.0, n2 / 2.0              # pitch radii for module 1
    ra1, ra2 = r1 + 1.0, r2 + 1.0            # addendum radii
    rb1, rb2 = r1 * np.cos(phi), r2 * np.cos(phi)
    path = np.sqrt(ra1 ** 2 - rb1 ** 2) + np.sqrt(ra2 ** 2 - rb2 ** 2) - (r1 + r2) * np.sin(phi)
    return float(path / (np.pi * np.cos(phi)))


# %% [markdown]
# ## Step 4: design a 1:20 reduction with the fewest teeth
# One stage would need a 17-tooth pinion and a 340-tooth gear. Two compound stages are better.
# We list every pair (N_driver, N_driven) with both counts from 17 to 100, group them by their
# exact ratio (a `Fraction`, so no rounding), and join two groups whose ratios multiply to 20.

# %%
def fewest_teeth_designs(target, n_min=17, n_max=100):
    """All two-stage integer designs with ratio exactly `target`, smallest total teeth first.

    Each entry is (total_teeth, (N1, N2), (N3, N4)).
    """
    groups = {}
    for a in range(n_min, n_max + 1):
        for b in range(n_min, n_max + 1):
            groups.setdefault(Fraction(b, a), []).append((a, b))
    found = []
    for r, first in groups.items():
        second = groups.get(Fraction(target) / r)
        if second:
            for p in first:
                for q in second:
                    found.append((sum(p) + sum(q), p, q))
    found.sort()
    return found


def shaft_speeds(w_in, stages):
    """Speed of each shaft: input, then after each stage (signed)."""
    out = [w_in]
    for n_driver, n_driven in stages:
        out.append(-out[-1] * n_driver / n_driven)
    return out


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    designs = fewest_teeth_designs(20)
    best = designs[0]
    print("number of exact 1:20 two-stage designs (17..100 teeth):", len(designs))
    print("smallest total:", best)
    stages = [best[1], best[2]]
    print("overall ratio", compound_ratio(stages), "speeds", shaft_speeds(1200, stages))
    print("undercut limit", round(min_teeth_no_undercut(), 2))
    print("contact ratio 20:40", round(contact_ratio(20, 40), 3), " 17:85", round(contact_ratio(17, 85), 3))
    print("centre distances (module 2):", centre_distance(2, 17, 68), centre_distance(2, 17, 85), "mm")

    # figure 1: all pair ratios and the 1:20 hyperbola
    n = np.arange(17, 101)
    fig, ax = plt.subplots(figsize=(6, 4.2))
    r1 = np.linspace(1.0, 6.0, 200)
    ax.plot(r1, 20 / r1, color="tab:blue", label="stage 1 x stage 2 = 20")
    for tot, p, q in designs[:12]:
        ax.plot(p[1] / p[0], q[1] / q[0], "o", color="tab:red", ms=4)
    ax.plot([], [], "o", color="tab:red", label="integer designs (smallest 12)")
    ax.set_xlabel("stage 1 ratio N2 / N1")
    ax.set_ylabel("stage 2 ratio N4 / N3")
    ax.set_title("Two stages whose ratios multiply to 20")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "ratio_hyperbola.png", dpi=120)

    # figure 2: speed and torque along the shafts (power stays constant)
    w = np.abs(shaft_speeds(1200, stages))
    t = 2.0 * np.array([1.0, stages[0][1] / stages[0][0], compound_ratio(stages)])
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot([0, 1, 2], w, "o-", label="speed (rpm)")
    ax2.set_xticks([0, 1, 2], ["input shaft", "middle shaft", "output shaft"])
    ax2.set_ylabel("speed (rpm)")
    ax3 = ax2.twinx()
    ax3.plot([0, 1, 2], t, "s-", color="tab:red")
    ax3.set_ylabel("ideal torque (N m)")
    ax2.set_title("Speed falls, torque rises: power is the same")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "shaft_speed_torque.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Change `n_max` or the target, predict how many designs there will be, then run it. Answer the
# four questions in the README (section F), then run the checkpoint.
