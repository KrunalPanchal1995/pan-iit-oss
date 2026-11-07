"""Session 1 (Level 1): a changing magnetic flux makes a voltage (electromagnetic induction).

Run:  python start.py 1
Low-voltage educational model only (never mains). Simplified: ideal coil, no resistance.
"""
# %% [markdown]
# # Session 1: a magnet and a coil make a voltage
# **A. Real-world problem.** A bicycle dynamo has no battery, yet it lights a lamp when you pedal.
# Inside is a magnet and a coil of wire. Nothing touches, nothing is charged up. Where does the
# voltage come from? The answer is *induction*: a **changing** magnetic field through a coil
# pushes charges round the wire.
#
# **Plan.** (1) push a magnet through a coil and measure the voltage, (2) see that speed and
# turns matter, (3) spin a coil and get an alternating voltage.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

AREA = 0.002          # coil area in m^2 (about 4.5 cm x 4.5 cm)


# %% [markdown]
# ## Step 1: the one rule
# *Voltage = number of turns x how fast the flux changes.*  Flux (symbol Phi, unit weber, Wb)
# is the amount of magnetic field passing through the coil. If the flux changes by `delta_flux`
# in a time `delta_t`, a coil of `turns` turns gives an average voltage
#
#     emf = turns * delta_flux / delta_t      (volts)
#
# Check by hand: 200 turns, flux change 0.0005 Wb in 0.05 s gives 200 * 0.0005 / 0.05 = 2 V.
# Twice as fast (0.025 s) gives 4 V. No change of flux, no voltage, however strong the magnet.

# %%
def average_emf(turns, delta_flux, delta_t):
    """Size of the average voltage (V) while the flux changes by delta_flux (Wb) in delta_t (s)."""
    if delta_t <= 0:
        raise ValueError("delta_t must be positive")
    return abs(turns * delta_flux / delta_t)


# %% [markdown]
# ## Step 2: a magnet pushed through a coil
# We model the flux through the coil as a bell-shaped bump: it is largest when the magnet is
# in the middle of the coil and small when the magnet is far away (a simple, illustrative
# shape, not a measurement). The voltage is minus turns times the slope of that curve.
# The minus sign is Lenz's law: the induced voltage opposes the change. Going in, the voltage
# has one sign; coming out, the opposite sign.

# %%
PHI_MAX = 0.001       # flux with the magnet in the middle, Wb (illustrative)
WIDTH = 0.04          # how far (m) the magnet must be from the middle for the flux to halve


def magnet_flux(x):
    """Flux (Wb) through the coil with the magnet at position x (m) from the coil middle."""
    return PHI_MAX / (1.0 + (np.asarray(x, dtype=float) / WIDTH) ** 2)


def magnet_pass(speed, turns, span=0.4, n=4001):
    """Push the magnet through at constant speed (m/s). Returns time (s), flux (Wb), emf (V)."""
    t = np.linspace(0.0, span / speed, n)
    x = -span / 2 + speed * t
    phi = magnet_flux(x)
    emf = -turns * np.gradient(phi, t)
    return t, phi, emf


# %% [markdown]
# ## Step 3: a spinning coil makes alternating voltage
# Turn a coil of area A in a field B. When the coil faces the field the flux is B*A; when it is
# edge-on the flux is zero. Spinning keeps changing the flux, so the voltage keeps changing,
# and it swings positive and negative: **alternating current (AC)**. The peak voltage is
#
#     peak = turns * B * A * 2 pi f      (f = turns per second = frequency in hertz)
#
# Check by hand: 100 turns, B = 0.1 T, A = 0.002 m^2, f = 5 Hz gives
# 100 * 0.1 * 0.002 * 2 pi * 5 = 0.628 V.

# %%
def peak_emf(turns, b_field, area, freq):
    """Peak voltage (V) of a coil of `turns` turns, area (m^2) spinning at freq (Hz) in field b_field (T)."""
    return turns * b_field * area * 2 * np.pi * freq


def rotating_emf(t, turns, b_field, area, freq):
    """Voltage (V) at times t (s). Starts at zero when the coil faces the field."""
    return peak_emf(turns, b_field, area, freq) * np.sin(2 * np.pi * freq * np.asarray(t, dtype=float))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for speed, col in ((0.5, "tab:blue"), (1.0, "tab:red")):
        t, phi, emf = magnet_pass(speed, 200)
        axes[0].plot(t * 1000, emf, color=col, label=f"magnet speed {speed} m/s")
        print(f"speed {speed} m/s: peak voltage {abs(emf).max():.2f} V, passes in {t[-1] * 1000:.0f} ms")
    axes[0].set_xlabel("time (ms)")
    axes[0].set_ylabel("coil voltage (V), 200 turns")
    axes[0].set_title("Faster magnet: bigger, shorter pulse")
    axes[0].grid(alpha=0.3)
    axes[0].legend(fontsize=8)
    tt = np.linspace(0, 0.4, 800)
    for n, col in ((50, "tab:green"), (100, "tab:orange"), (200, "tab:purple")):
        axes[1].plot(tt * 1000, rotating_emf(tt, n, 0.1, AREA, 5), color=col, label=f"{n} turns")
    axes[1].set_xlabel("time (ms)")
    axes[1].set_ylabel("coil voltage (V)")
    axes[1].set_title("Spinning coil (5 Hz, 0.1 T): alternating voltage")
    axes[1].grid(alpha=0.3)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "magnet_and_coil.png", dpi=120)
    print("average emf 200 turns, 0.5 mWb in 0.05 s:", average_emf(200, 0.0005, 0.05), "V")
    print("peak emf 100 turns, 0.1 T, 5 Hz:", round(peak_emf(100, 0.1, AREA, 5), 3), "V")

# %% [markdown]
# ## Where this stops
# Here we only saw *that* the voltage depends on how fast the flux changes. Session 2 turns
# this into Faraday's law with units, gives the exact sine wave, and adds the transformer.
