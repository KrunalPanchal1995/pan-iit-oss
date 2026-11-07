"""Session 1 (Level 1): salt water pulls on fresh water, and that pull sets the minimum energy.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: osmotic pressure and the minimum energy
# **A. Real-world problem.** Coastal cities such as Chennai already drink water made from
# the sea. Pulling the salt out costs electricity. Is there a smallest possible energy bill,
# one that no clever machine can beat? Physics says yes, and it is set by the
# **osmotic pressure** of seawater.
#
# **Plan.** (1) turn grams of salt per litre into moles per cubic metre, (2) the van 't Hoff
# law for osmotic pressure, (3) pressure times volume is energy: 1 kPa x 1 m3 = 1 kJ,
# (4) compare the minimum with boiling the water and with pumping it uphill.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R = 8.314           # gas constant, J/(mol K)
M_NACL = 58.44      # molar mass of sodium chloride, g/mol
KJ_PER_KWH = 3600.0  # 1 kWh = 3600 kJ


# %% [markdown]
# ## Step 1: from grams per litre to moles per cubic metre
# Seawater holds about 35 g of salt in every litre. We treat all of it as sodium chloride
# (NaCl, 58.44 g/mol). Since 1 g/L = 1 kg/m3, the concentration in mol/m3 is
#
#     c = (salt in g/L) / (58.44 g/mol) x 1000
#
# Each NaCl splits into two ions (Na+ and Cl-), so the number of dissolved particles is
# i = 2 times larger. Osmosis counts particles, not grams.

# %%
def molar_concentration(salt_g_per_l, molar_mass=M_NACL):
    """Moles of salt per cubic metre (mol/m3) from grams of salt per litre."""
    if salt_g_per_l < 0:
        raise ValueError("salt concentration cannot be negative")
    return salt_g_per_l / molar_mass * 1000.0


# %% [markdown]
# ## Step 2: the van 't Hoff law
# Put fresh water and salt water on two sides of a membrane that lets water through but
# not salt. Water flows into the salty side. The pressure you must push back with to stop
# that flow is the osmotic pressure
#
#     pi = phi x i x c x R x T
#
# with T in **kelvin** (K = degrees C + 273.15). phi = 1 is the ideal (dilute) law used in
# this repo; measured seawater behaves as if phi were about 0.9, so the ideal law gives
# numbers about 10 percent too high. We keep phi = 1 so every number is hand-checkable.

# %%
def osmotic_pressure(salt_g_per_l, t_celsius=25.0, i=2, phi=1.0):
    """Osmotic pressure in kPa of NaCl water (van 't Hoff law)."""
    t_kelvin = t_celsius + 273.15
    if t_kelvin <= 0:
        raise ValueError("temperature must be above absolute zero")
    c = molar_concentration(salt_g_per_l)
    return phi * i * c * R * t_kelvin / 1000.0   # Pa -> kPa


# %% [markdown]
# ## Step 3: pressure x volume = energy
# To squeeze fresh water out through the membrane you must push at (at least) the osmotic
# pressure. Pushing a volume V against a pressure P costs the work P x V. Units:
# 1 kPa x 1 m3 = 1 kJ, and 1 kWh = 3600 kJ. So for each cubic metre of fresh water
#
#     minimum energy (kWh/m3) = pi (kPa) / 3600
#
# This is the minimum when you take only a tiny sip of fresh water out of a huge amount of
# seawater (zero recovery). Session 2 shows it grows when you take more.

# %%
def kwh_per_m3(pressure_kpa):
    """Energy per cubic metre (kWh/m3) to push water against a pressure in kPa."""
    return pressure_kpa / KJ_PER_KWH


def minimum_energy(salt_g_per_l, t_celsius=25.0):
    """Least energy (kWh/m3) to take a little fresh water out of salt water."""
    return kwh_per_m3(osmotic_pressure(salt_g_per_l, t_celsius))


def column_height(pressure_kpa, rho=1000.0, g=9.81):
    """Height (m) of a water column that gives this pressure at its base: h = P / (rho g)."""
    return pressure_kpa * 1000.0 / (rho * g)


# %% [markdown]
# ## Step 4: compare with boiling and with pumping uphill
# The oldest way to make fresh water is to boil it and condense the steam. Boiling 1 m3
# (1000 kg) needs the latent heat 2257 kJ/kg. Lifting 1 m3 of water by a height h needs
# rho g h. These put the osmotic minimum in perspective.

# %%
def boiling_energy(latent_kj_per_kg=2257.0, rho=1000.0):
    """Heat (kWh/m3) to evaporate water once, without any heat recovery."""
    return latent_kj_per_kg * rho / KJ_PER_KWH


def lifting_energy(height_m, rho=1000.0, g=9.81):
    """Energy (kWh/m3) to lift water by a height in metres."""
    return rho * g * height_m / 1000.0 / KJ_PER_KWH


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # Figure 1: osmotic pressure against salinity, with some real waters marked
    waters = [("river", 0.5, (8, 14)), ("brackish well", 5.0, (8, 36)), ("seawater", 35.0, (-6, 8)),
              ("Gulf seawater", 45.0, (-6, 8)), ("RO brine", 70.0, (-6, -30))]
    s = np.linspace(0.0, 75.0, 151)
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    for tc, ls in [(10.0, "--"), (25.0, "-"), (40.0, ":")]:
        ax.plot(s, [osmotic_pressure(x, tc) / 1000 for x in s], "k", ls=ls, lw=1.5, label=f"{tc:.0f} C")
    for name, x, off in waters:
        p = osmotic_pressure(x)
        ax.plot(x, p / 1000, "o", color="#2a9d8f")
        ax.annotate(f"{name}\n{p / 1000:.2f} MPa", (x, p / 1000), textcoords="offset points", xytext=off,
                    fontsize=8, ha="left" if off[0] > 0 else "right")
        print(f"{name:14s}: {x:5.1f} g/L -> pi = {p:7.0f} kPa, minimum {minimum_energy(x):.3f} kWh/m3")
    ax.set_xlabel("salt concentration (g/L, as NaCl)")
    ax.set_ylabel("osmotic pressure (MPa)")
    ax.set_title("van 't Hoff: osmotic pressure grows in a straight line with salt")
    ax.set_xlim(0, 75)
    ax.set_ylim(0, 6.6)
    ax.grid(alpha=0.3)
    ax.legend(title="temperature", fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "osmotic_pressure.png", dpi=120)

    # Figure 2: the minimum energy next to boiling and lifting (log scale)
    items = [("osmotic minimum\nseawater 35 g/L", minimum_energy(35.0), "#2a9d8f"),
             ("lift water\n100 m", lifting_energy(100.0), "#8d99ae"),
             ("typical seawater\nRO plant (approx.)", 3.5, "#e9c46a"),
             ("boil once,\nno heat recovery", boiling_energy(), "#d9534f")]
    fig2, ax2 = plt.subplots(figsize=(7.0, 4.2))
    for k, (name, e, col) in enumerate(items):
        ax2.bar(k, e, color=col)
        ax2.text(k, e * 1.15, f"{e:.2f}", ha="center", fontsize=9)
        print(f"{name.replace(chr(10), ' '):38s}: {e:8.3f} kWh/m3")
    ax2.set_yscale("log")
    ax2.set_ylim(0.1, 2000)
    ax2.set_xticks(range(len(items)))
    ax2.set_xticklabels([n for n, _, _ in items], fontsize=8)
    ax2.set_ylabel("energy per m3 of fresh water (kWh/m3)")
    ax2.set_title("The osmotic minimum is about 760 times smaller than boiling")
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "energy_compare.png", dpi=120)
    print(f"seawater osmotic pressure equals a water column of {column_height(osmotic_pressure(35.0)):.0f} m")

# %% [markdown]
# ## Where this stops
# We took only a tiny sip of fresh water. A real plant takes about half of the seawater as
# fresh water, so the salt left behind gets stronger and the push must grow. Session 2
# works out how the minimum energy depends on that share (the recovery).
