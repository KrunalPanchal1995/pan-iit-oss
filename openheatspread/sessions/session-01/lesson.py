"""Session 1 (Level 1): heat flows through a slab, from hot to cold.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: how heat flows through a slab
# **A. Real-world problem.** The chip inside a laptop gets hot; the metal heatsink and the air
# around it stay cooler. Heat always moves from the hot side to the cold side, but how fast? And
# what does the temperature look like INSIDE the material between them? Today we answer both
# for the simplest case: a flat slab with one hot face and one cold face.
#
# **Plan.** (1) write Fourier's law of conduction, (2) get the temperature at any depth,
# (3) compare materials, (4) plot the straight-line temperature profile.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
AREA = 1.0e-4          # m^2: a 1 cm x 1 cm patch, about the size of a small chip

# thermal conductivity k in W/(m K) (typical room-temperature values)
MATERIALS = {
    "copper": 400.0,
    "aluminium": 200.0,
    "steel": 50.0,
    "thermal pad": 5.0,
    "glass": 1.0,
    "still air": 0.026,
}


# %% [markdown]
# ## Step 1: Fourier's law
# Heat flow through a slab of thickness L, area A and conductivity k, with the hot face at
# T_hot and the cold face at T_cold (steady state: nothing changes with time):
#
#     Q = k * A * (T_hot - T_cold) / L          (watts)
#
# Read it as a story: a bigger area lets more heat through, a bigger temperature difference
# pushes harder, a thicker slab slows the heat down, and a higher conductivity k means the
# material is a better heat road. Heat flux q = Q / A is the same thing per square metre (W/m^2).

# %%
def heat_rate(k, thickness_mm, t_hot, t_cold, area=AREA):
    """Heat flow Q in watts through a slab of the given thickness (mm)."""
    return k * area * (t_hot - t_cold) / (thickness_mm * 1e-3)


def heat_flux(k, thickness_mm, t_hot, t_cold):
    """Heat flux q in W/m^2 (heat per second per square metre)."""
    return k * (t_hot - t_cold) / (thickness_mm * 1e-3)


# %% [markdown]
# ## Step 2: the temperature inside the slab
# In steady state the same heat Q must cross every layer, so the temperature falls at a constant
# rate: a straight line from T_hot at x = 0 to T_cold at x = L. Notice that k does not appear
# in this line. A good conductor and a poor one have the same straight profile; they differ in
# how much heat Q they carry.

# %%
def temperature_at(x_mm, thickness_mm, t_hot, t_cold):
    """Temperature (deg C) at depth x_mm from the hot face."""
    return t_hot - (t_hot - t_cold) * np.asarray(x_mm, dtype=float) / thickness_mm


# %% [markdown]
# ## Step 3: compare materials
# Same slab (5 mm thick, 1 cm^2), same temperatures (80 C hot face, 40 C cold face): how much
# heat flows in each material?

# %%
def compare_materials(thickness_mm=5.0, t_hot=80.0, t_cold=40.0):
    return {name: heat_rate(k, thickness_mm, t_hot, t_cold) for name, k in MATERIALS.items()}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    table = compare_materials()
    for name, q in table.items():
        print(f"{name:12s} k = {MATERIALS[name]:7.3f} W/(m K)  ->  Q = {q:9.3f} W")
    print(f"copper carries {table['copper'] / table['thermal pad']:.0f} times more heat than the thermal pad")

    q = heat_rate(5.0, 1.0, 80.0, 50.0)
    print(f"worked example: pad k = 5, 1 mm, 80 C to 50 C -> Q = {q:.1f} W, flux {heat_flux(5.0, 1.0, 80.0, 50.0):.0f} W/m^2")
    print(f"temperature at mid depth = {float(temperature_at(0.5, 1.0, 80.0, 50.0)):.1f} C")

    fig, ax = plt.subplots(figsize=(6, 4))
    for thick in (2.0, 5.0, 10.0):
        x = np.linspace(0, thick, 50)
        ax.plot(x, temperature_at(x, thick, 80.0, 40.0), label=f"L = {thick:.0f} mm")
    ax.set_xlabel("depth from the hot face (mm)")
    ax.set_ylabel("temperature (C)")
    ax.set_title("Straight-line temperature profile, any material")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "temperature_profile.png", dpi=120)

    names = [n for n in table if n != "still air"]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(names, [table[n] for n in names], color="#2a9d8f")
    ax2.set_yscale("log")
    ax2.set_ylabel("heat flow Q (W), log scale")
    ax2.set_title("Same slab, different material (5 mm, 80 C to 40 C)")
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "heat_by_material.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. Next session: what if there are several layers, and the air at the end?
