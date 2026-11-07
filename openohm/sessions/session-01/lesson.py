"""Session 1 (Level 1): Ohm's law and electrical power.

Run:  python start.py 1
Low-voltage educational circuits only (batteries and small supplies, never mains).
"""
# %% [markdown]
# # Session 1: Ohm's law and electrical power
# **A. Real-world problem.** A phone charger, a torch bulb and a toaster all push electric
# current through something that resists it. How much current flows, and how much power turns
# into heat? Two short rules answer both.
#
# **Plan.** (1) Ohm's law V = I R, (2) power P = V I, (3) three graphs: I vs V, I vs R, P vs R.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: Ohm's law
# Voltage V (volts) is the push, resistance R (ohms) is how hard the part resists, and the
# current I (amperes) is the flow. For an *ohmic* part, I = V / R.
#
# Check by hand: V = 12 V across R = 6 ohm gives I = 12 / 6 = 2 A.

# %%
def current(volts, ohms):
    """Current in amperes through a resistor (ideal supply, ideal wires)."""
    if ohms <= 0:
        raise ValueError("resistance must be positive")
    return volts / ohms


# %% [markdown]
# ## Step 2: electrical power
# Power is energy per second turned into heat in the resistor: P = V I. Using Ohm's law it
# can also be written P = I^2 R and P = V^2 / R. All three give the same number.
#
# Check by hand: 12 V and 2 A give P = 24 W. Also I^2 R = 4 * 6 = 24 W.

# %%
def power(volts, ohms):
    """Power in watts dissipated in the resistor, P = V^2 / R."""
    return volts * volts / ohms


def power_forms(volts, ohms):
    """The three equivalent forms (V*I, I^2*R, V^2/R), in watts."""
    i = current(volts, ohms)
    return volts * i, i * i * ohms, volts * volts / ohms


# %% [markdown]
# ## Step 3: see it
# Three graphs, one question each. I vs V: a straight line with slope 1/R. I vs R: a falling
# curve (more resistance, less current). P vs R: also falling at fixed V.

# %%
PRESET_V = (1.0, 12.0, 24.0)
PRESET_R = (1.0, 6.0, 12.0, 24.0)


def table(volts_list=PRESET_V, ohms_list=PRESET_R):
    """Rows (V, R, I, P) for every preset combination."""
    return [(v, r, current(v, r), power(v, r)) for v in volts_list for r in ohms_list]


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for v, r, i, p in table((12.0,), PRESET_R):
        print(f"V = {v:4.0f} V, R = {r:4.0f} ohm -> I = {i:.3f} A, P = {p:.1f} W")
    print("24 ohm on 12 V draws", current(12.0, 24.0), "A")

    v = np.linspace(0, 24, 100)
    fig, ax = plt.subplots(figsize=(6, 4))
    for r in PRESET_R:
        ax.plot(v, v / r, label=f"R = {r:g} ohm")
    ax.set_xlabel("voltage V (volts)")
    ax.set_ylabel("current I (amperes)")
    ax.set_title("I versus V: straight lines, slope = 1/R")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "i_vs_v.png", dpi=120)

    r = np.linspace(1, 24, 100)
    fig2, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4))
    for volts in PRESET_V:
        a1.plot(r, volts / r, label=f"V = {volts:g} V")
        a2.plot(r, volts ** 2 / r, label=f"V = {volts:g} V")
    a1.set_xlabel("resistance R (ohms)")
    a1.set_ylabel("current I (amperes)")
    a1.set_title("I versus R")
    a2.set_xlabel("resistance R (ohms)")
    a2.set_ylabel("power P (watts)")
    a2.set_title("P versus R")
    for a in (a1, a2):
        a.grid(alpha=0.3)
        a.legend()
    a2.set_ylim(0, 150)
    fig2.tight_layout()
    fig2.savefig(OUT / "i_p_vs_r.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
