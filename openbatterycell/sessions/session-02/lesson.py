"""Session 2 (Level 2): cell voltage, series and parallel packs, charge and Faraday's law.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: voltage, capacity and how much metal a cell must hold
# **A. Real-world problem.** You want a 12 V, 2 Ah supply for a small light and you have only
# 1.10 V zinc-copper cells that each hold 1 Ah. How many cells, connected how? And how many
# grams of zinc must be inside, at the very least?
#
# **Plan.** (1) cell voltage from electrode potentials, (2) series adds voltage, parallel adds
# capacity, (3) charge = n F per mole, (4) Faraday's law gives the metal mass, (5) design.
#
# *Safety: educational model of ideal cells. Real lithium and lead-acid batteries can burn or
# explode if shorted, overheated or overcharged. Do not build battery packs from this lesson.*

# %%
import math
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

FARADAY = 96485.0          # C/mol, charge of one mole of electrons
E_STD = {"Li": -3.04, "Zn": -0.76, "Fe": -0.44, "H": 0.0, "Cu": 0.34, "Ag": 0.80}       # V
MOLAR_MASS = {"Li": 6.941, "Zn": 65.38, "Fe": 55.845, "Cu": 63.546, "Ag": 107.868}     # g/mol
ELECTRONS = {"Li": 1, "Zn": 2, "Fe": 2, "Cu": 2, "Ag": 1}                              # n per ion


# %% [markdown]
# ## Step 1: cell voltage
# E_cell = E_cathode - E_anode, using the standard electrode potentials. Zinc anode and copper
# cathode: 0.34 - (-0.76) = 1.10 V.

# %%
def cell_voltage(cathode, anode):
    return E_STD[cathode] - E_STD[anode]


# %% [markdown]
# ## Step 2: series and parallel
# * **Series** (one after another): voltages add, capacity stays that of one cell.
# * **Parallel** (side by side): voltage stays, capacities add.
# * A pack of `ns` cells in each string and `npar` strings has voltage `ns * V`, capacity
#   `npar * Ah` and energy `V_pack * Ah_pack` (watt-hours, Wh).

# %%
def pack(ns, npar, v_cell, ah_cell):
    """Ideal pack of ns cells in series per string, npar strings in parallel."""
    if ns < 1 or npar < 1 or int(ns) != ns or int(npar) != npar:
        raise ValueError("ns and npar must be whole numbers of at least 1")
    v, ah = ns * v_cell, npar * ah_cell
    return {"volts": v, "amp_hours": ah, "watt_hours": v * ah, "cells": int(ns * npar)}


# %% [markdown]
# ## Step 3: charge and Faraday's law
# One mole of electrons carries F = 96485 coulombs (C). A metal ion with charge n+ needs n
# electrons, so dissolving one mole of metal moves n F coulombs. One ampere-hour is
# 3600 C. The mass of metal that reacts when a charge Q flows is
#
#     m = Q * M / (n * F)         (M = molar mass in g/mol, result in grams)

# %%
def charge_coulombs(amp_hours):
    return amp_hours * 3600.0


def metal_mass_g(charge_c, metal):
    """Grams of `metal` consumed (or deposited) when charge_c coulombs flow (Faraday's law)."""
    if charge_c < 0:
        raise ValueError("charge must not be negative")
    return charge_c * MOLAR_MASS[metal] / (ELECTRONS[metal] * FARADAY)


def specific_capacity_mah_per_g(metal):
    """Theoretical capacity of the metal alone: mAh released per gram (ignores everything else)."""
    return ELECTRONS[metal] * FARADAY / (MOLAR_MASS[metal] * 3.6)


# %% [markdown]
# ## Step 4: the design problem
# Given a target voltage, a target capacity and a cell, find the smallest pack:
# `ns = ceil(V_target / V_cell)` and `npar = ceil(Ah_target / Ah_cell)`, then the zinc needed
# is `cells * mass of zinc for one cell's capacity`.

# %%
def design_pack(v_target, ah_target, v_cell, ah_cell, metal="Zn"):
    """Smallest series/parallel pack meeting both targets, with the metal it must contain (grams)."""
    if v_cell <= 0 or ah_cell <= 0:
        raise ValueError("cell voltage and capacity must be positive")
    ns = max(1, math.ceil(v_target / v_cell - 1e-9))
    npar = max(1, math.ceil(ah_target / ah_cell - 1e-9))
    p = pack(ns, npar, v_cell, ah_cell)
    p.update({"ns": ns, "npar": npar,
              "metal_g": p["cells"] * metal_mass_g(charge_coulombs(ah_cell), metal)})
    return p


def runtime_hours(ah, load_amps):
    return ah / load_amps


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    d = design_pack(12.0, 2.0, cell_voltage("Cu", "Zn"), 1.0)
    print("cell voltage Zn/Cu:", round(cell_voltage("Cu", "Zn"), 2), "V")
    print("charge in 1 Ah:", charge_coulombs(1.0), "C ->", round(charge_coulombs(1.0) / FARADAY, 5), "mol of electrons")
    print("zinc per Ah:", round(metal_mass_g(3600.0, "Zn"), 4), "g")
    print("design:", {k: round(v, 3) if isinstance(v, float) else v for k, v in d.items()})
    for m in ("Li", "Zn", "Fe", "Ag"):
        print(f"{m}: {metal_mass_g(3600.0, m):.3f} g per Ah, {specific_capacity_mah_per_g(m):.0f} mAh/g")

    # figure 1: the 11 x 2 pack drawn as a grid
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for r in range(d["npar"]):
        for c in range(d["ns"]):
            ax.add_patch(plt.Rectangle((c * 1.0, -r * 1.2), 0.8, 0.8, fc="#cfe8f3", ec="k"))
            ax.text(c + 0.4, -r * 1.2 + 0.4, "1.1", ha="center", va="center", fontsize=7)
        ax.plot([-0.4, d["ns"] + 0.1], [-r * 1.2 + 0.4] * 2, color="#999999", lw=0.5, zorder=0)
    ax.set_xlim(-0.6, d["ns"] + 0.3)
    ax.set_ylim(-d["npar"] * 1.2 + 0.2, 1.8)
    ax.axis("off")
    ax.set_title(f"{d['ns']} cells in series x {d['npar']} strings in parallel = {d['volts']:.1f} V, {d['amp_hours']:.0f} Ah, {d['watt_hours']:.1f} Wh", fontsize=9)
    ax.text(0, 1.2, "each box: one 1.10 V, 1 Ah cell (volts shown)", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "pack_grid.png", dpi=120)

    # figure 2: grams of metal per ampere-hour
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    names = ["Li", "Zn", "Fe", "Ag"]
    ax2.bar(names, [metal_mass_g(3600.0, m) for m in names], color=["#2a9d8f", "#8c92ac", "#b0643c", "#c0c0c0"])
    ax2.set_ylabel("metal consumed per ampere-hour (g)")
    ax2.set_xlabel("metal at the anode (or cathode)")
    ax2.set_title("Faraday's law: light metals give more charge per gram")
    ax2.grid(axis="y", alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "mass_per_ah.png", dpi=120)

# %% [markdown]
# ## Where this stops
# These formulas assume the cell delivers its full 1.10 V and every gram of metal reacts. Real
# cells lose voltage under load and cannot use all their metal. Session 3 simulates that.
