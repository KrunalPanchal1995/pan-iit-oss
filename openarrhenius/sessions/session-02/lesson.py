"""Session 2 (Level 2): the Arrhenius fit, its units, the modified form, and the design of the experiment.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: fit k(T), then design the experiment
# **A. Real-world problem.** Each measurement of a rate constant costs a day of lab work. You can
# afford six temperatures. Which six give the most precise activation energy?
#
# **Plan.** (1) the fit as a function with units, (2) the standard error of Ea from the spread
# of 1000/T, (3) the modified Arrhenius form k = A T^n exp(-Ea/(R T)), (4) a design rule
# checked by simulation.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_GAS = 8.314462618          # J/(mol K)
A_TRUE = 1.0e13              # 1/s
EA_TRUE = 150.0              # kJ/mol


# %% [markdown]
# ## Step 1: model, data, fit
# ln k = ln A - (Ea/R)(1/T). With x = 1000/T the slope is s = -Ea/(1000 R), so Ea[kJ/mol] = -s R.
# If the scatter of ln k differs from point to point, pass `sigma_ln` (one number per point):
# numpy.polyfit then weights each point by 1/sigma.

# %%
def arrhenius_k(T, A=A_TRUE, Ea_kJ=EA_TRUE, n=0.0):
    """Modified Arrhenius k = A T^n exp(-Ea/(R T)); n = 0 is the plain law. Units of A: 1/s when n = 0."""
    T = np.asarray(T, dtype=float)
    return A * T ** n * np.exp(-Ea_kJ * 1000.0 / (R_GAS * T))


def synthetic(T, rel_noise=0.05, seed=0, A=A_TRUE, Ea_kJ=EA_TRUE, n=0.0):
    """Measured k = true k times exp(rel_noise * N(0,1)): multiplicative (lognormal) error."""
    rng = np.random.default_rng(seed)
    T = np.asarray(T, dtype=float)
    return arrhenius_k(T, A, Ea_kJ, n) * np.exp(rel_noise * rng.standard_normal(T.size))


def fit_arrhenius(T, k, sigma_ln=None):
    """Fit ln k = ln A - (Ea/R)/T. Returns (A, Ea in kJ/mol)."""
    T, k = np.asarray(T, dtype=float), np.asarray(k, dtype=float)
    w = None if sigma_ln is None else 1.0 / np.asarray(sigma_ln, dtype=float)
    s, b = np.polyfit(1000.0 / T, np.log(k), 1, w=w)
    return float(np.exp(b)), float(-s * R_GAS)


# %% [markdown]
# ## Step 2: how precise is Ea?
# For equal-size errors sigma in ln k, the standard error of the slope is sigma / sqrt(Sxx)
# with Sxx = sum (x - xbar)^2 and x = 1000/T. In kJ/mol: SE(Ea) = R * sigma / sqrt(Sxx).
# A wide spread of x (a big Sxx) means a small error.

# %%
def sxx(T):
    x = 1000.0 / np.asarray(T, dtype=float)
    return float(np.sum((x - x.mean()) ** 2))


def ea_se(T, sigma_ln):
    """Standard error of Ea in kJ/mol for temperatures T and error sigma_ln (no unit) in ln k."""
    return float(R_GAS * sigma_ln / np.sqrt(sxx(T)))


def even_in_inverse_T(Tmin, Tmax, n):
    """n temperatures evenly spaced in 1/T between Tmin and Tmax (K)."""
    return 1.0 / np.linspace(1.0 / Tmax, 1.0 / Tmin, n)


def simulated_ea_std(T, sigma_ln, repeats=4000, seed=3):
    """Spread (standard deviation) of the fitted Ea over many synthetic experiments."""
    rng = np.random.default_rng(seed)
    T = np.asarray(T, dtype=float)
    x = 1000.0 / T
    eas = np.empty(repeats)
    for i in range(repeats):
        y = np.log(arrhenius_k(T)) + sigma_ln * rng.standard_normal(T.size)
        eas[i] = -np.polyfit(x, y, 1)[0] * R_GAS
    return float(eas.std(ddof=1)), float(eas.mean())


# %% [markdown]
# ## Step 3: the modified Arrhenius form
# Many fits use k = A T^n exp(-Ea/(R T)), so ln k = ln A + n ln T - (Ea/R)(1/T). That is a
# plane fit with three unknowns (ln A, n, Ea), solved by linear least squares.

# %%
def fit_modified(T, k):
    """Returns (A, n, Ea in kJ/mol) from linear least squares on [1, ln T, -1000/T]."""
    T, k = np.asarray(T, dtype=float), np.asarray(k, dtype=float)
    M = np.column_stack([np.ones(T.size), np.log(T), -1000.0 / T])
    c = np.linalg.lstsq(M, np.log(k), rcond=None)[0]
    return float(np.exp(c[0])), float(c[1]), float(c[2] * R_GAS)


# %% [markdown]
# ## Step 4: see it
# Left: the same six noisy points fitted with two different temperature windows. Right: the
# standard error of Ea against the width of the 1000/T range, theory against simulation.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    sig = 0.05
    wide = even_in_inverse_T(500, 1500, 6)
    narrow = even_in_inverse_T(850, 1000, 6)
    print("wide   : SE(Ea) =", round(ea_se(wide, sig), 2), "kJ/mol, simulated", round(simulated_ea_std(wide, sig)[0], 2))
    print("narrow : SE(Ea) =", round(ea_se(narrow, sig), 2), "kJ/mol, simulated", round(simulated_ea_std(narrow, sig)[0], 2))

    fig, ax = plt.subplots(1, 2, figsize=(9, 3.8))
    for T, name, col in ((wide, "500-1500 K", "tab:blue"), (narrow, "850-1000 K", "tab:red")):
        k = synthetic(T, sig, seed=5)
        A, Ea = fit_arrhenius(T, k)
        xg = np.linspace(0.6, 2.1, 20)
        ax[0].plot(1000 / T, np.log(k), "o", color=col, label=f"{name}: Ea = {Ea:.0f}")
        ax[0].plot(xg, np.log(A) - Ea / R_GAS * xg, color=col, lw=1)
    ax[0].set_xlabel("1000 / T (1/K x 1000)")
    ax[0].set_ylabel("ln k (k in 1/s)")
    ax[0].set_title("Same noise, two temperature windows")
    ax[0].grid(alpha=0.3)
    ax[0].legend()
    Tmaxs = np.linspace(900, 2000, 12)
    th = [ea_se(even_in_inverse_T(800, t, 6), sig) for t in Tmaxs]
    sm = [simulated_ea_std(even_in_inverse_T(800, t, 6), sig, repeats=1500)[0] for t in Tmaxs]
    ax[1].plot(Tmaxs, th, label="theory R sigma / sqrt(Sxx)")
    ax[1].plot(Tmaxs, sm, "o", label="simulation")
    ax[1].set_xlabel("highest temperature Tmax (K), lowest fixed at 800 K")
    ax[1].set_ylabel("standard error of Ea (kJ/mol)")
    ax[1].set_title("A wider 1/T range pins Ea down")
    ax[1].grid(alpha=0.3)
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(OUT / "design_range.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
