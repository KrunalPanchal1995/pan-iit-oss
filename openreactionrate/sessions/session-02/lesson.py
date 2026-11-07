"""Session 2 (Level 2): rate laws, half-life, reading the order, Arrhenius and catalysts.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: rate laws and the effect of temperature and catalysts
# **A. Real-world problem.** A drug tablet, a paint, a pot of stew: someone has to decide how
# long a reaction needs. For that we need an equation for the rate, a way to tell from data what
# kind of reaction it is, and the effect of temperature and of a catalyst on k. (General
# education only; real process design needs measured data and safety review.)

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
R = 8.314  # gas constant, J/(mol K)


# %% [markdown]
# ## Step 1: rate = k [A]^n
# The *order* n says how strongly the rate depends on concentration. Solving d[A]/dt = -k [A]^n:
#
#     n = 1:  [A] = A0 exp(-k t)            half-life = ln 2 / k  (same for any A0)
#     n = 2:  [A] = A0 / (1 + k A0 t)       half-life = 1 / (k A0) (longer when A0 is small)
#
# Units of k: 1/s for n = 1 and L/(mol s) for n = 2.

# %%
def conc_first(t, A0, k):
    return A0 * np.exp(-k * np.asarray(t, dtype=float))


def conc_second(t, A0, k):
    return A0 / (1.0 + k * A0 * np.asarray(t, dtype=float))


def half_life(order, A0, k):
    if order == 1:
        return float(np.log(2.0) / k)
    return float(1.0 / (k * A0))


def time_to_conversion(order, A0, k, x):
    """Time (s) for a fraction x (0 < x < 1) of A to react."""
    if order == 1:
        return float(np.log(1.0 / (1.0 - x)) / k)
    return float(x / (k * A0 * (1.0 - x)))


# %% [markdown]
# ## Step 2: read the order from a plot
# Straight lines are easy to recognise:
# * first order: **ln [A] against t** is a straight line (slope -k);
# * second order: **1/[A] against t** is a straight line (slope +k).
# `order_from_data` fits both lines by least squares and picks the straighter one (larger R^2).

# %%
def r_squared(x, y):
    slope, icpt = np.polyfit(x, y, 1)
    resid = y - (slope * x + icpt)
    return float(1.0 - resid.var() / y.var())


def order_from_data(t, conc):
    t, conc = np.asarray(t, float), np.asarray(conc, float)
    r1 = r_squared(t, np.log(conc))
    r2 = r_squared(t, 1.0 / conc)
    return (1 if r1 >= r2 else 2), r1, r2


# %% [markdown]
# ## Step 3: temperature and catalysts through k = A exp(-Ea / R T)
# The Arrhenius form: only a small share of collisions have energy above the activation energy
# Ea, and that share grows steeply with temperature T (in kelvin). A catalyst offers another
# route with a lower Ea, so it multiplies k by exp(dEa / (R T)), where dEa is the drop in Ea.
# (Fitting Ea from data properly is the job of the openarrhenius repo.)

# %%
def arrhenius_k(A_factor, Ea, T):
    """k = A exp(-Ea / (R T)); Ea in J/mol, T in K."""
    return A_factor * np.exp(-Ea / (R * T))


def k_at_temperature(k_ref, Ea, T, T_ref=300.0):
    """k at T from a known k at T_ref (the pre-exponential factor cancels)."""
    return k_ref * np.exp(-Ea / R * (1.0 / T - 1.0 / T_ref))


def catalyst_speedup(delta_Ea, T):
    """Factor by which k grows when the activation energy drops by delta_Ea (J/mol) at T (K)."""
    return float(np.exp(delta_Ea / (R * T)))


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t = np.linspace(0, 120, 200)
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
    c1, c2 = conc_first(t, 1.0, 0.03), conc_second(t, 1.0, 0.03)
    axes[0].plot(t, c1, label="first order, k = 0.03 1/s")
    axes[0].plot(t, c2, label="second order, k = 0.03 L/(mol s)")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("[A] (mol/L)")
    axes[0].legend(fontsize=7)
    axes[1].plot(t, np.log(c1), color="tab:blue")
    axes[1].plot(t, np.log(c2), color="tab:orange", ls="--")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("ln [A] (no unit)")
    axes[1].set_title("first order: straight", fontsize=9)
    axes[2].plot(t, 1 / c1, color="tab:blue", ls="--")
    axes[2].plot(t, 1 / c2, color="tab:orange")
    axes[2].set_xlabel("time (s)")
    axes[2].set_ylabel("1/[A] (L/mol)")
    axes[2].set_title("second order: straight", fontsize=9)
    for a in axes:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "orders_and_lines.png", dpi=120)

    T = np.linspace(280, 380, 100)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    for dEa, lab in ((0, "no catalyst"), (20000, "catalyst: Ea lower by 20 kJ/mol")):
        ax2.semilogy(T, k_at_temperature(0.01, 50000 - dEa, T) , label=lab)
    ax2.set_xlabel("temperature (K)")
    ax2.set_ylabel("rate constant k (1/s), log scale")
    ax2.set_title("k = A exp(-Ea / R T) with Ea = 50 kJ/mol")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "arrhenius_catalyst.png", dpi=120)

    print("half-life first order k=0.03:", round(half_life(1, 1.0, 0.03), 2), "s;  second order A0=1:", round(half_life(2, 1.0, 0.03), 2), "s; A0=0.5:", round(half_life(2, 0.5, 0.03), 2), "s")
    tt = np.linspace(0, 100, 12)
    print("order read from first-order data:", order_from_data(tt, conc_first(tt, 1.0, 0.03))[0],
          "; from second-order data:", order_from_data(tt, conc_second(tt, 1.0, 0.03))[0])
    print("k ratio 310 K / 300 K for Ea = 50 kJ/mol:", round(float(k_at_temperature(1.0, 50000, 310)), 3))
    print("k ratio 350 K / 300 K for Ea = 50 kJ/mol:", round(float(k_at_temperature(1.0, 50000, 350)), 1))
    print("catalyst, dEa = 20 kJ/mol at 300 K: speed-up", round(catalyst_speedup(20000, 300), 0), "times")
    print("catalyst, dEa = 20 kJ/mol at 350 K: speed-up", round(catalyst_speedup(20000, 350), 0), "times")
    k300 = 0.02
    print("design: first order k=0.02 1/s, 90% at", round(time_to_conversion(1, 1.0, k300, 0.9), 1), "s")
    k310 = float(k_at_temperature(k300, 50000, 310))
    print("   at 310 K k =", round(k310, 4), "1/s ->", round(time_to_conversion(1, 1.0, k310, 0.9), 1), "s")
    print("   catalyst dEa = 5 kJ/mol at 300 K:", round(time_to_conversion(1, 1.0, k300 * catalyst_speedup(5000, 300), 0.9), 1), "s")
    print("second order A0=1 k=0.02: 90% at", round(time_to_conversion(2, 1.0, 0.02, 0.9), 1), "s; A0 = 0.1:", round(time_to_conversion(2, 0.1, 0.02, 0.9), 1), "s")

# %% [markdown]
# ## Where this stops
# Real reactions rarely have a single step. Session 3 writes whole networks of steps as a system
# of differential equations and solves it numerically.
