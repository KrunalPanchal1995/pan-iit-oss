"""Session 1 (Level 1): sort fruit with a rule, draw a boundary, count two kinds of mistake.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a rule that splits two groups
# **A. Real-world problem.** A packing line must send ripe fruit to the shop and keep unripe
# fruit back. A camera gives two numbers per fruit: its size (cm) and a colour score
# (0 = green, 10 = deep red). A *classifier* is a rule that turns those two numbers into a
# decision. Today you write rules, draw their boundary, and count how they go wrong.
# (General education only, with made-up data.)

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# Twelve fruit by hand: (size cm, colour score, label). label 1 = ripe, 0 = unripe.
TOY = [
    (2.0, 2.0, 0), (3.0, 4.0, 0), (4.0, 2.0, 0), (3.5, 6.0, 0), (5.0, 3.0, 0), (6.0, 4.5, 0),
    (4.5, 7.0, 1), (6.0, 8.0, 1), (7.0, 6.0, 1), (8.0, 9.0, 1), (7.5, 4.0, 1), (5.5, 5.5, 1),
]


# %% [markdown]
# ## Step 1: a rule is a yes/no question
# The simplest rule asks one question about one number: "is the size above t?"
# A better rule asks about a mix of both numbers. The set of points where the answer flips
# is the **decision boundary**. For the line rule below, the boundary is the straight line
#
#     x * cos(a) + y * sin(a) = c
#
# where x is size, y is colour, a is the angle of the line's normal, and c is how far the
# line sits from the origin. Fruit on the far side are called ripe (1), others unripe (0).

# %%
def size_rule(points, t):
    """Predict 1 when size is above t (one number only)."""
    return (np.asarray(points)[:, 0] > t).astype(int)


def line_rule(points, angle_deg, c):
    """Predict 1 when x*cos(a) + y*sin(a) > c."""
    a = np.radians(angle_deg)
    p = np.asarray(points)
    return (p[:, 0] * np.cos(a) + p[:, 1] * np.sin(a) > c).astype(int)


# %% [markdown]
# ## Step 2: two kinds of mistake
# Call "ripe" the thing we are looking for ("positive").
# * **False alarm** (false positive): we said ripe, the fruit is unripe.
# * **Miss** (false negative): we said unripe, the fruit is ripe.
# They cost different things, so we count them separately.

# %%
def count_mistakes(y_true, y_pred):
    """Return (false_alarms, misses)."""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    false_alarms = int(np.sum((y_pred == 1) & (y_true == 0)))
    misses = int(np.sum((y_pred == 0) & (y_true == 1)))
    return false_alarms, misses


def accuracy(y_true, y_pred):
    return float(np.mean(np.asarray(y_true) == np.asarray(y_pred)))


def toy_arrays():
    arr = np.array(TOY, dtype=float)
    return arr[:, :2], arr[:, 2].astype(int)


# %% [markdown]
# ## Step 3: a bigger, random batch
# Real fruit vary, so the two groups overlap. `make_fruit` draws two clusters from normal
# distributions with a fixed seed, so everyone gets the same picture.

# %%
def make_fruit(n_each=100, seed=3):
    rng = np.random.default_rng(seed)
    unripe = rng.normal([3.0, 3.0], 1.3, size=(n_each, 2))
    ripe = rng.normal([6.5, 6.5], 1.3, size=(n_each, 2))
    X = np.vstack([unripe, ripe])
    y = np.r_[np.zeros(n_each, int), np.ones(n_each, int)]
    return X, y


def sweep_offset(X, y, angle_deg, cs):
    """False alarms and misses as the line slides: the trade-off curve."""
    fa, ms = [], []
    for c in cs:
        f, m = count_mistakes(y, line_rule(X, angle_deg, c))
        fa.append(f)
        ms.append(m)
    return np.array(fa), np.array(ms)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    Xt, yt = toy_arrays()
    pred = line_rule(Xt, 45, 7.0)
    print("toy: mistakes (false alarms, misses) =", count_mistakes(yt, pred), " accuracy", round(accuracy(yt, pred), 3))

    X, y = make_fruit()
    for name, pr in [("size only (t = 4.75)", size_rule(X, 4.75)), ("size + colour line", line_rule(X, 45, 6.7))]:
        fa, ms = count_mistakes(y, pr)
        print(f"{name:24s} false alarms {fa:3d}  misses {ms:3d}  accuracy {accuracy(y, pr):.3f}")

    fig, ax = plt.subplots(figsize=(5.5, 5))
    pr = line_rule(X, 45, 6.7)
    ax.scatter(*X[y == 0].T, c="tab:green", s=14, label="unripe")
    ax.scatter(*X[y == 1].T, c="tab:red", s=14, label="ripe")
    wrong = pr != y
    ax.scatter(*X[wrong].T, facecolors="none", edgecolors="k", s=60, label="mistake")
    xs = np.linspace(0, 10, 2)
    ax.plot(xs, (6.7 - xs * np.cos(np.radians(45))) / np.sin(np.radians(45)), "k--", label="boundary")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    ax.set_xlabel("size (cm)"); ax.set_ylabel("colour score (0 green to 10 red)")
    ax.set_title("Two clusters, one boundary, some mistakes")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(OUT / "clusters_boundary.png", dpi=120)

    cs = np.linspace(2, 11, 91)
    fa, ms = sweep_offset(X, y, 45, cs)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(cs, fa, label="false alarms")
    ax2.plot(cs, ms, label="misses")
    ax2.set_xlabel("line offset c (score units)"); ax2.set_ylabel("count (out of 100 each)")
    ax2.set_title("Sliding the boundary trades one mistake for the other")
    ax2.legend(); ax2.grid(alpha=0.3)
    fig2.tight_layout(); fig2.savefig(OUT / "two_mistakes.png", dpi=120)
    print("c with equal counts near:", cs[np.argmin(np.abs(fa - ms))])
