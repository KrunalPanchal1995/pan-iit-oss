"""Session 2 (Level 2): Faraday's law, the sine wave of a rotating coil, RMS, and the ideal transformer.

Run:  python start.py 2
Low-voltage educational model only (never mains). Ideal coil and ideal transformer.
"""
# %% [markdown]
# # Session 2: Faraday's law with numbers
# **A. Real-world problem.** You want a hand-crank torch with no battery. How many turns of wire,
# how strong a magnet and how fast a crank give a few volts? And your phone charger must turn
# 230 V from the wall socket into a safe low voltage: how many turns on each side?
#
# **Plan.** (1) flux and Faraday's law, (2) the exact sine wave of a rotating coil and its RMS
# value, (3) the ideal transformer and a design to a requirement.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: flux and Faraday's law
# Flux through a flat coil of area A (m^2) in a uniform field B (tesla, T) whose direction makes
# an angle theta with the coil's normal: Phi = B A cos(theta)  (weber, Wb).
# Faraday's law: EMF = - N dPhi/dt (volts), with N the number of turns.
# We spin the coil at constant angular speed w = 2 pi f (rad/s) so theta = w t.

# %%
def flux(b_field, area, theta):
    """Flux (Wb) through one turn; theta in radians from the field direction."""
    return b_field * area * np.cos(theta)


def rotating_flux(t, b_field, area, freq):
    return flux(b_field, area, 2 * np.pi * freq * np.asarray(t, dtype=float))


def emf_numeric(t, turns, b_field, area, freq):
    """EMF = -N dPhi/dt computed by a numerical derivative (central differences)."""
    t = np.asarray(t, dtype=float)
    return -turns * np.gradient(rotating_flux(t, b_field, area, freq), t)


# %% [markdown]
# ## Step 2: the exact answer for a rotating coil
# Differentiating B A cos(w t) gives  EMF = N B A w sin(w t).  Peak value N B A w.
# RMS (the 'heating equivalent' value) of a sine = peak / sqrt(2).
# Hand-crank torch: 400 turns, B = 0.15 T, A = 0.002 m^2, coil at f = 10 Hz
# (crank 2 rev/s with a 5 : 1 gear). Peak = 400 * 0.15 * 0.002 * 2 pi * 10 = 7.54 V,
# RMS = 5.33 V.

# %%
def omega(freq):
    return 2 * np.pi * freq


def peak_emf(turns, b_field, area, freq):
    return turns * b_field * area * omega(freq)


def emf(t, turns, b_field, area, freq):
    return peak_emf(turns, b_field, area, freq) * np.sin(omega(freq) * np.asarray(t, dtype=float))


def rms_from_peak(peak):
    return peak / np.sqrt(2.0)


def rms_numeric(wave):
    """Root mean square of samples covering a whole number of periods."""
    return float(np.sqrt(np.mean(np.asarray(wave, dtype=float) ** 2)))


def period(freq):
    return 1.0 / freq


# %% [markdown]
# ## Step 3: the ideal transformer
# Two coils on one iron core share the same changing flux, so each turn gets the same voltage:
#     V2 / V1 = N2 / N1.
# An ideal transformer wastes nothing: P1 = V1 I1 = V2 I2 = P2, so I2 / I1 = N1 / N2.
# It only works with changing (AC) flux: with steady DC the flux does not change and V2 = 0.

# %%
def secondary_voltage(v1, n1, n2):
    return v1 * n2 / n1


def secondary_current(i1, n1, n2):
    return i1 * n1 / n2


def design_transformer(v1, v2, power, n2):
    """Primary turns, and the currents, for an ideal transformer giving v2 volts at `power` watts."""
    if min(v1, v2, power, n2) <= 0:
        raise ValueError("all inputs must be positive")
    n1 = n2 * v1 / v2
    i2 = power / v2
    i1 = power / v1
    return {"n1": n1, "n2": n2, "i1": i1, "i2": i2, "ratio": v1 / v2}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    N, B, FREQ = 400, 0.15, 10.0
    area = 0.002
    t = np.linspace(0, 2 * period(FREQ), 2001)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax1.plot(t * 1000, rotating_flux(t, B, area, FREQ) * 1000, color="tab:blue")
    ax1.set_ylabel("flux through one turn (mWb)")
    ax1.set_title("Flux and EMF of a hand-crank coil (400 turns, 0.15 T, 10 Hz)")
    ax1.grid(alpha=0.3)
    ax2.plot(t * 1000, emf(t, N, B, area, FREQ), color="tab:red", label="N B A w sin(w t)")
    ax2.plot(t[::40] * 1000, emf_numeric(t, N, B, area, FREQ)[::40], "k.", label="-N dPhi/dt (numerical)")
    ax2.axhline(rms_from_peak(peak_emf(N, B, area, FREQ)), color="gray", ls="--", label="RMS = peak / sqrt(2)")
    ax2.axhline(-rms_from_peak(peak_emf(N, B, area, FREQ)), color="gray", ls="--")
    ax2.set_xlabel("time (ms)")
    ax2.set_ylabel("EMF (V)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "flux_and_emf.png", dpi=120)
    pk = peak_emf(N, B, area, FREQ)
    print(f"hand crank: peak {pk:.2f} V, RMS {rms_from_peak(pk):.2f} V, period {period(FREQ) * 1000:.0f} ms")

    d = design_transformer(230.0, 12.0, 24.0, 24)
    print("design 230 V -> 12 V, 24 W:", {k: round(v, 4) for k, v in d.items()})
    t50 = np.linspace(0, 0.04, 2001)
    v1 = 230 * np.sqrt(2) * np.sin(omega(50) * t50)
    v2 = secondary_voltage(v1, d["n1"], d["n2"])
    fig2, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t50 * 1000, v1, color="tab:blue", label="primary 230 V RMS (460 turns)")
    ax.plot(t50 * 1000, v2, color="tab:red", label="secondary 12 V RMS (24 turns)")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("voltage (V)")
    ax.set_title("Ideal step-down transformer, 50 Hz")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "transformer_waveforms.png", dpi=120)
    print(f"mains peak {230 * np.sqrt(2):.1f} V, secondary peak {12 * np.sqrt(2):.2f} V, period at 50 Hz {period(50) * 1000:.0f} ms")

# %% [markdown]
# ## Where this stops
# The sine wave and the ideal transformer are exact only for lossless parts. Session 3 adds coil
# resistance and inductance, solves the circuit in time, and counts the losses.
