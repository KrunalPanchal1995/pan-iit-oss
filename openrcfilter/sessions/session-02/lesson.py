"""Session 2 (Level 2): the RC low-pass in numbers: tau, cutoff, gain, phase, decibels.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: the RC low-pass in numbers
# **A. Real-world problem.** Mains wiring leaks a 50 Hz hum into a sensor wire. Which R and C
# remove it, how many decibels does a given filter really remove, and what does the next
# circuit in the chain do to the filter?
#
# **Plan.** (1) tau and the step response, (2) cutoff frequency, gain and phase, (3) decibels
# and the Bode plot, (4) a design problem, (5) the loading effect.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: time constant and step response
# Apply a sudden 1 V step to the input. The capacitor charges through R:
# `v(t) = 1 - exp(-t / tau)` with `tau = R C`. After one tau it has reached 63.2 percent;
# after 3 tau, 95.0 percent.

# %%
def time_constant(R, C):
    """tau = R C in seconds (R in ohms, C in farads)."""
    return R * C


def step_response(t, tau):
    """Output voltage (volts) at time t for a 1 V input step at t = 0."""
    return 1.0 - np.exp(-np.asarray(t, dtype=float) / tau)


def step_response_numeric(tau, dt, n):
    """The same curve found by stepping dv/dt = (1 - v) / tau forward in small steps (Euler)."""
    v = np.zeros(n + 1)
    for i in range(n):
        v[i + 1] = v[i] + dt * (1.0 - v[i]) / tau
    return v


# %% [markdown]
# ## Step 2: cutoff frequency, gain and phase
# Drive the filter with a sine of frequency f. The output is a sine of the same frequency with
# a different size (gain) and shifted in time (phase). With `f_c = 1 / (2 pi R C)`:
# `|H| = 1 / sqrt(1 + (f / f_c)^2)` and `phase = -atan(f / f_c)`.

# %%
def cutoff_hz(R, C):
    """Cutoff frequency f_c = 1 / (2 pi R C) in hertz."""
    return 1.0 / (2.0 * np.pi * R * C)


def gain(f, fc):
    """Size of the output sine divided by the size of the input sine (no unit)."""
    return 1.0 / np.sqrt(1.0 + (np.asarray(f, dtype=float) / fc) ** 2)


def phase_deg(f, fc):
    """Phase shift of the output relative to the input, in degrees (negative = output is late)."""
    return -np.degrees(np.arctan(np.asarray(f, dtype=float) / fc))


# %% [markdown]
# ## Step 3: decibels and the Bode plot
# `gain_dB = 20 log10(|H|)`. A Bode plot draws gain_dB (and phase) against frequency on a
# logarithmic axis. Far above f_c the gain falls 10 times for every 10 times in frequency,
# which is -20 dB per decade; exactly at f_c the gain is 0.7071, which is -3.01 dB.

# %%
def gain_db(f, fc):
    return 20.0 * np.log10(gain(f, fc))


def rolloff_db_per_decade(fc, f_start):
    """Change of gain in dB when the frequency goes from f_start to 10 f_start."""
    return float(gain_db(10 * f_start, fc) - gain_db(f_start, fc))


# %% [markdown]
# ## Step 4: a design problem
# Choose C, compute R for the wanted cutoff, round R to a stock value (the E24 series), and
# ask honestly how many dB of 50 Hz hum the result removes.

# %%
E24 = [10, 11, 12, 13, 15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 75, 82, 91]


def design_R(fc, C):
    """Resistance (ohms) that gives cutoff fc (hertz) with capacitance C (farads)."""
    return 1.0 / (2.0 * np.pi * fc * C)


def nearest_e24(value):
    """Nearest stock value of the E24 series (same unit as value)."""
    decade = 10.0 ** np.floor(np.log10(value))
    candidates = [m / 10.0 * decade for m in E24] + [decade * 10.0, decade]
    return float(min(candidates, key=lambda c: abs(np.log(c / value))))


def hum_removed_db(fc, f_hum=50.0):
    """Attenuation in dB (positive number) that the filter gives at the hum frequency."""
    return float(-gain_db(f_hum, fc))


def fc_for_attenuation(att_db, f_hum=50.0):
    """Cutoff (hertz) that attenuates f_hum by att_db decibels."""
    g = 10.0 ** (-att_db / 20.0)
    return float(f_hum / np.sqrt(1.0 / g ** 2 - 1.0))


# %% [markdown]
# ## Step 5: the loading effect
# A circuit connected to the output (a load of resistance R_L) is in parallel with the
# capacitor. Seen from the capacitor, the resistor R and the load R_L are in parallel for the
# cutoff, and they divide the voltage at DC: `gain(0) = R_L / (R + R_L)` and
# `f_c = 1 / (2 pi (R || R_L) C)`.

# %%
def loaded_rc(R, C, R_load):
    """(DC gain, cutoff in hertz) of an RC low-pass that drives a resistive load R_load."""
    r_par = R * R_load / (R + R_load)
    return R_load / (R + R_load), 1.0 / (2.0 * np.pi * r_par * C)


def loaded_gain(f, R, C, R_load):
    g0, fc = loaded_rc(R, C, R_load)
    return g0 * gain(f, fc)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    R, C = 16e3, 100e-9
    tau, fc = time_constant(R, C), cutoff_hz(R, C)
    print(f"R = 16 kohm, C = 100 nF: tau = {tau * 1000:.2f} ms, f_c = {fc:.2f} Hz")
    print(f"step at 1 tau: {float(step_response(tau, tau)):.4f}, at 3 tau: {float(step_response(3 * tau, tau)):.4f}")
    print(f"gain at f_c = {float(gain(fc, fc)):.4f} = {float(gain_db(fc, fc)):.2f} dB, "
          f"phase = {float(phase_deg(fc, fc)):.1f} deg")
    print(f"50 Hz hum: gain {float(gain(50, fc)):.4f}, removed {hum_removed_db(fc):.2f} dB")
    print(f"ideal R for 100 Hz with 100 nF: {design_R(100, C):.0f} ohm; nearest E24: "
          f"{nearest_e24(design_R(100, C) / 1000):.0f} kohm")
    print(f"cutoff needed to remove 50 Hz hum by 20 dB: {fc_for_attenuation(20):.3f} Hz")
    g0, fl = loaded_rc(16e3, 100e-9, 16e3)
    print(f"load of 16 kohm: DC gain {g0:.2f}, f_c = {fl:.1f} Hz")

    t = np.linspace(0, 6 * tau, 300)
    f = np.logspace(0, 4, 400)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    ax[0].plot(t * 1000, step_response(t, tau), color="C0", lw=2, label="1 - exp(-t / tau)")
    tn = np.arange(0, 6 * tau + 1e-12, tau / 200)
    ax[0].plot(tn * 1000, step_response_numeric(tau, tau / 200, len(tn) - 1), "k:", lw=1.2, label="numeric check")
    ax[0].axhline(0.632, color="0.6", ls="--", lw=1)
    ax[0].axvline(tau * 1000, color="0.6", ls="--", lw=1)
    ax[0].set_xlabel("time (ms)")
    ax[0].set_ylabel("output voltage (V) for a 1 V step")
    ax[0].set_title("Step response: 63.2 % after one tau = 1.6 ms")
    ax[0].grid(alpha=0.3)
    ax[0].legend(loc="lower right")
    ax[1].semilogx(f, gain_db(f, fc), color="C0", lw=2, label="gain (dB)")
    ax[1].axvline(fc, color="0.6", ls="--", lw=1)
    ax[1].axhline(-3.01, color="0.6", ls="--", lw=1)
    ax[1].plot([fc], [-3.01], "ro")
    ax[1].plot([50], [float(gain_db(50, fc))], "gs", label="50 Hz hum")
    ax[1].set_xlabel("frequency (Hz)")
    ax[1].set_ylabel("gain (dB)")
    ax[1].set_ylim(-50, 3)
    ax[1].set_title("Bode gain: -3 dB at f_c = 99.5 Hz, then -20 dB per decade")
    ax[1].grid(alpha=0.3, which="both")
    ax2 = ax[1].twinx()
    ax2.semilogx(f, phase_deg(f, fc), color="C1", lw=1.5, ls="-.")
    ax2.set_ylabel("phase (degrees)", color="C1")
    ax2.set_ylim(-95, 5)
    ax[1].legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "step_and_bode.png", dpi=120)

    fcs = np.logspace(-0.5, 2.3, 200)
    fig2, ax3 = plt.subplots(figsize=(6.4, 3.8))
    ax3.semilogx(fcs, [hum_removed_db(c) for c in fcs], color="C3", lw=2)
    ax3.axhline(20, color="0.6", ls="--", lw=1)
    ax3.axvline(fc_for_attenuation(20), color="0.6", ls="--", lw=1)
    ax3.set_xlabel("cutoff frequency f_c (Hz)")
    ax3.set_ylabel("50 Hz hum removed (dB)")
    ax3.set_title("A cutoff of 100 Hz removes only 1 dB; 20 dB needs 5 Hz")
    ax3.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(OUT / "hum_removed.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
