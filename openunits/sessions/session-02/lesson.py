"""Session 2 (Level 2): dimensional analysis with exponent vectors of M, L, T.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: dimensional analysis
# **A. Real-world problem.** Units can disagree without anyone noticing: an engineer adds a
# length to a time, or feeds feet into a formula written for metres. Before trusting any
# equation we can check its *dimensions*: every term must be the same kind of quantity.
# Today you write each kind of quantity as a vector of exponents of mass (M), length (L) and
# time (T), check equations with it, and measure how big a hidden unit mistake becomes.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
G = 9.80665          # standard gravity, m/s^2


# %% [markdown]
# ## Step 1: a dimension is a vector of exponents
# speed = length / time = L T^-1, so its vector is [M, L, T] = [0, 1, -1].
# Multiplying quantities adds the vectors; dividing subtracts them; a power multiplies them.

# %%
DIMS = {
    "dimensionless": [0, 0, 0], "mass": [1, 0, 0], "length": [0, 1, 0], "time": [0, 0, 1],
    "area": [0, 2, 0], "volume": [0, 3, 0], "speed": [0, 1, -1], "acceleration": [0, 1, -2],
    "force": [1, 1, -2], "impulse": [1, 1, -1], "momentum": [1, 1, -1], "energy": [1, 2, -2],
    "pressure": [1, -1, -2], "density": [1, -3, 0], "viscosity": [1, -1, -1],
}


def dim(x):
    """Dimension vector from a name (like 'force') or from a list [M, L, T]."""
    return np.array(DIMS[x] if isinstance(x, str) else x, dtype=float)


def dim_str(d):
    names = ("M", "L", "T")
    parts = [f"{n}^{e:g}" if e != 1 else n for n, e in zip(names, d) if e != 0]
    return " ".join(parts) if parts else "1 (no dimension)"


def expr_dim(factors):
    """Dimension of a product of factors [(quantity, power), ...]."""
    total = np.zeros(3)
    for q, power in factors:
        total = total + power * dim(q)
    return total


def same_dim(a, b):
    return bool(np.allclose(dim(a), dim(b)))


# %% [markdown]
# ## Step 2: check an equation
# An equation  left = term1 + term2  is dimensionally possible only if every term has the same
# dimension as the left side. (Passing the test does not prove the equation is right; failing
# it proves the equation is wrong.)

# %%
def check_sum(left, terms):
    """left: a quantity; terms: list of factor lists. Returns one True/False per term."""
    return [same_dim(expr_dim(t), left) for t in terms]


# %% [markdown]
# ## Step 3: let dimensions find the formula
# A pendulum's period T might depend on its length L, gravity g and mass m:  T ~ L^p g^q m^r.
# Match exponents of M, L, T on both sides. That is three linear equations, solved with numpy.

# %%
def find_exponents(quantities, target):
    """Exponents e so that product(quantity_i ** e_i) has the dimension `target`."""
    A = np.array([dim(q) for q in quantities]).T       # columns = dimension vectors
    return np.linalg.solve(A, dim(target))


# %% [markdown]
# ## Step 4: how big does a hidden unit mistake get?
# If a length is wrong by a factor f (for example feet read as metres), a quantity with
# dimension L^b is wrong by f^b. Mass factor m and time factor t work the same way:
#     error factor = m_f^M * l_f^L * t_f^T.
# For independent measurements with small relative errors, errors add up as shown below.

# %%
def scale_factor(d, mass=1.0, length=1.0, time=1.0):
    """How much a quantity of dimension d is multiplied by when units are rescaled."""
    d = dim(d)
    return float(mass ** d[0] * length ** d[1] * time ** d[2])


def rel_error_worst(powers, rel_errors):
    """Worst case relative error of a product x1^n1 * x2^n2 ... (errors all push the same way)."""
    return float(np.sum(np.abs(powers) * np.abs(rel_errors)))


def rel_error_rss(powers, rel_errors):
    """Typical relative error of a product when the errors are independent (root sum of squares)."""
    return float(np.sqrt(np.sum((np.asarray(powers) * np.asarray(rel_errors)) ** 2)))


def pendulum_period(length_m, g=G):
    """Small-swing period of a simple pendulum, in seconds (2 pi comes from physics, not dimensions)."""
    return 2 * np.pi * np.sqrt(length_m / g)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    good = check_sum("length", [[("speed", 1), ("time", 1)], [("acceleration", 1), ("time", 2)]])
    bad = check_sum("length", [[("speed", 1), ("time", 1)], [("acceleration", 1), ("time", 1)]])
    print("s = u t + a t^2 (per term, ok?):", good, "  s = u t + a t:", bad)
    p, q, r = find_exponents(["length", "acceleration", "mass"], "time")
    print(f"pendulum period ~ L^{p:g} g^{q:g} m^{r:g}")
    print(f"period of a 1.000 m pendulum: {pendulum_period(1.0):.3f} s")
    for name in ("length", "area", "volume", "speed", "force"):
        print(f"feet read as metres: {name:7s} {dim_str(dim(name)):10s} wrong by x{1 / scale_factor(name, length=0.3048):.2f}")

    names = ["length", "area", "volume"]
    wrong = [1 / scale_factor(n, length=0.3048) for n in names]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(names, wrong, color=["#2a9d8f", "#e9c46a", "#d9534f"])
    for i, w in enumerate(wrong):
        ax.text(i, w + 0.5, f"x{w:.2f}", ha="center")
    ax.set_xlabel("quantity (dimension L^1, L^2, L^3)")
    ax.set_ylabel("error factor when feet are read as metres")
    ax.set_title("A unit mistake grows with the power of length")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(OUT / "error_factors.png", dpi=120)

    length = np.linspace(0.05, 2, 100)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(length, pendulum_period(length), label="2 pi sqrt(L/g)  (correct dimensions)")
    ax2.plot(length, length / G * 2 * np.pi, "--", label="2 pi L/g  (wrong dimensions)")
    ax2.set_xlabel("pendulum length (m)")
    ax2.set_ylabel("computed value (s for the solid curve)")
    ax2.set_title("Only one power of L and g gives a time")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "pendulum_dimensions.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the README questions (F), then run the checkpoint.
