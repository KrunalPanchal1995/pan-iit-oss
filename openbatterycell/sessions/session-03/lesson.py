"""Session 3 (Level 3): Nernst equation, a discharging cell, maximum power and a short circuit.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a cell that runs down
# **A. Real-world problem.** A cell is not a fixed 1.10 V source. Its voltage depends on how
# much of each chemical is left (the Nernst equation), it sags when current flows (internal
# resistance), it delivers the most power only at one load, and a short circuit turns almost
# all of its energy into heat. Today you simulate all four with one small model and check it
# against Faraday's law and the Nernst limits.
#
# **Plan.** (1) Nernst voltage, (2) concentrations as charge is drawn, (3) terminal voltage
# and the discharge curve, (4) validation, (5) power versus load, temperature and a short circuit.
#
# *Illustrative parameters:* the volume, the internal resistance, the resistance rise as Cu2+
# runs out and the thermal numbers below are chosen for teaching, not measured from a real cell.
# *Safety: real lithium and lead-acid batteries can be dangerous. Educational model only.*

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_GAS = 8.314462618        # J/(mol K)
FARADAY = 96485.0          # C/mol
T0 = 298.15                # K (25 C)
N_E = 2                    # electrons per Zn2+/Cu2+ reaction
E0 = 1.10                  # V, standard Daniell cell voltage
M_ZN = 65.38               # g/mol

# ILLUSTRATIVE cell parameters (not measured)
VOL = 0.020                # L of solution in each half cell
C_CU0 = 1.0                # mol/L Cu2+ at the start
C_ZN0 = 0.1                # mol/L Zn2+ at the start
R_INT0 = 0.8               # ohm, internal resistance at 25 C
K_DEP = 0.05               # resistance rises by K_DEP * C_CU0 / c_Cu as Cu2+ runs out
EA = 20000.0               # J/mol, "activation" energy for how resistance changes with temperature
C_FLOOR = 1e-9            # mol/L, keeps the logarithm finite
Q_MAX = N_E * FARADAY * VOL * C_CU0       # C: charge the Cu2+ in solution can supply


# %% [markdown]
# ## Step 1: the Nernst equation
# For the reaction Zn + Cu2+ -> Zn2+ + Cu the reaction quotient is Q = [Zn2+] / [Cu2+]
# (concentrations in mol/L; pure metals count as 1). The cell voltage is
#
#     E = E0 - (R T / (n F)) ln Q
#
# * R T / F at 25 C is 25.69 mV: every factor e (2.718) in Q changes E by 25.69 mV / n.
# * One *decade* (factor 10) in Q changes E by 2.303 R T / (n F): 59.16 mV for n = 1, and
#   29.58 mV for the Daniell cell (n = 2).

# %%
def area(y, x):
    """Trapezoid-rule integral of y dx (works on every NumPy version)."""
    y, x = np.asarray(y, dtype=float), np.asarray(x, dtype=float)
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))


def thermal_voltage(T=T0, n=1):
    """R T / (n F) in volts."""
    return R_GAS * T / (n * FARADAY)


def nernst(Q, T=T0, e0=E0, n=N_E):
    """Cell voltage in volts for reaction quotient Q (Q > 0)."""
    Q = np.asarray(Q, dtype=float)
    if np.any(Q <= 0):
        raise ValueError("reaction quotient must be positive")
    return e0 - thermal_voltage(T, n) * np.log(Q)


def mv_per_decade(T=T0, n=1):
    return 1000.0 * thermal_voltage(T, n) * np.log(10.0)


# %% [markdown]
# ## Step 2: concentrations while the cell discharges
# Drawing a charge q (coulombs) reacts xi = q / (n F) moles. Each litre of Cu2+ solution loses
# xi / VOL mol and the zinc solution gains the same.

# %%
def concentrations(q):
    xi = np.asarray(q, dtype=float) / (N_E * FARADAY)
    c_zn = C_ZN0 + xi / VOL
    c_cu = np.maximum(C_CU0 - xi / VOL, C_FLOOR)
    return c_zn, c_cu


def ocv(q, T=T0):
    """Open-circuit voltage after charge q has been drawn."""
    c_zn, c_cu = concentrations(q)
    return nernst(c_zn / c_cu, T)


# %% [markdown]
# ## Step 3: terminal voltage and the discharge curve
# With a load resistance `R` the current is I = E / (R + r) and the voltage you can use is
# V = E - I r (the terminal voltage). The internal resistance `r` is larger when cold
# (an Arrhenius-type factor, illustrative) and rises as Cu2+ runs out (illustrative).

# %%
def r_internal(q, T=T0, r0=R_INT0):
    _, c_cu = concentrations(q)
    temp_factor = np.exp(EA / R_GAS * (1.0 / T - 1.0 / T0))
    return r0 * temp_factor * (1.0 + K_DEP * C_CU0 / c_cu)


def current(q, R, T=T0, r0=R_INT0):
    return ocv(q, T) / (R + r_internal(q, T, r0))


def terminal_voltage(q, R, T=T0, r0=R_INT0):
    return ocv(q, T) - current(q, R, T, r0) * r_internal(q, T, r0)


def discharge_curve(R, T=T0, r0=R_INT0, n=3001):
    """Quasi-static discharge in the charge domain. Returns arrays q, e, i, v and time t."""
    u = np.linspace(0.0, 1.0, n)
    q = Q_MAX * (1.0 - 1e-4) * (1.0 - (1.0 - u) ** 4)          # denser near the end
    e, i, v = ocv(q, T), current(q, R, T, r0), terminal_voltage(q, R, T, r0)
    t = np.concatenate([[0.0], np.cumsum(0.5 * (1 / i[1:] + 1 / i[:-1]) * np.diff(q))])
    return {"q": q, "e": e, "i": i, "v": v, "t": t, "r": r_internal(q, T, r0)}


def usable_capacity_ah(R, T=T0, r0=R_INT0, drop=0.10):
    """Charge drawn (Ah) before the terminal voltage has fallen by `drop` from its starting value."""
    c = discharge_curve(R, T, r0)
    target = (1.0 - drop) * c["v"][0]
    idx = np.nonzero(c["v"] < target)[0]
    if len(idx) == 0:
        return float(c["q"][-1] / 3600.0)
    j = idx[0]
    q_cut = np.interp(target, [c["v"][j], c["v"][j - 1]], [c["q"][j], c["q"][j - 1]])
    return float(q_cut / 3600.0)


def energy_wh(R, T=T0, r0=R_INT0, drop=0.10):
    """Energy delivered to the load (Wh) until the cutoff defined by `drop`."""
    c = discharge_curve(R, T, r0, n=6001)
    target = (1.0 - drop) * c["v"][0]
    m = c["v"] >= target
    q, v = c["q"][m], c["v"][m]
    return float(area(v, q) / 3600.0)


# %% [markdown]
# ## Step 4: validation against Faraday and Nernst
# 1. **Time-domain solver.** Solve dq/dt = I(q) with fourth-order Runge-Kutta and compare
#    with the charge-domain result (time = integral of dq / I).
# 2. **Faraday's law.** The zinc dissolved, found from the concentration change, equals
#    Q M / (n F) from the charge that flowed.
# 3. **Energy balance.** chemical energy integral of E dq = delivered integral of V dq + heat integral of I r dq.

# %%
def rk4_charge(R, t_end, steps=2000, T=T0, r0=R_INT0):
    """Charge (C) drawn after t_end seconds, from dq/dt = I(q) solved with RK4."""
    h = t_end / steps
    q = 0.0
    for _ in range(steps):
        k1 = current(q, R, T, r0)
        k2 = current(q + 0.5 * h * k1, R, T, r0)
        k3 = current(q + 0.5 * h * k2, R, T, r0)
        k4 = current(q + h * k3, R, T, r0)
        q += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
    return float(q)


def zinc_from_concentration(q):
    """Zinc dissolved (g), found from how much Zn2+ the solution gained."""
    c_zn, _ = concentrations(q)
    return float((c_zn - C_ZN0) * VOL * M_ZN)


def zinc_from_faraday(q):
    return float(q * M_ZN / (N_E * FARADAY))


def energy_balance(R, T=T0, r0=R_INT0):
    """(chemical, delivered, heat) in joules over the whole discharge curve."""
    c = discharge_curve(R, T, r0, n=6001)
    return (float(area(c["e"], c["q"])), float(area(c["v"], c["q"])), float(area(c["i"] * c["r"], c["q"])))


def pack_runtime_hours(ns, npar, R_lamp, v_min, T=T0, r0=R_INT0, n=4001):
    """Hours a lamp of resistance R_lamp stays at or above v_min volts when powered by a pack of
    `ns` cells in series per string and `npar` identical strings in parallel (same model per cell)."""
    if ns < 1 or npar < 1:
        raise ValueError("a pack needs at least one cell")
    u = np.linspace(0.0, 1.0, n)
    q = Q_MAX * (1.0 - 1e-4) * (1.0 - (1.0 - u) ** 4)          # charge drawn from each cell
    e, r = ocv(q, T), r_internal(q, T, r0)
    i_total = ns * e / (R_lamp + ns * r / npar)
    v_lamp = i_total * R_lamp
    if v_lamp[0] < v_min:
        return 0.0
    bad = np.nonzero(v_lamp < v_min)[0]
    j = bad[0] if len(bad) else n - 1
    i_string = i_total / npar
    dt = 0.5 * (1 / i_string[1:j + 1] + 1 / i_string[:j]) * np.diff(q[:j + 1])
    return float(np.sum(dt) / 3600.0)


# %% [markdown]
# ## Step 5: power, temperature and a short circuit
# Delivered power is P = I^2 R = E^2 R / (R + r)^2. It is largest when R = r, where
# P_max = E^2 / (4 r), and the efficiency R / (R + r) is then only 50 percent: half the chemical
# energy is heat inside the cell. A short circuit (R near 0) gives I = E / r and heat I^2 r,
# which warms the cell according to a simple lumped model (illustrative numbers):
#
#     C_th dT/dt = I^2 r - hA (T - T_ambient)

# %%
def load_power(E, r, R):
    R = np.asarray(R, dtype=float)
    return E ** 2 * R / (R + r) ** 2


def efficiency(r, R):
    R = np.asarray(R, dtype=float)
    return R / (R + r)


def short_circuit_heating(E, r, C_th, hA, t_end, dt=0.5, T_amb=25.0):
    """Cell temperature (C) versus time for a dead short. Illustrative lumped model (explicit Euler)."""
    if r <= 0 or C_th <= 0:
        raise ValueError("resistance and heat capacity must be positive")
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    T = np.empty(n + 1)
    T[0] = T_amb
    heat = (E / r) ** 2 * r
    for k in range(n):
        T[k + 1] = T[k] + dt * (heat - hA * (T[k] - T_amb)) / C_th
    return t, T


def short_circuit_exact(E, r, C_th, hA, t, T_amb=25.0):
    """Closed form of the same model, used to check the numerical one."""
    heat = (E / r) ** 2 * r
    return T_amb + heat / hA * (1.0 - np.exp(-np.asarray(t) * hA / C_th))


# %% [markdown]
# ## Step 6: many cycles, a little capacity lost each time
# A rechargeable cell is discharged, recharged to full, discharged again. Each cycle permanently
# loses a small fraction `loss` of the capacity that is left (0.2 percent per cycle is typical of
# a modest cell; real fade is not constant). Because the loss is a *fraction of what remains*,
# the capacity after n cycles is geometric:  f(n) = (1 - loss)^n.  After 50 cycles of 0.2 percent
# that is 0.998^50 = 0.9047, i.e. 90.5 percent. (A loss of 0.2 percent of the *original*
# capacity per cycle would give exactly 90.0 percent: the two differ because the second takes
# the same bite every time.) An aged cell behaves like a smaller cell: the same voltage curve,
# stretched shorter along the charge axis by f, so the usable capacity and the energy per
# discharge both scale with f.

# %%
LOSS_PER_CYCLE = 0.002


def capacity_fraction(n, loss=LOSS_PER_CYCLE):
    """Capacity left after n cycles as a fraction of the new cell: (1 - loss)^n."""
    return (1.0 - loss) ** np.asarray(n, dtype=float)


def cycles_to_fraction(target=0.8, loss=LOSS_PER_CYCLE):
    """Whole cycles after which the capacity first falls to `target` or below (end of life at 0.8)."""
    if not 0.0 < loss < 1.0 or not 0.0 < target < 1.0:
        raise ValueError("loss and target must lie strictly between 0 and 1")
    return int(np.ceil(np.log(target) / np.log(1.0 - loss) - 1e-12))


def cycle_life(R, n_cycles, loss=LOSS_PER_CYCLE, T=T0, r0=R_INT0, drop=0.10):
    """Simulate n_cycles of discharge (to the `drop` cutoff) and full recharge, cycle by cycle.

    Returns arrays: cycle number 1..n, capacity fraction at the start of each cycle, usable
    capacity (Ah) and energy (Wh) delivered in that cycle. The fresh-cell numbers are computed once."""
    ah0, wh0 = usable_capacity_ah(R, T, r0, drop), energy_wh(R, T, r0, drop)
    frac = 1.0
    cyc, fr, ah, wh = [], [], [], []
    for k in range(1, int(n_cycles) + 1):
        cyc.append(k)
        fr.append(frac)
        ah.append(ah0 * frac)
        wh.append(wh0 * frac)
        frac *= (1.0 - loss)             # recharge restores the starting concentrations, minus the permanent loss
    return {"cycle": np.array(cyc), "fraction": np.array(fr), "ah": np.array(ah), "wh": np.array(wh)}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print(f"RT/F at 25 C = {1000 * thermal_voltage():.3f} mV per e-fold (n = 1)")
    print(f"decade, n = 1: {mv_per_decade(T0, 1):.2f} mV;  n = 2 (Daniell): {mv_per_decade(T0, 2):.2f} mV")
    print(f"E at Q = 0.1: {float(nernst(0.1)):.4f} V;  at Q = 1: {float(nernst(1.0)):.4f} V;  at Q = 10: {float(nernst(10.0)):.4f} V")
    print(f"capacity from Cu2+: {Q_MAX:.0f} C = {Q_MAX / 3600:.3f} Ah")

    # figure 1: Nernst sweep
    logq = np.linspace(-4, 4, 161)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(logq, nernst(10.0 ** logq), color="#2a6fdb", label="25 C")
    ax.plot(logq, nernst(10.0 ** logq, T=273.15), "--", color="#2a9d8f", label="0 C")
    ax.plot(logq, nernst(10.0 ** logq, T=323.15), ":", color="#d9534f", label="50 C")
    ax.axhline(E0, color="gray", lw=0.8)
    ax.set_xlabel("log10 of Q = [Zn2+] / [Cu2+]")
    ax.set_ylabel("Daniell cell voltage E (V)")
    ax.set_title(f"Nernst: a straight line, {mv_per_decade(T0, 2):.1f} mV per decade at 25 C", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "nernst_sweep.png", dpi=120)

    # figure 2: discharge curves
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for R, col in ((2.0, "#d9534f"), (10.0, "#2a6fdb"), (40.0, "#2a9d8f")):
        c = discharge_curve(R)
        ax2.plot(c["q"] / 3600.0, c["v"], color=col, label=f"load {R:g} ohm: {usable_capacity_ah(R):.2f} Ah to -10%")
    ax2.plot(c["q"] / 3600.0, c["e"], "k:", lw=1, label="open-circuit voltage E")
    ax2.set_xlabel("charge drawn (Ah)")
    ax2.set_ylabel("terminal voltage V = E - I r (V)")
    ax2.set_ylim(0.0, 1.25)
    ax2.set_title("Discharge curves (illustrative parameters)", fontsize=10)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8, loc="lower left")
    fig2.tight_layout()
    fig2.savefig(OUT / "discharge_curve.png", dpi=120)

    # figure 3: power and efficiency versus load
    Rs = np.linspace(0.05, 6.0, 300)
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.2))
    ax3.plot(Rs, load_power(E0, R_INT0, Rs), color="#2a6fdb", label="power to the load (W)")
    ax3.set_xlabel("load resistance R (ohm)")
    ax3.set_ylabel("power (W)", color="#2a6fdb")
    ax3b = ax3.twinx()
    ax3b.plot(Rs, 100 * efficiency(R_INT0, Rs), color="#d9534f", label="efficiency (%)")
    ax3b.set_ylabel("efficiency (%)", color="#d9534f")
    ax3.axvline(R_INT0, color="gray", ls="--")
    ax3.set_title(f"Maximum power at R = r = {R_INT0} ohm: {float(load_power(E0, R_INT0, R_INT0)):.3f} W at 50 %", fontsize=10)
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "power_vs_load.png", dpi=120)

    # figure 4: short circuit
    fig4, ax4 = plt.subplots(figsize=(6.4, 4.2))
    for r, col in ((0.8, "#2a9d8f"), (0.05, "#d9534f")):
        t, T = short_circuit_heating(E0, r, C_th=40.0, hA=0.15, t_end=300.0)
        ax4.plot(t, T, color=col, label=f"r = {r} ohm: I = {E0 / r:.1f} A, heat {E0 ** 2 / r:.1f} W")
        print(f"short circuit r = {r}: I = {E0 / r:.2f} A, heat {E0 ** 2 / r:.2f} W, temperature after 60 s = {T[120]:.1f} C, after 300 s = {T[-1]:.1f} C")
    ax4.set_xlabel("time after the short (s)")
    ax4.set_ylabel("cell temperature (C)")
    ax4.set_title("Short circuit: lumped heating (illustrative numbers)", fontsize=10)
    ax4.grid(alpha=0.3)
    ax4.legend(fontsize=8)
    fig4.tight_layout()
    fig4.savefig(OUT / "short_circuit.png", dpi=120)

    # figure 5: capacity over many cycles
    ncyc = np.arange(0, 201)
    fig5, ax5 = plt.subplots(figsize=(6.4, 4.2))
    ax5.plot(ncyc, 100 * capacity_fraction(ncyc), color="#003f7f", lw=2, label="0.2 % of what is left per cycle")
    ax5.plot(ncyc, 100 * (1 - LOSS_PER_CYCLE * ncyc), "--", color="#c86a00", label="0.2 % of the original per cycle")
    ax5.axhline(80, color="gray", ls=":")
    ax5.plot([50], [100 * capacity_fraction(50)], "o", color="#d81b60")
    ax5.annotate(f"{100 * capacity_fraction(50):.1f} % after 50 cycles", (50, 100 * capacity_fraction(50)), (62, 93), fontsize=9)
    n80 = cycles_to_fraction(0.8)
    ax5.annotate(f"80 % after {n80} cycles", (n80, 80), (n80 + 8, 82), fontsize=9)
    ax5.set_xlabel("cycle number")
    ax5.set_ylabel("capacity (% of a new cell)")
    ax5.set_title("Capacity fade: geometric loss against straight-line loss", fontsize=10)
    ax5.set_ylim(60, 101)
    ax5.grid(alpha=0.3)
    ax5.legend(fontsize=8, loc="lower left")
    fig5.tight_layout()
    fig5.savefig(OUT / "capacity_fade.png", dpi=120)
    cl = cycle_life(10.0, n80)
    print(f"cycles to 80 %: {n80};  after 50 cycles: {100 * capacity_fraction(50):.2f} %;  10 ohm load: {cl['ah'][0]:.3f} Ah at cycle 1, {cl['ah'][49]:.3f} Ah at cycle 50;  energy over life to 80 %: {cl['wh'].sum():.1f} Wh")

    # numbers quoted in the lesson text
    for R in (2.0, 10.0, 40.0):
        c = discharge_curve(R)
        print(f"load {R:g} ohm: start V = {c['v'][0]:.3f} V, I = {c['i'][0]:.3f} A, usable {usable_capacity_ah(R):.3f} Ah, energy {energy_wh(R):.3f} Wh, time {c['t'][-1] / 3600:.2f} h")
    print(f"P_max = {float(load_power(E0, R_INT0, R_INT0)):.4f} W at R = {R_INT0}")
    for Tc in (0, 25, 45):
        print(f"{Tc} C: r(0) = {float(r_internal(0.0, Tc + 273.15)):.3f} ohm, V_term at 10 ohm = {float(terminal_voltage(0.0, 10.0, Tc + 273.15)):.3f} V")

# %% [markdown]
# ## Where this stops
# Real cells have diffusion limits, side reactions, electrode surface effects and ageing that
# this model leaves out. The shape of a discharge curve differs between chemistries. Use
# this to understand, never to design or test a real battery.
