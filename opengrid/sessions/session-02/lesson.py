"""Session 2 (Level 2): AC power, power factor, correction and line losses.

Run:  python start.py 2
Simplified single-phase maths for learning. Real installations must be designed by qualified engineers.
"""
# %% [markdown]
# # Session 2: real power, reactive power and power factor
# **A. Real-world problem.** A workshop pulls 100 kW from a 400 V supply, but its motors make the
# current lag the voltage. The supply cable must carry far more current than 100 kW / 400 V
# would suggest, and the utility charges a penalty for a low power factor. A bank of capacitors
# fixes it. How big must the bank be, and why does high-voltage transmission lose less power?
#
# **Plan.** (1) the power triangle, (2) current at a given power factor, (3) capacitor
# correction, (4) line loss I^2 R at two voltages, (5) a design problem.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the power triangle
# Voltage V and current I (both RMS) are sine waves, with the current lagging by the angle phi.
#   real power      P = V I cos(phi)    (watts, does the useful work)
#   reactive power  Q = V I sin(phi)    (var, swaps back and forth with motor/coil fields)
#   apparent power  S = V I             (volt-amperes, what the wires must carry)
# They form a right triangle: S^2 = P^2 + Q^2, and the power factor pf = cos(phi) = P / S.

# %%
def power_triangle(v_rms, i_rms, phi_deg):
    """Return (P, Q, S, pf) for RMS voltage (V), RMS current (A) and lag angle (degrees)."""
    phi = np.radians(phi_deg)
    s = v_rms * i_rms
    return s * np.cos(phi), s * np.sin(phi), s, float(np.cos(phi))


def current_for(p_watts, v_rms, pf):
    """RMS current (A) a single-phase load needs for real power P at power factor pf: I = P / (V pf)."""
    return p_watts / (v_rms * pf)


def reactive_for(p_watts, pf):
    """Reactive power Q (var) of a load with real power P and power factor pf (lagging)."""
    return p_watts * np.tan(np.arccos(pf))


# %% [markdown]
# ## Step 2: correcting with a capacitor
# A capacitor supplies reactive power locally, so the supply does not have to. To lift the power
# factor from pf1 to pf2 without changing P:
#   Qc = P (tan phi1 - tan phi2),   and for a capacitor C across the load   Qc = 2 pi f C V^2
#   so   C = Qc / (2 pi f V^2).
# Check by hand for 100 kW, pf 0.70 to 0.95: tan phi1 = 1.0202, tan phi2 = 0.3287, so Qc = 69.15 kvar.

# %%
def capacitor_kvar(p_watts, pf1, pf2):
    """Reactive power (var) a capacitor bank must supply to lift pf1 to pf2 at constant P."""
    return p_watts * (np.tan(np.arccos(pf1)) - np.tan(np.arccos(pf2)))


def capacitance_for(qc_var, v_rms, freq=50.0):
    """Capacitance (farad) that gives qc_var at v_rms across it: C = Qc / (2 pi f V^2)."""
    return qc_var / (2.0 * np.pi * freq * v_rms ** 2)


# %% [markdown]
# ## Step 3: why transmission uses high voltage
# For the same power, a higher voltage means a smaller current, and the line heats up with
# the square of the current: loss = I^2 R. Ten times the voltage means one tenth of the
# current and one hundredth of the loss.

# %%
def line_loss(p_watts, v_rms, r_line, pf=1.0):
    """Power lost (W) in a line of resistance r_line (ohm) that delivers P at v_rms (single-phase)."""
    i = current_for(p_watts, v_rms, pf)
    return i * i * r_line


# %% [markdown]
# ## Step 4: see it
# Left: the power triangle before and after correction (P stays, Q shrinks, S shrinks).
# Right: current needed for 100 kW as the power factor falls.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    P, V = 100e3, 400.0
    for pf in (0.7, 0.95):
        print(f"100 kW at {V:.0f} V, pf {pf}: I = {current_for(P, V, pf):.1f} A, Q = {reactive_for(P, pf) / 1e3:.2f} kvar")
    qc = capacitor_kvar(P, 0.7, 0.95)
    print(f"capacitor: Qc = {qc / 1e3:.2f} kvar, C = {capacitance_for(qc, V) * 1e6:.0f} microfarad")
    qd = capacitor_kvar(50e3, 0.75, 0.95)
    print(f"design: 50 kW, pf 0.75 to 0.95: Qc = {qd / 1e3:.2f} kvar, C = {capacitance_for(qd, V) * 1e6:.0f} microfarad")
    for vv in (10e3, 100e3):
        print(f"1 MW over a 5 ohm line at {vv / 1e3:.0f} kV: loss = {line_loss(1e6, vv, 5.0):.0f} W")

    fig, ax = plt.subplots(figsize=(5.5, 5))
    q1, q2 = reactive_for(P, 0.7) / 1e3, reactive_for(P, 0.95) / 1e3
    ax.plot([0, 100, 100, 0], [0, 0, q1, 0], "r-", label=f"before: pf 0.70, S = {np.hypot(100, q1):.0f} kVA")
    ax.plot([0, 100, 0], [0, q2, 0], "g-", label=f"after: pf 0.95, S = {np.hypot(100, q2):.0f} kVA")
    ax.plot([100, 100], [q2, q1], "b:", lw=3, label=f"capacitor Qc = {q1 - q2:.1f} kvar")
    ax.set_xlabel("real power P (kW)")
    ax.set_ylabel("reactive power Q (kvar)")
    ax.set_title("Power triangle before and after correction")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "power_triangle.png", dpi=120)

    pfs = np.linspace(0.5, 1.0, 51)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(pfs, current_for(P, V, pfs))
    ax2.set_xlabel("power factor")
    ax2.set_ylabel("current for 100 kW at 400 V (A)")
    ax2.set_title("Low power factor needs more current")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "current_vs_pf.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Change the load to 80 kW and the target pf to 0.98. Then answer the four questions in the
# README (section F) and run the checkpoint.
