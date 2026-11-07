"""Session 2 (Level 2): formulas as expression trees, complexity versus error.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: a formula is a tree; simple versus accurate
# **A. Real-world problem.** Kepler found that a planet's orbital period T (years) and its
# distance a from the Sun (astronomical units, AU) are tied by a law. Many formulas fit a
# few planets; which one should we trust? Size and error pull in opposite directions.
#
# **Plan.** (1) represent a formula as a tree and evaluate it, (2) count its nodes
# (complexity), (3) measure the mean squared error, (4) compare three hand-written
# candidates, (5) hold out the outer planets to expose the one that overfits.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: expression trees
# A tree is a nested tuple. Leaves: ('x',) the variable, ('c', 2.5) a number. Branches: an
# operation and its children, such as ('add', left, right) or ('sqrt', child).
# Allowed operations: add, sub, mul, div, sqrt, exp, log, sq (square). Evaluation walks the
# tree from the leaves up, using numpy on a whole array of x values at once.

# %%
def evaluate(tree, x):
    """Value of the tree at x (an array). Invalid operations give nan."""
    x = np.asarray(x, float)
    with np.errstate(all="ignore"):
        k = tree[0]
        if k == "x":
            return x.copy()
        if k == "c":
            return np.full(x.shape, float(tree[1]))
        if k == "sqrt":
            return np.sqrt(evaluate(tree[1], x))
        if k == "exp":
            return np.exp(evaluate(tree[1], x))
        if k == "log":
            return np.log(evaluate(tree[1], x))
        if k == "sq":
            return evaluate(tree[1], x) ** 2
        a, b = evaluate(tree[1], x), evaluate(tree[2], x)
        return {"add": a + b, "sub": a - b, "mul": a * b, "div": a / b}[k]


def complexity(tree):
    """Number of nodes (leaves and operations) in the tree."""
    return 1 + sum(complexity(ch) for ch in tree[1:] if isinstance(ch, tuple))


def show(tree):
    """Readable text for a tree."""
    k = tree[0]
    if k == "x":
        return "x"
    if k == "c":
        return f"{tree[1]:.4g}"
    if k in ("sqrt", "exp", "log", "sq"):
        return f"{k}({show(tree[1])})"
    sym = {"add": "+", "sub": "-", "mul": "*", "div": "/"}[k]
    return f"({show(tree[1])} {sym} {show(tree[2])})"


def mse(tree, x, y):
    """Mean squared error between the tree and the data (units of y, squared)."""
    return float(np.mean((evaluate(tree, x) - np.asarray(y, float)) ** 2))


# %% [markdown]
# ## Step 2: the data (Kepler's third law)
# Round textbook values for six planets: semi-major axis a in AU and period T in years.
# Kepler's third law says T^2 is proportional to a^3, so T = a^1.5 in these units.

# %%
PLANETS = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn"]
A_AU = np.array([0.387, 0.723, 1.000, 1.524, 5.203, 9.537])
T_YR = np.array([0.241, 0.615, 1.000, 1.881, 11.862, 29.457])

TRAIN = slice(0, 4)      # Mercury ... Mars: used to build the formula
TEST = slice(4, 6)       # Jupiter, Saturn: held out, never used to fit


# %% [markdown]
# ## Step 3: three hand-written candidates, each with fitted constants
# * A (small): T = c * a. One number, 3 nodes.
# * B (the law): T = c * sqrt(a * a * a). 8 nodes.
# * C (large): a cubic polynomial c0 + a (c1 + a (c2 + a c3)). Four numbers, 13 nodes.
# Constants that enter linearly are found by least squares (numpy `lstsq`).

# %%
def cand_a(c):
    return ("mul", ("c", c), ("x",))


def cand_b(c):
    return ("mul", ("c", c), ("sqrt", ("mul", ("x",), ("mul", ("x",), ("x",)))))


def cand_c(cs):
    c0, c1, c2, c3 = cs
    return ("add", ("c", c0), ("mul", ("x",), ("add", ("c", c1), ("mul", ("x",), ("add", ("c", c2), ("mul", ("c", c3), ("x",)))))))


def fit_candidates(x, y):
    """Fit the constants of A, B and C on (x, y). Returns {name: tree}."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ca = float(np.sum(x * y) / np.sum(x * x))
    shape_b = x ** 1.5
    cb = float(np.sum(shape_b * y) / np.sum(shape_b ** 2))
    V = np.vander(x, 4, increasing=True)
    cs, *_ = np.linalg.lstsq(V, y, rcond=None)
    return {"A": cand_a(ca), "B": cand_b(cb), "C": cand_c(cs)}


def report(x_tr, y_tr, x_te, y_te):
    """Rows (name, nodes, train mse, test mse) for A, B, C."""
    trees = fit_candidates(x_tr, y_tr)
    return [(k, complexity(t), mse(t, x_tr, y_tr), mse(t, x_te, y_te)) for k, t in trees.items()]


# %% [markdown]
# ## Step 4: simple versus accurate, and the held-out test
# On the training planets C has the smallest error (it has the most freedom). But the
# held-out planets, Jupiter and Saturn, lie outside the training range, and there C fails
# badly while B stays close. Choosing the formula by training error alone would have been
# a mistake: we must judge by data the fitting never saw.

# %%
def pareto_indices(points):
    """Indices of points (complexity, error) not beaten by a simpler-or-equal, lower-error point."""
    keep = []
    for i, (c, e) in enumerate(points):
        if not any((c2 <= c and e2 < e) or (c2 < c and e2 <= e) for j, (c2, e2) in enumerate(points) if j != i):
            keep.append(i)
    return keep


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    rows = report(A_AU[TRAIN], T_YR[TRAIN], A_AU[TEST], T_YR[TEST])
    trees = fit_candidates(A_AU[TRAIN], T_YR[TRAIN])
    for name, nodes, tr, te in rows:
        print(f"{name}: {nodes:2d} nodes   train MSE = {tr:9.4f}   held-out MSE = {te:9.4f}   {show(trees[name])[:70]}")

    aa = np.linspace(0.2, 10, 300)
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 4))
    ax[0].plot(A_AU[TRAIN], T_YR[TRAIN], "ko", label="training planets")
    ax[0].plot(A_AU[TEST], T_YR[TEST], "r^", label="held-out planets")
    for name, t in trees.items():
        ax[0].plot(aa, evaluate(t, aa), label=f"candidate {name}")
    ax[0].set_ylim(0, 35)
    ax[0].set_xlabel("semi-major axis a (AU)")
    ax[0].set_ylabel("orbital period T (years)")
    ax[0].set_title("Three candidate formulas")
    ax[0].grid(alpha=0.3)
    ax[0].legend()
    for name, nodes, tr, te in rows:
        ax[1].semilogy([nodes], [tr], "o", label=f"{name} train")
        ax[1].semilogy([nodes], [te], "^", label=f"{name} held-out")
    ax[1].set_xlabel("complexity (nodes)")
    ax[1].set_ylabel("mean squared error (years squared)")
    ax[1].set_title("Complexity versus error")
    ax[1].grid(alpha=0.3)
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "kepler_candidates.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
