"""Session 1 (Level 1): data that follow a law, and a computer that guesses the formula.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: can a computer guess the formula?
# **A. Real-world problem.** Drop a ball and note how far it has fallen after each second.
# Galileo did this with rolling balls and found a law. Today a computer can search for
# the law by trying many formulas and keeping the one that matches the data best.
#
# **Plan.** (1) make fall data that follow a law with a little measurement noise,
# (2) write a few candidate formulas with one unknown number c each, (3) fit c for each,
# (4) score each by its error, (5) read the winner and what it tells us about gravity g.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the data
# A ball dropped from rest falls a distance d = (1/2) g t^2 metres after t seconds,
# where g is the acceleration due to gravity (9.81 m/s^2 on Earth). Real measurements are
# never exact, so we multiply each distance by (1 + a small error). The six errors below
# are fixed numbers (2%, -3%, 1%, -2%, 3%, -1%) so that everyone gets the same data.

# %%
T_OBS = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0])             # seconds
REL_ERR = np.array([0.02, -0.03, 0.01, -0.02, 0.03, -0.01])  # fractional measurement errors


def fall_distance(t, g=9.81):
    """True distance fallen (metres) after t seconds, starting from rest."""
    return 0.5 * g * np.asarray(t, float) ** 2


def fall_data(g=9.81):
    """Measured distances (metres) at T_OBS, with the fixed measurement errors."""
    return fall_distance(T_OBS, g) * (1.0 + REL_ERR)


# %% [markdown]
# ## Step 2: a library of candidate formulas
# Each formula has the form d = c * f(t), where f is a shape (t, t squared, ...) and c is
# one unknown number. We can find the best c with a formula. Minimising the sum of
# squared differences gives
#     c = sum(f * d) / sum(f * f).
# The score is the mean squared error (MSE): the average of (data - formula)^2, in metres squared.

# %%
LIBRARY = {
    "c * sqrt(t)": np.sqrt,
    "c * t": lambda t: t,
    "c * t^2": lambda t: t ** 2,
    "c * t^3": lambda t: t ** 3,
    "c * exp(t)": np.exp,
    "c * exp(-t)": lambda t: np.exp(-np.asarray(t, float)),
}


# %% [markdown]
# ## A second law: cooling tea
# In this synthetic example, tea starts 60 degrees C above room temperature. We record
# its temperature excess (above room temperature) every half minute; this example follows
# the simple exponential model excess = c * exp(-t).

# %%
COOLING_T_OBS = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])  # minutes


def cooling_data():
    """Synthetic tea temperature above room temperature (degrees C) at COOLING_T_OBS."""
    return COOLING_T_OBS.copy(), 60.0 * np.exp(-COOLING_T_OBS)


def fit_c(shape, d):
    """Best c and mean squared error for d = c * shape."""
    shape = np.asarray(shape, float)
    c = float(np.sum(shape * d) / np.sum(shape * shape))
    mse = float(np.mean((d - c * shape) ** 2))
    return c, mse


def search_library(t, d):
    """Try every formula in LIBRARY; return a list of (name, c, mse) sorted by mse."""
    rows = [(name, *fit_c(f(t), d)) for name, f in LIBRARY.items()]
    return sorted(rows, key=lambda r: r[2])


# %% [markdown]
# ## Step 3: a wider search over powers
# Instead of a short list, try d = c * t^n for many exponents n from 0.5 to 3.5. The
# exponent with the lowest error is the computer's guess for the shape of the law.

# %%
def best_exponent(t, d, exponents=None):
    """Return (n, c, mse) for the exponent n with the lowest mse, and the whole curve of mse."""
    if exponents is None:
        exponents = np.arange(0.5, 3.51, 0.1)
    curve = [fit_c(np.asarray(t, float) ** n, d)[1] for n in exponents]
    i = int(np.argmin(curve))
    c, mse = fit_c(np.asarray(t, float) ** exponents[i], d)
    return float(exponents[i]), c, mse, np.array(curve), exponents


def gravity_from_c(c):
    """If d = c t^2 then c = g/2, so g = 2 c (m/s^2)."""
    return 2.0 * c


# %% [markdown]
# ## Step 4: see it
# Left: the data and three candidate curves. Right: error against the exponent n; the
# deep valley sits at n = 2.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    d = fall_data()
    for name, c, mse in search_library(T_OBS, d):
        print(f"{name:12s} c = {c:8.3f}   MSE = {mse:10.3f} m^2")
    n, c, mse, curve, exps = best_exponent(T_OBS, d)
    print(f"best exponent n = {n:.1f}, c = {c:.3f}, so g = {gravity_from_c(c):.2f} m/s^2")

    tt = np.linspace(0, 3.2, 200)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(T_OBS, d, "ko", label="measured data")
    for name, f in (("c * t", LIBRARY["c * t"]), ("c * t^2", LIBRARY["c * t^2"]), ("c * t^3", LIBRARY["c * t^3"])):
        cc, _ = fit_c(f(T_OBS), d)
        ax.plot(tt, cc * f(tt), label=name)
    ax.set_xlabel("time t (s)")
    ax.set_ylabel("distance fallen d (m)")
    ax.set_title("Which formula follows the falling ball?")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "fall_candidates.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.semilogy(exps, curve, "o-")
    ax2.set_xlabel("exponent n in d = c t^n")
    ax2.set_ylabel("mean squared error (m^2)")
    ax2.set_title("Error valley: the best exponent is 2")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "error_vs_exponent.png", dpi=120)

    cooling_t, excess = cooling_data()
    cooling_c, _ = fit_c(LIBRARY["c * exp(-t)"](cooling_t), excess)
    cooling_tt = np.linspace(0, 3.0, 200)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(cooling_t, excess, "ko", label="synthetic tea data")
    ax3.plot(cooling_tt, cooling_c * LIBRARY["c * exp(-t)"](cooling_tt), label="c * exp(-t)")
    ax3.set_xlabel("time t (minutes)")
    ax3.set_ylabel("temperature above room temperature (°C)")
    ax3.set_title("Cooling tea follows an exponential shape")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "cooling_tea.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
