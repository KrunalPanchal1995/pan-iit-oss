"""Session 1 (Level 1): why things float, and how deep they sit.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: things float when the water they push aside weighs as much as they do
# **A. Real-world problem.** A steel ship weighs thousands of tonnes and floats. A pebble
# weighs a few grams and sinks. A block of wood floats, but sits deeper in a pond than in the
# sea. One rule explains all of it: *an object pushes water out of its way, and the water
# pushes back with a force equal to the weight of the water that was pushed aside.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.81            # gravity, m/s^2
FRESH = 1000.0      # density of fresh water, kg/m^3
SEA = 1025.0        # density of sea water, kg/m^3 (about)


# %% [markdown]
# ## Step 1: average density decides
# Average density = total mass / total outside volume. A floating object sinks into the
# water until the water it displaces has the same mass as the object. For an object with
# average density `rho_obj` in a fluid of density `rho_fluid`, that means a fraction
# `rho_obj / rho_fluid` of its volume is under the surface (and it sinks if that is 1 or more).

# %%
def average_density(mass, volume):
    """kg/m^3 from mass (kg) and the outside volume (m^3)."""
    return mass / volume


def floats(rho_obj, rho_fluid):
    """True if the object floats (average density below the fluid's)."""
    return bool(rho_obj < rho_fluid)


def submerged_fraction(rho_obj, rho_fluid):
    """Fraction of the volume below the surface: rho_obj / rho_fluid, at most 1."""
    return float(min(1.0, rho_obj / rho_fluid))


def displaced_mass(rho_obj, volume, rho_fluid):
    """Mass (kg) of water pushed aside: equals the object's mass when it floats."""
    return rho_fluid * volume * submerged_fraction(rho_obj, rho_fluid)


# %% [markdown]
# ## Step 2: the draft marking
# For a box with a flat bottom of area `area` (m^2) floating upright, the depth below the
# surface (the *draft*) is: draft = mass / (rho_fluid * area). Ships have draft marks painted
# on the bow so everyone can read how deep they sit.

# %%
def draft_box(mass, area, rho_fluid):
    """Depth (m) of a flat-bottomed box below the surface."""
    return mass / (rho_fluid * area)


# %% [markdown]
# ## Step 3: three things and one trick
# A wooden block, a rock and a steel boat (the same steel, hammered flat, would sink).

# %%
THINGS = {
    # name: (mass kg, outside volume m^3, flat bottom area m^2)
    "wood block 0.2 m cube": (4.8, 0.008, 0.04),
    "rock 0.2 m cube": (21.6, 0.008, 0.04),
    "small steel boat 2.0 x 0.8 x 0.5 m": (150.0, 0.8, 1.6),
}
SHORT = dict(zip(THINGS, ["wood block", "rock", "steel boat"]))
STEEL = 7850.0      # density of steel, kg/m^3


def steel_volume(mass):
    """Volume (m^3) of the metal itself, if it were a solid lump."""
    return mass / STEEL


# %% [markdown]
# ## Step 4: salt in the bucket
# Dissolving table salt makes water denser: about 0.71 kg/m^3 for every gram of salt in each
# litre (35 g per litre gives 1025 kg/m^3, the sea). This straight-line rule is good up to
# roughly 100 g per litre. Denser water pushes back harder per unit of volume, so a floating
# box sits higher. `salt_experiment` predicts the draft for each amount of salt.

# %%
SALT_SLOPE = (SEA - FRESH) / 35.0   # kg/m^3 per (g of salt per litre of water)


def salt_water_density(salt_g, water_litres):
    """Density (kg/m^3) of `water_litres` of water with `salt_g` grams of table salt dissolved."""
    return FRESH + SALT_SLOPE * salt_g / water_litres


def salt_experiment(mass, area, water_litres, salt_steps_g):
    """Rows (salt_g, density, draft_m) for a flat-bottomed floater of `mass` kg and base `area` m^2."""
    rows = []
    for salt in salt_steps_g:
        rho = salt_water_density(salt, water_litres)
        rows.append((salt, rho, draft_box(mass, area, rho)))
    return rows


# the home set-up used on the experiment sheet: a sand-ballasted straight-sided bottle in a 10 litre bucket
SALT_SETUP = dict(mass=0.60, area=0.0050, water_litres=10.0, salt_steps_g=[0, 200, 400, 600, 800, 1000])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for name, (m, v, a) in THINGS.items():
        rho = average_density(m, v)
        print(f"{name:38s} average density {rho:7.1f} kg/m^3  floats in fresh water: {floats(rho, FRESH)}"
              f"  submerged {submerged_fraction(rho, FRESH):.3f}  draft {draft_box(m, a, FRESH) if floats(rho, FRESH) else float('nan'):.3f} m")
    m_boat = THINGS["small steel boat 2.0 x 0.8 x 0.5 m"][0]
    print(f"the boat's steel as a solid lump: {steel_volume(m_boat):.4f} m^3, density {STEEL:.0f} -> sinks: {not floats(STEEL, FRESH)}")
    print(f"wood block draft: fresh {draft_box(4.8, 0.04, FRESH):.3f} m, sea {draft_box(4.8, 0.04, SEA):.3f} m")
    for salt, rho, d in salt_experiment(**SALT_SETUP):
        print(f"salt {salt:5.0f} g in {SALT_SETUP['water_litres']:.0f} L: density {rho:7.1f} kg/m^3, draft {1000 * d:6.1f} mm")

    # figure 1: side views with the water line
    fig, axs = plt.subplots(1, 3, figsize=(10, 3.6), sharey=True)
    for ax, (name, (m, v, a)) in zip(axs, THINGS.items()):
        rho = average_density(m, v)
        f = submerged_fraction(rho, FRESH)
        h = 1.0
        top = h * (1 - f) if f < 1 else -h
        ax.axhspan(-1.4, 0, color="tab:blue", alpha=0.25)
        ax.axhline(0, color="tab:blue")
        ax.add_patch(plt.Rectangle((-0.5, -h * f if f < 1 else -1.3), 1.0, h, color="tab:orange", alpha=0.8))
        ax.set_title(f"{name.split(' 0')[0].split(' 2')[0]}\nrho = {rho:.0f} kg/m^3, {'floats' if f < 1 else 'sinks'}", fontsize=9)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1.4, 1.3)
        ax.set_xticks([])
    axs[0].set_ylabel("height relative to the water line (scaled)")
    fig.tight_layout()
    fig.savefig(OUT / "float_or_sink.png", dpi=120)

    # figure 2: submerged fraction versus average density
    rho = np.linspace(0, 3000, 301)
    frac = np.minimum(1.0, rho / FRESH)
    frac_sea = np.minimum(1.0, rho / SEA)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(rho, frac, label="fresh water (1000 kg/m^3)")
    ax2.plot(rho, frac_sea, "--", label="sea water (1025 kg/m^3)")
    for name, (m, v, a) in THINGS.items():
        ax2.plot(average_density(m, v), submerged_fraction(average_density(m, v), FRESH), "ko")
    ax2.set_xlabel("average density of the object (kg/m^3)")
    ax2.set_ylabel("fraction of volume under water")
    ax2.set_title("It floats while the fraction is below 1")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "fraction_vs_density.png", dpi=120)

    # figure 3: draft marks
    fig3, ax3 = plt.subplots(figsize=(5, 4))
    for extra in np.arange(0.0, 3.1, 0.5):
        d = draft_box(4.8 + extra, 0.04, FRESH)
        ax3.plot([0, 1], [-d, -d], color="tab:blue")
        ax3.text(1.03, -d, f"{4.8 + extra:.1f} kg", va="center", fontsize=8)
    ax3.set_xlim(0, 1.5)
    ax3.set_xticks([])
    ax3.set_ylabel("draft: depth below the water line (m, drawn downward)")
    ax3.set_title("Wood block: each extra kilogram sinks it 2.5 cm")
    fig3.tight_layout()
    fig3.savefig(OUT / "draft_marks.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Floating is only half the story: a ship can float and still roll over. That is Session 3.
