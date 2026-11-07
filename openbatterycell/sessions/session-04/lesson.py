"""Session 4 (Level 3): a cold-proof lamp pack. How temperature changes internal resistance and what a designer does about it.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: a cold-proof lamp pack
# **A. Real-world problem.** A small lamp (30 ohm) needs at least 9 V across it for at least 5 hours.
# In Session 3 the smallest pack of our zinc-copper cells that does the job at 25 C has 20 cells
# (10 in series x 2 in parallel). Carry it outside at 0 C and the lamp never reaches 9 V: the pack
# gives 0 hours. Cold cells have a much larger internal resistance. This session finds out how
# much larger, designs a pack that works at 0, 25 and 45 C, and shows what a designer can do to
# make that pack smaller than the 24 cells a plain search needs.
#
# **Plan.** (1) resistance against temperature, (2) the pack as one equivalent cell, (3) why
# a pack fails (and how), (4) a design search across temperatures, (5) validate the pack model with
# an independent solver and an exact equivalence, (6) design levers: a cell with lower
# resistance, a pack held warm, (7) failures: too cold, and the limits of the search.
#
# *Illustrative parameters:* the volume, internal resistance, the resistance rise as Cu2+ runs out
# and the temperature sensitivity below are chosen for teaching (as in Session 3), not measured.
# *Safety: real lithium and lead-acid batteries can be dangerous. Educational model only.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_GAS = 8.314462618        # J/(mol K)
FARADAY = 96485.0          # C/mol
T0 = 298.15                # K (25 C)
N_E = 2                    # electrons per Zn2+/Cu2+ reaction
E0 = 1.10                  # V, standard Daniell cell voltage

# ILLUSTRATIVE cell parameters (the same as Session 3)
VOL = 0.020                # L of solution in each half cell
C_CU0 = 1.0                # mol/L Cu2+ at the start
C_ZN0 = 0.1                # mol/L Zn2+ at the start
R_INT0 = 0.8               # ohm, internal resistance at 25 C (fresh solution rises by a factor 1.05 at q = 0)
K_DEP = 0.05               # resistance rises by K_DEP * C_CU0 / c_Cu as Cu2+ runs out
EA = 20000.0               # J/mol, "activation" energy of the resistance (illustrative)
C_FLOOR = 1e-9
Q_MAX = N_E * FARADAY * VOL * C_CU0       # C: charge the Cu2+ in solution can supply (1.072 Ah)

# the requirement of the mini-project
R_LAMP = 30.0              # ohm
V_MIN = 9.0                # V across the lamp
HOURS = 5.0                # h
TEMPS_C = (0.0, 25.0, 45.0)


def kelvin(t_c):
    return float(t_c) + 273.15


# %% [markdown]
# ## Step 1: how the resistance depends on temperature
# Ions move more slowly when it is cold, so the cell's internal resistance rises. We use the
# same Arrhenius-type law as Session 3 (and as the openarrhenius repo): a **factor**
#
#     f(T) = r(T) / r(25 C) = exp( (EA / R) (1/T - 1/T0) ),      EA = 20 kJ/mol (illustrative)
#
# At 0 C the factor is 2.09 (more than double), at -10 C 2.9, at 45 C 0.60. The maximum power a
# cell can deliver, E^2 / (4 r), falls by the same factor.

# %%
def resistance_factor(T):
    """r(T) / r(25 C) for the temperature-dependent part (T in kelvin)."""
    return float(np.exp(EA / R_GAS * (1.0 / np.asarray(T, dtype=float) - 1.0 / T0)))


def thermal_voltage(T=T0, n=1):
    return R_GAS * T / (n * FARADAY)


def nernst(Q, T=T0, e0=E0, n=N_E):
    Q = np.asarray(Q, dtype=float)
    if np.any(Q <= 0):
        raise ValueError("reaction quotient must be positive")
    return e0 - thermal_voltage(T, n) * np.log(Q)


def concentrations(q):
    xi = np.asarray(q, dtype=float) / (N_E * FARADAY)
    return C_ZN0 + xi / VOL, np.maximum(C_CU0 - xi / VOL, C_FLOOR)


def ocv(q, T=T0):
    c_zn, c_cu = concentrations(q)
    return nernst(c_zn / c_cu, T)


def r_internal(q, T=T0, r0=R_INT0):
    """Internal resistance of one cell (ohm) after charge q (C) has been drawn, at temperature T (K)."""
    _, c_cu = concentrations(q)
    return r0 * np.exp(EA / R_GAS * (1.0 / T - 1.0 / T0)) * (1.0 + K_DEP * C_CU0 / c_cu)


def max_power(T=T0, r0=R_INT0):
    """Largest power one fresh cell can give to a load: E^2 / (4 r) (W)."""
    e, r = float(ocv(0.0, T)), float(r_internal(0.0, T, r0))
    return e * e / (4.0 * r)


# %% [markdown]
# ## Step 2: the pack as one equivalent cell
# A pack has `ns` cells in series in each string and `npar` identical strings in parallel. With
# lamp resistance R the current in each string is i = ns E / (R + ns r / npar) / npar, so
#
#     i = E / (R npar / ns + r).
#
# That is exactly one cell feeding a load R_eq = R npar / ns. The lamp voltage is v = ns i R_eq,
# so the lamp stays above v_min exactly while the single cell's terminal voltage stays above
# v_min / ns. Whatever we learned about one cell (Session 3) carries over to the whole pack.
# We integrate time as t = integral of dq / i until the cutoff.

# %%
def _grid(n):
    u = np.linspace(0.0, 1.0, n)
    return Q_MAX * (1.0 - 1e-4) * (1.0 - (1.0 - u) ** 4)          # charge drawn from each cell, denser near the end


def pack_curve(ns, npar, R_lamp, T=T0, r0=R_INT0, dT=0.0, n=4001):
    """Lamp voltage against time for a pack in an ambient of T kelvin, with the cells held dT kelvin above it.
    Returns dict: q (C per cell), t (h), v (lamp voltage), i (A per string), cell_T (K)."""
    if ns < 1 or npar < 1:
        raise ValueError("a pack needs at least one cell")
    Tc = T + dT
    q = _grid(n)
    e, r = ocv(q, Tc), r_internal(q, Tc, r0)
    i_total = ns * e / (R_lamp + ns * r / npar)
    i_string = i_total / npar
    t = np.concatenate([[0.0], np.cumsum(0.5 * (1.0 / i_string[1:] + 1.0 / i_string[:-1]) * np.diff(q))]) / 3600.0
    return {"q": q, "t": t, "v": i_total * R_lamp, "i": i_string, "cell_T": Tc}


def pack_runtime_hours(ns, npar, R_lamp, v_min, T=T0, r0=R_INT0, dT=0.0, n=4001):
    """Hours the lamp stays at or above v_min volts (0 if it starts below). The crossing is found by
    linear interpolation between grid points. If the lamp never drops below v_min the run ends when the
    Cu2+ is used up."""
    c = pack_curve(ns, npar, R_lamp, T, r0, dT, n)
    v, t = c["v"], c["t"]
    if v[0] < v_min:
        return 0.0
    bad = np.nonzero(v < v_min)[0]
    if len(bad) == 0:
        return float(t[-1])
    j = bad[0]
    return float(np.interp(v_min, [v[j], v[j - 1]], [t[j], t[j - 1]]))


# %% [markdown]
# ## Step 3: how a pack fails
# There are two different failures, and they need different cures:
# * **fails at the start**: the very first lamp voltage is already below 9 V. More cells in series
#   (higher voltage) or a lower resistance per cell is the cure; more time makes no difference.
# * **runs out early**: the lamp starts fine, but as Cu2+ is used up the cell voltage falls and the
#   resistance rises, so the lamp crosses 9 V after a few hours. More strings in parallel (each
#   cell works less) or a lower resistance helps.
# A third surprise: with the number of strings fixed, *more* cells in series can shorten the run,
# because a higher voltage drives more current through the lamp and drains every cell faster.

# %%
def pack_report(ns, npar, R_lamp=R_LAMP, v_min=V_MIN, T=T0, r0=R_INT0, dT=0.0):
    """One pack, one temperature. Returns dict: cells, hours, v_start, r_start (ohm per cell), limit ("start", "cutoff" or "exhausted")."""
    c = pack_curve(ns, npar, R_lamp, T, r0, dT)
    h = pack_runtime_hours(ns, npar, R_lamp, v_min, T, r0, dT)
    if c["v"][0] < v_min:
        limit = "start"
    elif np.all(c["v"] >= v_min):
        limit = "exhausted"
    else:
        limit = "cutoff"
    return {"cells": ns * npar, "hours": h, "v_start": float(c["v"][0]), "r_start": float(r_internal(0.0, T + dT, r0)), "limit": limit}


# %% [markdown]
# ## Step 4: a design search across temperatures
# A design **works** when the lamp stays at or above v_min for at least `hours` at *every* ambient
# temperature in the list. `design_search` tries every (ns, npar) in a range, records the runtime
# at each temperature, and returns the smallest working pack (fewest cells; if tied, the one with
# the longest worst-case runtime). It returns `None` for the best pack when nothing in the range
# works, instead of an invented answer.

# %%
def design_search(R_lamp=R_LAMP, v_min=V_MIN, hours=HOURS, temps_c=TEMPS_C, r0=R_INT0, dT=0.0,
                  ns_range=range(6, 19), np_range=range(1, 7)):
    """Returns dict: rows (list of dicts ns, npar, cells, hours = tuple per temperature, ok), best (dict or None)."""
    if hours <= 0 or v_min <= 0 or R_lamp <= 0 or len(temps_c) == 0:
        raise ValueError("requirements must be positive and at least one temperature is needed")
    rows = []
    for ns in ns_range:
        for npar in np_range:
            hs = tuple(pack_runtime_hours(ns, npar, R_lamp, v_min, kelvin(tc), r0, dT) for tc in temps_c)
            rows.append({"ns": ns, "npar": npar, "cells": ns * npar, "hours": hs, "ok": min(hs) >= hours})
    ok = [r for r in rows if r["ok"]]
    best = min(ok, key=lambda r: (r["cells"], -min(r["hours"]), r["ns"])) if ok else None
    return {"rows": rows, "best": best}


def coldest_ok(ns, npar, R_lamp=R_LAMP, v_min=V_MIN, hours=HOURS, r0=R_INT0, dT=0.0, t_hot_c=45.0, t_cold_c=-40.0):
    """Lowest ambient temperature (C) at which this pack still meets the requirement, searched downward from
    t_hot_c in 0.5 K steps and then refined to 0.01 K. None if it fails even at t_hot_c; t_cold_c if it never fails above it."""
    def ok(tc):
        return pack_runtime_hours(ns, npar, R_lamp, v_min, kelvin(tc), r0, dT) >= hours
    if not ok(t_hot_c):
        return None
    tc = t_hot_c
    while tc > t_cold_c and ok(tc - 0.5):
        tc -= 0.5
    if tc <= t_cold_c:
        return float(t_cold_c)
    lo, hi = tc - 0.5, tc                      # fails at lo, works at hi
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if ok(mid) else (mid, hi)
    return float(round(hi, 2))


# %% [markdown]
# ## Step 5: validate the pack model
# 1. **Independent solver.** Integrate dq/dt = i(q) in *time* with fourth-order Runge-Kutta
#    (no use of the charge-domain integral) and find when the lamp reaches v_min; it must match
#    `pack_runtime_hours`.
# 2. **Exact equivalence.** The pack equals one cell with load R npar / ns and a cutoff of v_min / ns.
#    Compute that single-cell runtime from the Session 3 relations and compare.
# 3. **Limits.** Heavy parallelism approaches the capacity limit (every cell then carries very
#    little current); a pack with too few cells in series gives 0 h because it starts below 9 V.

# %%
def rk4_runtime_hours(ns, npar, R_lamp, v_min, T=T0, r0=R_INT0, dT=0.0):
    """Runtime by integrating dq/dt in time with RK4 and stopping at the first time the lamp is below v_min."""
    Tc = T + dT

    def i_string(q):
        e, r = float(ocv(q, Tc)), float(r_internal(q, Tc, r0))
        return ns * e / (R_lamp + ns * r / npar) / npar

    def lamp_v(q):
        return npar * i_string(q) * R_lamp

    if lamp_v(0.0) < v_min:
        return 0.0
    q_end = Q_MAX * (1.0 - 1e-4)
    h = 30.0                                   # s, a fixed time step: the curve is smooth
    q, t = 0.0, 0.0
    while t < 48.0 * 3600.0 and q < q_end:
        k1 = i_string(q)
        k2 = i_string(min(q + 0.5 * h * k1, q_end))
        k3 = i_string(min(q + 0.5 * h * k2, q_end))
        k4 = i_string(min(q + h * k3, q_end))
        qn = min(q + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0, q_end)
        if lamp_v(qn) < v_min:
            f = (lamp_v(q) - v_min) / (lamp_v(q) - lamp_v(qn))
            return float((t + f * h) / 3600.0)
        q, t = qn, t + h
    return float(t / 3600.0)


def single_cell_equivalent_hours(ns, npar, R_lamp, v_min, T=T0, r0=R_INT0, dT=0.0, n=20001):
    """Runtime of ONE cell feeding R_lamp * npar / ns to the cutoff v_min / ns (Session 3 relations)."""
    Tc = T + dT
    R_eq = R_lamp * npar / ns
    q = _grid(n)
    e, r = ocv(q, Tc), r_internal(q, Tc, r0)
    i = e / (R_eq + r)
    v = e - i * r
    cut = v_min / ns
    if v[0] < cut:
        return 0.0
    t = np.concatenate([[0.0], np.cumsum(0.5 * (1.0 / i[1:] + 1.0 / i[:-1]) * np.diff(q))]) / 3600.0
    bad = np.nonzero(v < cut)[0]
    if len(bad) == 0:
        return float(t[-1])
    j = bad[0]
    return float(np.interp(cut, [v[j], v[j - 1]], [t[j], t[j - 1]]))


# %% [markdown]
# ## Step 6: design levers
# The plain search needs 24 cells at 0 C. A designer has three ways to do better, each with a cost:
# 1. **More cells** (what the search already does): simple, but heavier and dearer.
# 2. **A cell with lower resistance** (r0 at 25 C): closer electrodes or a better electrolyte.
#    In the model this is just `r0`. The 0.56 ohm used below (30 percent lower) is an
#    illustration, not a measured value.
# 3. **Keep the pack warm** (`dT` kelvin above the ambient): an insulated box that holds the
#    cells' own heat, or a pack carried inside a coat. The model holds the cells at that
#    temperature for the whole run. A real pack takes time to warm up, and that transient (and the cost
#    of a heater) is **not** in this session; it comes in the heat-feedback session of the roadmap.

# %%
R0_LOW = 0.56            # ohm, a cell with 30 percent lower resistance (illustrative)
DT_WARM = 5.0            # K, an insulated pack held 5 K above the ambient (illustrative)


def levers_table(temps_c=TEMPS_C):
    """Smallest working pack for four cases: plain, lower-resistance cell, warm pack, both."""
    out = []
    for name, r0, dT in (("plain cells", R_INT0, 0.0), ("lower-resistance cell", R0_LOW, 0.0),
                         (f"pack held {DT_WARM:g} K warm", R_INT0, DT_WARM), ("both levers", R0_LOW, DT_WARM)):
        res = design_search(temps_c=temps_c, r0=r0, dT=dT)
        out.append({"name": name, "r0": r0, "dT": dT, "best": res["best"]})
    return out


# %% [markdown]
# ## Step 7: two failures
# (a) **Too cold for any pack in the range.** Below some temperature no pack of up to 18 cells in
# series and 6 strings in parallel keeps the lamp at 9 V: the search must say so.
# (b) **A pack made for a warm day.** The 20-cell winner at 25 C looks fine until it is cold: it
# fails at the *start* at 0 C, and the pack that wins at 45 C (18 cells) fails sooner still.

# %%
def coldest_designable(temps_c, r0=R_INT0, dT=0.0, ns_range=range(6, 19), np_range=range(1, 7)):
    """For each ambient temperature (C) the smallest working pack's cell count, or None if nothing in the range works."""
    out = []
    for tc in temps_c:
        b = design_search(temps_c=(tc,), r0=r0, dT=dT, ns_range=ns_range, np_range=np_range)["best"]
        out.append(None if b is None else b["cells"])
    return out


# %% [markdown]
# ## Step 8: see it
# Left: the lamp voltage of the 20-cell pack against time at 25, 0 and 45 C, with the 9 V line.
# Middle: the smallest working pack against ambient temperature, with and without the two levers.
# Right: runtime of the 24-cell, 22-cell and 20-cell packs against the ambient temperature.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    print("resistance factor at -10, 0, 25, 45 C:", [round(resistance_factor(kelvin(t)), 3) for t in (-10, 0, 25, 45)])
    print("max power of a fresh cell at 0, 25, 45 C:", [round(max_power(kelvin(t)), 3) for t in (0, 25, 45)])
    for tc in TEMPS_C:
        print(tc, "C: 10x2", pack_report(10, 2, T=kelvin(tc)))
    res = design_search()
    print("smallest pack working at 0, 25 and 45 C:", res["best"])
    for row in levers_table():
        print(row["name"], row["best"])

    fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.9))
    for tc, col in ((25.0, "#2a6fdb"), (0.0, "#d9534f"), (45.0, "#2a9d8f")):
        c = pack_curve(10, 2, R_LAMP, kelvin(tc))
        ax[0].plot(c["t"], c["v"], color=col, label=f"{tc:g} C: {pack_runtime_hours(10, 2, R_LAMP, V_MIN, kelvin(tc)):.2f} h")
    ax[0].axhline(V_MIN, color="gray", ls="--")
    ax[0].axvline(HOURS, color="gray", ls=":")
    ax[0].set_xlabel("time (h)")
    ax[0].set_ylabel("lamp voltage (V)")
    ax[0].set_title("The 20-cell pack (10 x 2) from Session 3", fontsize=10)
    ax[0].set_xlim(0, 8)
    ax[0].set_ylim(0, 13)
    ax[0].grid(alpha=0.3)
    ax[0].legend(fontsize=8, loc="lower left")

    temps = list(range(-10, 46, 5))
    for name, r0, dT, col, ls in (("plain cells", R_INT0, 0.0, "#d9534f", "-"), ("lower-resistance cell", R0_LOW, 0.0, "#2a6fdb", "--"),
                                  (f"held {DT_WARM:g} K warm", R_INT0, DT_WARM, "#c86a00", ":")):
        cells = coldest_designable(temps, r0, dT)
        xs = [t for t, c in zip(temps, cells) if c is not None]
        ax[1].plot(xs, [c for c in cells if c is not None], ls, marker="o", color=col, label=name)
    ax[1].set_xlabel("ambient temperature (C)")
    ax[1].set_ylabel("cells in the smallest working pack")
    ax[1].set_title("Cold costs cells", fontsize=10)
    ax[1].grid(alpha=0.3)
    ax[1].legend(fontsize=8)

    ta = np.linspace(-15, 45, 121)
    for (ns, npar, r0), col in (((12, 2, R_INT0), "#d9534f"), ((11, 2, R0_LOW), "#2a6fdb"), ((10, 2, R_INT0), "#2a9d8f")):
        ax[2].plot(ta, [pack_runtime_hours(ns, npar, R_LAMP, V_MIN, kelvin(t), r0) for t in ta], color=col,
                   label=f"{ns} x {npar} = {ns * npar} cells" + (" (r0 0.56)" if r0 != R_INT0 else ""))
    ax[2].axhline(HOURS, color="gray", ls="--")
    ax[2].set_xlabel("ambient temperature (C)")
    ax[2].set_ylabel("lamp runtime to 9 V (h)")
    ax[2].set_title("Where each pack stops working", fontsize=10)
    ax[2].grid(alpha=0.3)
    ax[2].legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "cold_pack.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Where this stops
# Real cold cells also lose capacity, freeze and change chemistry; this model changes only the
# resistance. The warm-pack lever holds the temperature fixed and ignores warm-up. Use this to
# understand, never to design or test a real battery.
