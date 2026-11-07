"""Session 1 (Level 1): a building must spread its weight over enough ground.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: spread the weight, or the ground gives way
# **A. Real-world problem.** A stiletto heel can dent a wooden floor, yet a heavy building
# stands on soil without sinking. The force is large, so the building spreads it over a
# wide *footing*. The idea is one division: pressure = force / area.
#
# **Plan.** (1) compute pressure, (2) compare heel, shoe and snowshoe, (3) find how wide a
# square footing must be so the soil is not overloaded, (4) plot pressure against width.
# Educational model only: never use it to design a real foundation.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# Typical textbook allowable bearing pressures in kPa (kilonewtons per square metre).
# They are rough ranges for teaching, NOT values for design.
SOIL_RANGES = {
    "soft clay": (50.0, 100.0),
    "firm clay": (100.0, 200.0),
    "dense sand or gravel": (200.0, 400.0),
}


# %% [markdown]
# ## Step 1: pressure = force / area
# With force in kilonewtons (kN) and area in square metres (m^2) the pressure comes out in
# kilopascals (kPa). 1 kPa = 1 kN per m^2.
#
# Worked by hand: 700 N is 0.7 kN. A heel of 1 cm^2 is 0.0001 m^2, so the pressure is
# 0.7 / 0.0001 = 7000 kPa. A snowshoe pair of 0.2 m^2 gives 0.7 / 0.2 = 3.5 kPa.

# %%
def pressure(force_kn, area_m2):
    """Pressure in kPa from a force in kN spread over an area in m^2."""
    if np.any(np.asarray(area_m2) <= 0):
        raise ValueError("area must be positive")
    return force_kn / area_m2


def person_pressures(weight_n=700.0):
    """Pressure (kPa) under a stiletto heel, a shoe and a pair of snowshoes (illustrative areas)."""
    areas = {"stiletto heel (1 cm^2)": 1e-4, "shoe (300 cm^2)": 0.03, "snowshoes (2000 cm^2)": 0.2}
    return {name: pressure(weight_n / 1000.0, a) for name, a in areas.items()}


# %% [markdown]
# ## Step 2: a square footing under a column
# A column carries a load P (kN) into a square footing of side B (m). The area is B * B.
# At this level we ignore the weight of the footing itself (Session 2 adds it).

# %%
def footing_pressure(load_kn, side_m):
    """Average pressure (kPa) under a square footing."""
    return pressure(load_kn, side_m * side_m)


def is_safe(load_kn, side_m, allowable_kpa):
    """True when the pressure does not exceed the allowable bearing pressure (tiny tolerance for round-off)."""
    return footing_pressure(load_kn, side_m) <= allowable_kpa * (1 + 1e-12)


def round_up(x, step=0.05):
    """Round x up to a multiple of step (footings are built in neat sizes)."""
    return math.ceil(x / step - 1e-9) * step


def min_side(load_kn, allowable_kpa):
    """Smallest square side (m) so that load / side^2 <= allowable: B = sqrt(P / q)."""
    return math.sqrt(load_kn / allowable_kpa)


# %% [markdown]
# ## Step 3: see it
# Left: pressure falls as the footing widens (area grows with B squared). The soil bands show
# typical allowable ranges. Right: heel, shoe and snowshoe on a log scale.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for name, v in person_pressures().items():
        print(f"{name:26s} -> {v:10.1f} kPa")
    print("300 kN on 1.5 m square:", round(footing_pressure(300, 1.5), 1), "kPa")
    print("smallest side for 75 kPa:", round(min_side(300, 75), 3), "m")

    B = np.linspace(0.8, 4.0, 200)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(B, footing_pressure(300, B), color="C0", label="pressure under 300 kN column")
    for (name, (lo, hi)), col in zip(SOIL_RANGES.items(), ("C3", "C1", "C2")):
        ax.axhspan(lo, hi, color=col, alpha=0.15, label=f"{name} ({lo:.0f} to {hi:.0f} kPa)")
    ax.set_ylim(0, 450)
    ax.set_xlabel("footing side B (m)")
    ax.set_ylabel("pressure on soil (kPa)")
    ax.set_title("A wider footing means lower pressure (typical ranges, not for design)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "pressure_vs_width.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 3.5))
    pp = person_pressures()
    ax2.barh(list(pp.keys()), list(pp.values()), color=["C3", "C1", "C2"])
    ax2.set_xscale("log")
    ax2.set_xlabel("pressure (kPa, log scale)")
    ax2.set_title("Same 700 N person, very different pressure")
    ax2.grid(alpha=0.3, axis="x")
    fig2.tight_layout()
    fig2.savefig(OUT / "heel_vs_snowshoe.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
