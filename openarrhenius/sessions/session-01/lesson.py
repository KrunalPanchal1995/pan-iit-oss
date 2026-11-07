"""Session 1 (Level 1): reactions speed up steeply with temperature, and a straight line tames the curve.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: reaction speed rises steeply with temperature
# **A. Real-world problem.** Food spoils faster in a warm kitchen, and a flame needs heat to
# start. A chemist measures a *rate constant* k (how fast one reaction goes) at five
# temperatures. The numbers climb so steeply that a normal graph is useless. Is there a way
# to draw them so that they fall on a straight line, and what does the line tell us?
#
# **Plan.** (1) a formula for k(T), (2) a small table of "measured" data, (3) change the axes
# so the data become a straight line, (4) fit that line by hand and read the activation energy.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

R_GAS = 8.314462618          # gas constant, J/(mol K)
A_TRUE = 1.0e13              # true pre-exponential factor of the toy reaction, 1/s
EA_TRUE = 150.0              # true activation energy, kJ/mol
T_DATA = np.array([600.0, 700.0, 800.0, 900.0, 1000.0])   # temperatures, K


# %% [markdown]
# ## Step 1: the Arrhenius law
# k = A * exp(-Ea / (R T)). T is the temperature in kelvin, Ea the activation energy (the
# energy hill the molecules must climb), R the gas constant, A a rate scale (1/s here).
# The exponent -Ea/(R T) is a pure number: Ea is converted from kJ/mol to J/mol first.

# %%
def arrhenius_k(T, A=A_TRUE, Ea_kJ=EA_TRUE):
    """Rate constant (1/s) at temperature T (K)."""
    return A * np.exp(-Ea_kJ * 1000.0 / (R_GAS * np.asarray(T, dtype=float)))


def speedup(T1, T2, Ea_kJ=EA_TRUE):
    """How many times faster the reaction goes at T2 than at T1 (A cancels)."""
    return float(arrhenius_k(T2, 1.0, Ea_kJ) / arrhenius_k(T1, 1.0, Ea_kJ))


# %% [markdown]
# ## Step 2: "measured" data
# Real measurements are never exact. We make a data set from the true law and multiply every
# k by a random factor of about 5 percent (a *multiplicative* error). A fixed random seed
# means everybody gets the same table.

# %%
def make_data(seed=1, T=T_DATA, A=A_TRUE, Ea_kJ=EA_TRUE, rel_noise=0.05):
    rng = np.random.default_rng(seed)
    k = arrhenius_k(T, A, Ea_kJ) * np.exp(rel_noise * rng.standard_normal(len(T)))
    return np.asarray(T, dtype=float), k


# %% [markdown]
# ## Step 3: the right axes
# Take logs: ln k = ln A - (Ea/R) * (1/T). Plot y = ln k against x = 1000/T and the data fall
# on a straight line of slope s = -Ea/(1000 R), so Ea (kJ/mol) = -s * R with R = 8.3145.
# The line is fitted by *least squares*: choose the line that makes the sum of squared
# vertical gaps smallest. The hand formulas are slope = Sxy/Sxx and intercept = ybar - slope*xbar,
# where Sxx = sum (x - xbar)^2 and Sxy = sum (x - xbar)(y - ybar).

# %%
def to_xy(T, k):
    """Straight-line coordinates: x = 1000/T (1/K * 1000), y = ln k."""
    return 1000.0 / np.asarray(T, dtype=float), np.log(np.asarray(k, dtype=float))


def fit_line(x, y):
    """Least-squares line by hand. Returns (slope, intercept)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    xm, ym = x.mean(), y.mean()
    slope = np.sum((x - xm) * (y - ym)) / np.sum((x - xm) ** 2)
    return float(slope), float(ym - slope * xm)


def ea_from_slope(slope):
    """Activation energy in kJ/mol from the slope of ln k against 1000/T."""
    return float(-slope * R_GAS)


# %% [markdown]
# ## Step 4: see it
# Left: k against T on a normal axis is a steep curve; the low-temperature points are squashed
# against the floor. Right: ln k against 1000/T is a straight line and the fit recovers Ea.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    T, k = make_data()
    x, y = to_xy(T, k)
    s, b = fit_line(x, y)
    print("speed-up from 600 K to 700 K:", round(speedup(600, 700), 1))
    print("slope", round(s, 3), "intercept", round(b, 3), "Ea", round(ea_from_slope(s), 1), "kJ/mol")

    Tg = np.linspace(550, 1050, 200)
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.8))
    ax[0].plot(Tg, arrhenius_k(Tg), color="gray", label="true law")
    ax[0].plot(T, k, "o", label="measured")
    ax[0].set_xlabel("temperature T (K)")
    ax[0].set_ylabel("rate constant k (1/s)")
    ax[0].set_title("Normal axes: a steep curve")
    ax[0].grid(alpha=0.3)
    ax[0].legend()
    xg = np.linspace(x.min() - 0.05, x.max() + 0.05, 50)
    ax[1].plot(xg, s * xg + b, color="gray", label=f"fit, Ea = {ea_from_slope(s):.0f} kJ/mol")
    ax[1].plot(x, y, "o", label="measured")
    ax[1].set_xlabel("1000 / T (1/K x 1000)")
    ax[1].set_ylabel("ln k (k in 1/s)")
    ax[1].set_title("Arrhenius axes: a straight line")
    ax[1].grid(alpha=0.3)
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(OUT / "arrhenius_axes.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
