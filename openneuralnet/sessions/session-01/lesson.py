"""Session 1 (Level 1): a neuron adds up weighted inputs, and learning nudges a line.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a neuron, a line and a nudge
# **A. Real-world problem.** A phone decides "photo of a cat or not" from numbers, not from
# rules typed by a programmer. The simplest decider is one artificial *neuron*: it adds up
# its inputs, each multiplied by a *weight*, and fires if the total is big enough.
#
# **Plan.** (1) build the neuron, (2) see that it draws a line between two groups of points,
# (3) let it learn by nudging the line whenever it makes a mistake.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the neuron
# Ten points, each with two inputs (x1, x2) and a label: 1 for group "A" and 0 for group "B".
# The neuron computes `z = w1*x1 + w2*x2 + b` and fires (outputs 1) when `z > 0`.
# The numbers w1, w2 are the *weights*; b is the *bias* (a head start or a handicap).
#
# Check by hand with w = (1, 1), b = 0 and the point (2, 2.5): z = 2 + 2.5 = 4.5 > 0, so it fires.

# %%
X = np.array([[2, 2.5], [-2, -1], [3, 1.5], [-3, 0.5], [2.5, 3.5],
              [-1.5, -2.5], [3.5, 3], [0.5, -0.5], [4, 2], [-2.5, -3]], dtype=float)
Y = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])


def neuron(x, w, b):
    """Weighted sum z and the fired output (1 if z > 0 else 0). Works for one point or many rows."""
    z = np.asarray(x, dtype=float) @ np.asarray(w, dtype=float) + b
    return z, (z > 0).astype(int)


def n_correct(X, y, w, b):
    """How many of the points the neuron labels correctly."""
    return int(np.sum(neuron(X, w, b)[1] == y))


# %% [markdown]
# ## Step 2: the neuron is a line
# The neuron changes its mind exactly where z = 0, that is where `w1*x1 + w2*x2 + b = 0`.
# That is a straight line in the (x1, x2) plane. Points on one side fire, points on the other
# side do not. So "a neuron decides" means "a line splits the points into two groups".

# %%
def line_x2(x1, w, b):
    """x2 of the dividing line at a given x1 (needs w2 != 0)."""
    return -(w[0] * x1 + b) / w[1]


# %% [markdown]
# ## Step 3: learning is nudging the line
# Start with any line. Visit the points one by one. If the neuron is right, do nothing.
# If it is wrong, nudge: add `(label - output) * point` to the weights and `(label - output)`
# to the bias. This is the *perceptron rule*. A missed A point pulls the line towards it; a
# wrongly-fired B point pushes the line away.

# %%
def perceptron_train(X, y, w0=(1.0, -2.0), b0=0.0, max_epochs=50):
    """Perceptron rule. Returns (w, b, history) where history[k] = (w, b) after the k-th nudge
    (history[0] is the start)."""
    w, b = np.array(w0, dtype=float), float(b0)
    history = [(w.copy(), b)]
    for _ in range(max_epochs):
        changed = 0
        for x, t in zip(X, y):
            out = int(x @ w + b > 0)
            if out != t:
                w = w + (t - out) * x
                b = b + (t - out)
                changed += 1
                history.append((w.copy(), b))
        if changed == 0:
            break
    return w, b, history


# %% [markdown]
# ## Step 4: see it
# Left: the line after each nudge. Right: how many of the 10 points are right after each nudge.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    w, b, hist = perceptron_train(X, Y)
    print(f"learned w = {w}, b = {b} after {len(hist) - 1} nudges; correct {n_correct(X, Y, w, b)} of 10")

    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.scatter(*X[Y == 1].T, c="tab:blue", label="group A (label 1)")
    ax.scatter(*X[Y == 0].T, c="tab:orange", label="group B (label 0)")
    xs = np.array([-5.0, 5.0])
    for k, (wk, bk) in enumerate(hist):
        if wk[1] != 0:
            ax.plot(xs, line_x2(xs, wk, bk), lw=2.5 if k == len(hist) - 1 else 1,
                    ls="-" if k == len(hist) - 1 else "--", label=f"after {k} nudges")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_xlabel("input x1")
    ax.set_ylabel("input x2")
    ax.set_title("A neuron is a line; learning moves it")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="lower right")
    fig.savefig(OUT / "perceptron_line.png", dpi=120)

    scores = [n_correct(X, Y, wk, bk) for wk, bk in hist]
    fig2, ax2 = plt.subplots(figsize=(5.5, 3.6))
    ax2.plot(range(len(scores)), scores, "o-")
    ax2.set_xlabel("number of nudges so far")
    ax2.set_ylabel("points classified correctly (of 10)")
    ax2.set_title("Each nudge fixes the neuron a little")
    ax2.set_ylim(0, 10.5)
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "correct_vs_nudges.png", dpi=120)
    print("correct after each nudge:", scores)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
