"""Session 2 (Level 2): the Arrhenius form, the 1000/T plot, sensitivities and experiment design.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: how fast is a reaction, and which rate does an experiment pin down?
# **A. Real-world problem.** Reactions speed up enormously when the gas is hotter. A
# mechanism therefore stores, for every reaction, a *formula* for the rate constant as a
# function of temperature, and a calibration adjusts that formula. Before we adjust anything we
# ask two questions. How does the rate constant depend on temperature (Arrhenius)? And if we
# nudge one rate constant, how much does the thing an experiment measures move
# (*sensitivity*)? The answer tells us which experiments are worth running. All numbers are toys.
#
# **Plan.** (1) the Arrhenius formula, (2) the straight line on a 1000/T plot, (3) a toy
# ignition delay with a formula, (4) sensitivities by finite differences, (5) a design problem.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_GAS = 8.314462618                                # J / (mol K)
T_REF = 1000.0                                     # K
# Toy rate constants at 1000 K and activation energies (invented numbers):
#   k1: F -> R (1/s), k2: F + R -> 2R (L/(mol s)), k3: R -> P (1/s)
K_REF = np.array([2.0e-3, 30.0, 10.0])
E_ACT = np.array([120e3, 60e3, 20e3])              # J/mol


# %% [markdown]
# ## Step 1: the modified Arrhenius form
# `k(T) = A * T^n * exp(-Ea / (R T))` with `A` the pre-exponential factor, `n` a temperature
# exponent (0 for the simplest case), `Ea` the activation energy in J/mol, `R` the gas constant
# 8.314 J/(mol K) and `T` the absolute temperature in K. The exponential is the fraction of
# molecular encounters that carry at least `Ea` of energy. Check the units: `Ea / (R T)` has
# no unit, so `A` carries the unit of `k`.

# %%
def arrhenius(T, A, n, Ea):
    """Rate constant k(T) = A T^n exp(-Ea / (R T)); T in K, Ea in J/mol."""
    T = np.asarray(T, dtype=float)
    return A * T ** n * np.exp(-Ea / (R_GAS * T))


def prefactor_from(k_at_ref, n, Ea, T_ref=T_REF):
    """The A that makes k(T_ref) = k_at_ref for given n and Ea."""
    return k_at_ref / (T_ref ** n * np.exp(-Ea / (R_GAS * T_ref)))


# %% [markdown]
# ## Step 2: the 1000/T plot
# Take the logarithm: `ln k = ln A + n ln T - Ea / (R T)`. For n = 0 this is a straight line
# when `ln k` is plotted against `1/T`; chemists plot against `1000/T` so the numbers are of
# order 1. The slope is `-Ea / (1000 R)` per unit of `1000/T`. So **a straight line fit to
# measured rate constants gives the activation energy**.

# %%
def fit_arrhenius(T, k, n=0.0):
    """Fit ln(k / T^n) = ln A - Ea/(R T) by a straight line. Returns (A, Ea in J/mol)."""
    T = np.asarray(T, dtype=float)
    y = np.log(np.asarray(k, dtype=float) / T ** n)
    slope, intercept = np.polyfit(1.0 / T, y, 1)
    return float(np.exp(intercept)), float(-slope * R_GAS)


# %% [markdown]
# ## Step 3: a toy ignition delay with a formula
# The three toy reactions make a branching chain. While fuel F is plentiful (F is about F0) the
# radical R obeys `dR/dt = k1 F0 + g R` with growth rate `g = k2 F0 - k3`. Its solution is
# `R = (k1 F0 / g)(exp(g t) - 1)`. Call the **ignition delay** the time when R reaches F0/2:
#
#     tau = ln(1 + g / (2 k1)) / g       (valid when g > 0)
#
# This is an *approximation* (it ignores the fuel being used up), good enough to see trends.
# Session 3 solves the full equations and measures the error.

# %%
def rate_constants(T, s=(1.0, 1.0, 1.0)):
    """k1, k2, k3 at temperature T (K) with scale factors s, using the Arrhenius form around 1000 K."""
    T = np.asarray(T, dtype=float)
    return [K_REF[i] * s[i] * np.exp(-E_ACT[i] / R_GAS * (1.0 / T - 1.0 / T_REF)) for i in range(3)]


def tau_approx(T, F0=1.0, s=(1.0, 1.0, 1.0)):
    """Approximate ignition delay (s). Returns nan when g <= 0 (radicals die faster than they grow)."""
    k1, k2, k3 = rate_constants(T, s)
    g = k2 * F0 - k3
    with np.errstate(all="ignore"):
        return np.where(g > 0, np.log1p(g / (2 * k1)) / g, np.nan)


# %% [markdown]
# ## Step 4: sensitivity by finite differences
# The **sensitivity** of the ignition delay to rate constant `k_i` is the percentage change of
# tau per percentage change of `k_i`: `S_i = d ln tau / d ln k_i`. Numerically, scale `k_i` up
# and down by a small factor `e^eps` and divide the change in `ln tau` by `2 eps` (a *central
# difference*). `S = -1` would mean "double this rate and the delay halves".

# %%
def sensitivity(T, i, F0=1.0, eps=0.01):
    """d ln(tau) / d ln(k_i) at temperature T by a central difference (i = 0, 1, 2)."""
    up = np.ones(3)
    dn = np.ones(3)
    up[i] = np.exp(eps)
    dn[i] = np.exp(-eps)
    return (np.log(tau_approx(T, F0, up)) - np.log(tau_approx(T, F0, dn))) / (2 * eps)


def sensitivity_exact(T, i, F0=1.0):
    """The same derivative from calculus (to check the finite difference)."""
    k1, k2, k3 = rate_constants(T)
    g = k2 * F0 - k3
    tau = np.log1p(g / (2 * k1)) / g
    dtau_dg = -tau / g + 1.0 / (g * (2 * k1 + g))
    if i == 0:
        return -1.0 / ((2 * k1 + g) * tau)
    if i == 1:
        return k2 * F0 * dtau_dg / tau
    return -k3 * dtau_dg / tau


# %% [markdown]
# ## Step 5: a design problem
# Suppose we will measure tau at two temperatures, each with noise of 5 percent (0.05 in
# `ln tau`), and we want to learn the scale factors `s1` and `s2` of `k1` and `k2`. Each
# experiment gives one row `[S_1, S_2] / 0.05` of a matrix `J`. The uncertainty (standard
# deviation) of `ln s1` and `ln s2` is the square root of the diagonal of `(J^T J)^-1`.
# Rows that are too alike make `J^T J` nearly singular and the uncertainty huge.

# %%
def design_std(temps, F0=1.0, sigma=0.05):
    """1-sigma uncertainty of (ln s1, ln s2) for experiments at the given temperatures (K)."""
    J = np.array([[sensitivity(T, 0, F0), sensitivity(T, 1, F0)] for T in np.atleast_1d(temps)]) / sigma
    return np.sqrt(np.diag(np.linalg.inv(J.T @ J)))


# %%
if __name__ == "__main__":
    import itertools

    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # --- Arrhenius and the 1000/T plot
    Ea, n = 80e3, 0.0
    A = prefactor_from(10.0, n, Ea)
    T = np.linspace(600, 2000, 8)
    k_true = arrhenius(T, A, n, Ea)
    rng = np.random.default_rng(3)
    k_noisy = k_true * np.exp(0.05 * rng.standard_normal(T.size))
    A_fit, Ea_fit = fit_arrhenius(T, k_noisy)
    print(f"A = {A:.4g}; true Ea = {Ea / 1000:.1f} kJ/mol, Ea from a line through noisy data = {Ea_fit / 1000:.1f} kJ/mol")
    print(f"k(1000 K) = {float(arrhenius(1000.0, A, n, Ea)):.3f} 1/s, k(2000 K) = {float(arrhenius(2000.0, A, n, Ea)):.1f} 1/s")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    Tg = np.linspace(600, 2000, 100)
    for Ea_kj in (40, 80, 160):
        kk = arrhenius(Tg, prefactor_from(10.0, 0.0, Ea_kj * 1e3), 0.0, Ea_kj * 1e3)
        ax.plot(1000 / Tg, np.log10(kk), label=f"Ea = {Ea_kj} kJ/mol")
    ax.plot(1000 / T, np.log10(k_noisy), "ko", label="noisy data (Ea = 80)")
    ax.set_xlabel("1000 / T  (1/K)")
    ax.set_ylabel("log10( k / 1/s )")
    ax.set_title("Arrhenius lines: steeper means larger Ea")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "arrhenius_1000T.png", dpi=120)

    # --- ignition delay and sensitivities
    Tt = np.array([900.0, 1000.0, 1100.0, 1200.0, 1300.0, 1400.0])
    print("tau_approx (s) at", Tt, "->", np.round(tau_approx(Tt), 4))
    for i, name in enumerate(["k1", "k2", "k3"]):
        fd = sensitivity(Tt, i)
        ex = sensitivity_exact(Tt, i)
        print(f"S({name}) finite difference:", np.round(fd, 3), " largest gap to calculus:", f"{np.abs(fd - ex).max():.1e}")

    Tp = np.linspace(900, 1400, 60)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    for i, name in enumerate(["k1 (F -> R)", "k2 (F + R -> 2R)", "k3 (R -> P)"]):
        ax2.plot(Tp, sensitivity(Tp, i), label=name)
    ax2.axhline(0, color="gray", lw=0.8)
    ax2.set_xlabel("temperature (K)")
    ax2.set_ylabel("sensitivity d ln tau / d ln k")
    ax2.set_title("Which rate does tau feel? (toy model)")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "sensitivity_vs_T.png", dpi=120)

    # --- design: choose two of six temperatures
    cands = [900, 1000, 1100, 1200, 1300, 1400]
    table = sorted(((design_std(p), p) for p in itertools.combinations(cands, 2)), key=lambda x: x[0][1])
    print("pair of temperatures -> 1-sigma of (ln s1, ln s2), best to worst for ln s2:")
    for sd, p in table[:3] + table[-2:]:
        print(f"  {p}: ({sd[0]:.3f}, {sd[1]:.3f})")
    fig3, ax3 = plt.subplots(figsize=(6.4, 4.2))
    labels = [f"{p[0]}-{p[1]}" for _, p in table]
    ax3.bar(range(len(table)), [sd[1] for sd, _ in table], color="tab:blue")
    ax3.set_yscale("log")
    ax3.set_xticks(range(len(table)))
    ax3.set_xticklabels(labels, rotation=90, fontsize=7)
    ax3.set_xlabel("pair of experiment temperatures (K)")
    ax3.set_ylabel("1-sigma of ln s2 (log scale)")
    ax3.set_title("Widely spaced temperatures pin k2 down best")
    ax3.grid(alpha=0.3, axis="y")
    fig3.tight_layout()
    fig3.savefig(OUT / "design_pairs.png", dpi=120)
