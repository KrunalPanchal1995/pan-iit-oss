"""Session 2 (Level 2): thermal resistance networks and a chip cooling design.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: thermal resistance, layer by layer
# **A. Real-world problem.** A laptop chip dissipates 20 W. Its heat crosses a smear of thermal
# paste, then an aluminium heatsink base, and is finally carried off by air blowing over the fins.
# Is the chip safe? If its temperature must stay below 85 C, what do you change: the metal, its
# thickness, or the airflow?
#
# **Plan.** (1) turn each layer into a thermal resistance, (2) add resistances in series,
# (3) find the chip temperature, (4) ask which resistance matters most, (5) solve a design problem.
# Heat-transfer model only: general education, not a certified thermal design.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
T_AMBIENT = 25.0        # deg C, air entering the fan
A_BASE = 4.0e-4         # m^2: 20 mm x 20 mm heatsink base (chip heat assumed spread evenly over it)
A_FINS = 1.0e-2         # m^2: total fin surface seen by the air (100 cm^2), a modelling assumption
PASTE_MM, K_PASTE = 0.2, 3.0   # thermal paste layer: thickness (mm) and conductivity W/(m K)


# %% [markdown]
# ## Step 1: a resistance for every layer
# Fourier's law Q = k A dT / L can be turned around into  dT = Q * R  (like Ohm's law, with
# temperature difference in place of voltage and heat flow Q in place of current):
#
#     conduction through a layer:   R = L / (k A)       (K/W)
#     convection to moving air:     R = 1 / (h A)       (K/W)
#
# Here h is the convection coefficient in W/(m^2 K): how well air carries heat off a surface
# (natural convection about 5-15, a laptop fan about 25-100 in this simple model).
# Resistances in a single heat path add, just like resistors in series.

# %%
def r_cond(thickness_mm, k, area):
    """Thermal resistance (K/W) of a flat layer."""
    return thickness_mm * 1e-3 / (k * area)


def r_conv(h, area):
    """Thermal resistance (K/W) of a surface cooled by air with coefficient h."""
    return 1.0 / (h * area)


def stack(base_mm, k_base, h):
    """The three resistances of the chip-to-air path (K/W): paste, base, convection."""
    return [r_cond(PASTE_MM, K_PASTE, A_BASE), r_cond(base_mm, k_base, A_BASE), r_conv(h, A_FINS)]


# %% [markdown]
# ## Step 2: chip temperature and the temperature at each interface
# Total resistance R_total = R_paste + R_base + R_conv. The same Q = P (the chip power) crosses
# every layer, so the chip (junction) temperature is  T_chip = T_ambient + P * R_total.
# Each layer drops P * R_layer on the way.

# %%
def chip_temperature(power, base_mm, k_base, h, t_amb=T_AMBIENT):
    return t_amb + power * sum(stack(base_mm, k_base, h))


def interface_temperatures(power, base_mm, k_base, h, t_amb=T_AMBIENT):
    """Temperatures (deg C) at chip, after paste, after base, then ambient air."""
    out, t = [], chip_temperature(power, base_mm, k_base, h, t_amb)
    out.append(t)
    for r in stack(base_mm, k_base, h)[:2]:
        t -= power * r
        out.append(t)
    out.append(t_amb)
    return out        # the drop across the convection film is the last gap, fins to air


# %% [markdown]
# ## Step 3: the design problem
# Given power P and a chip limit T_max, how much airflow (h) is needed? Rearranging
# T_max = T_amb + P (R_paste + R_base + 1/(h A_fins)) gives the largest allowed convection
# resistance and so the smallest h. The same idea gives the largest power for a given cooler.

# %%
def required_h(power, t_max, base_mm, k_base, t_amb=T_AMBIENT):
    """Smallest h (W/(m^2 K)) that keeps the chip at or below t_max, or None if impossible."""
    r_left = (t_max - t_amb) / power - sum(stack(base_mm, k_base, 1.0)[:2])
    if r_left <= 0:
        return None
    return 1.0 / (r_left * A_FINS)


def max_power(t_max, base_mm, k_base, h, t_amb=T_AMBIENT):
    return (t_max - t_amb) / sum(stack(base_mm, k_base, h))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    P, L, K, H = 20.0, 3.0, 200.0, 50.0
    rs = stack(L, K, H)
    print("resistances (K/W): paste %.4f, base %.4f, convection %.4f, total %.4f" % (*rs, sum(rs)))
    print("worked example: chip temperature = %.2f C" % chip_temperature(P, L, K, H))
    print("interface temperatures:", [round(t, 2) for t in interface_temperatures(P, L, K, H)])
    print("share of the total resistance:", [f"{100 * r / sum(rs):.1f}%" for r in rs])
    for name, k in (("steel", 50.0), ("aluminium", 200.0), ("copper", 400.0)):
        print(f"  base material {name:9s} k = {k:5.0f}: chip at {chip_temperature(P, L, k, H):.2f} C")
    for h in (25.0, 50.0, 100.0):
        print(f"  airflow h = {h:5.1f}: chip at {chip_temperature(P, L, K, h):.2f} C")
    for t in (1.0, 3.0, 6.0):
        print(f"  base thickness {t:3.1f} mm: chip at {chip_temperature(P, t, K, H):.2f} C")
    print("design: 30 W chip, limit 85 C needs h >= %.1f W/(m^2 K)" % required_h(30.0, 85.0, L, K))
    print("max power with this cooler at 85 C: %.1f W" % max_power(85.0, L, K, H))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["paste", "base", "convection"], rs, color=["#e9c46a", "#8d99ae", "#2a9d8f"])
    ax.set_ylabel("thermal resistance (K/W)")
    ax.set_title("The air film dominates the path")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "resistances.png", dpi=120)

    h = np.linspace(20, 100, 81)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for p in (10.0, 20.0, 30.0):
        ax2.plot(h, [chip_temperature(p, L, K, x) for x in h], label=f"{p:.0f} W")
    ax2.axhline(85.0, color="red", ls="--", label="85 C limit")
    ax2.set_xlabel("convection coefficient h (W/(m^2 K))")
    ax2.set_ylabel("chip temperature (C)")
    ax2.set_title("More airflow, cooler chip")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "chip_vs_airflow.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# We treated heat as flowing through the whole base area evenly and the fins as one number.
# Real chips are small hot spots on a larger base, so heat also spreads sideways. That needs 2D
# conduction and time: Session 3.
