"""Session 2 (Level 2): the perceptron rule, the sigmoid, logistic regression and why XOR is hard.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: from a line to a probability, and the wall called XOR
# **A. Real-world problem.** A spam filter must say "how likely is this message spam?", not
# only "yes or no". And it must learn its settings from examples, by a rule we can check.
#
# **Plan.** (1) the perceptron rule always finishes on separable data, (2) the sigmoid turns a
# score into a probability, (3) logistic regression learns by gradient descent and we check
# its gradient against finite differences, (4) the learning rate can be too small or too
# large, (5) no single line can solve XOR.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: the perceptron rule on separable data
# Labels t = +1 or -1. Write the input with a constant 1 added, x~ = (x1, x2, 1), and the
# weights with the bias included, w~ = (w1, w2, b). Rule: if `t * (w~ . x~) <= 0` (wrong or on
# the line), then `w~ = w~ + t * x~`. If a line exists that separates the data with margin
# gamma (the smallest distance of any point to it, measured with unit-length weights) and
# every x~ has length at most R, then starting from w~ = 0 the rule makes at most (R / gamma)^2
# updates and then stops (the perceptron convergence theorem).

# %%
def make_separable(n, gap, seed):
    """n points uniform in [-3, 3]^2, labelled by the true line w.x + b = 0, with every point at
    least `gap` away from it. Returns X, y (0/1), unit true weights, true bias."""
    rng = np.random.default_rng(seed)
    wt = np.array([1.0, 2.0]) / np.sqrt(5.0)
    bt = 0.3
    pts = []
    while len(pts) < n:
        x = rng.uniform(-3, 3, 2)
        if abs(x @ wt + bt) >= gap:
            pts.append(x)
    X = np.array(pts)
    return X, (X @ wt + bt > 0).astype(int), wt, bt


def perceptron_fit(X, y01, max_epochs=10000):
    """Perceptron rule from w~ = 0. Returns (w~, number of updates, number of passes)."""
    Xa = np.c_[X, np.ones(len(X))]
    t = 2 * y01 - 1
    w = np.zeros(3)
    updates = 0
    for epoch in range(1, max_epochs + 1):
        changed = 0
        for x, tt in zip(Xa, t):
            if tt * (w @ x) <= 0:
                w = w + tt * x
                updates += 1
                changed += 1
        if changed == 0:
            return w, updates, epoch
    return w, updates, -1


def novikoff_bound(X, y01, wt, bt):
    """(R / gamma)^2 for the true separating line."""
    Xa = np.c_[X, np.ones(len(X))]
    ws = np.r_[wt, bt]
    ws = ws / np.linalg.norm(ws)
    gamma = np.min((2 * y01 - 1) * (Xa @ ws))
    R = np.max(np.linalg.norm(Xa, axis=1))
    return float((R / gamma) ** 2)


# %% [markdown]
# ## Step 2: the sigmoid
# `sigmoid(z) = 1 / (1 + exp(-z))` squeezes any score z into (0, 1), so we can read it as a
# probability. Its slope has a neat form: `s'(z) = s(z) * (1 - s(z))`. The largest slope is
# 0.25, at z = 0.

# %%
def sigmoid(z):
    """Numerically stable sigmoid (no overflow for large |z|)."""
    z = np.asarray(z, dtype=float)
    e = np.exp(-np.abs(z))
    return np.where(z >= 0, 1.0 / (1.0 + e), e / (1.0 + e))


def sigmoid_prime(z):
    s = sigmoid(z)
    return s * (1.0 - s)


# %% [markdown]
# ## Step 3: logistic regression
# Model: `p = sigmoid(w.x + b)`, the probability that the label is 1. Loss (cross-entropy):
# `L = -mean( y log p + (1-y) log(1-p) )`. The key result: the gradient is
# `dL/dw = mean( (p - y) x )` and `dL/db = mean( p - y )`. "Prediction minus truth, times the
# input". Gradient descent: `w = w - lr * dL/dw`, where lr is the learning rate.

# %%
def make_blobs(n, sep, seed):
    """Two overlapping Gaussian clusters (unit spread) with centres `sep` apart on the x1 axis."""
    rng = np.random.default_rng(seed)
    h = n // 2
    X = np.r_[rng.normal([-sep / 2, 0.0], 1.0, (h, 2)), rng.normal([sep / 2, 0.0], 1.0, (n - h, 2))]
    return X, np.r_[np.zeros(h), np.ones(n - h)]


def logreg_loss(w, b, X, y):
    p = np.clip(sigmoid(X @ w + b), 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def logreg_grad(w, b, X, y):
    """Analytic gradient (dL/dw, dL/db)."""
    r = sigmoid(X @ w + b) - y
    return X.T @ r / len(y), float(np.mean(r))


def numeric_grad(w, b, X, y, h=1e-6):
    """Central finite differences (L(w + h) - L(w - h)) / (2h) for every parameter."""
    gw = np.zeros_like(w)
    for i in range(len(w)):
        e = np.zeros_like(w)
        e[i] = h
        gw[i] = (logreg_loss(w + e, b, X, y) - logreg_loss(w - e, b, X, y)) / (2 * h)
    gb = (logreg_loss(w, b + h, X, y) - logreg_loss(w, b - h, X, y)) / (2 * h)
    return gw, gb


def train_logreg(X, y, lr, epochs):
    """Full-batch gradient descent from zero. Returns (w, b, losses) with epochs + 1 losses."""
    w, b = np.zeros(X.shape[1]), 0.0
    losses = [logreg_loss(w, b, X, y)]
    for _ in range(epochs):
        gw, gb = logreg_grad(w, b, X, y)
        w, b = w - lr * gw, b - lr * gb
        losses.append(logreg_loss(w, b, X, y))
    return w, b, losses


def accuracy(w, b, X, y):
    return float(np.mean((X @ w + b > 0) == (y == 1)))


# %% [markdown]
# ## Step 4: the learning rate
# Too small: the loss falls but painfully slowly. Too large: each step overshoots. The
# cleanest demonstration is a single weight with loss `L = w^2`: the step is
# `w <- w - lr * 2w = (1 - 2 lr) w`, so |w| shrinks if lr < 1 and grows if lr > 1.

# %%
def gd_quadratic(lr, steps, w0=1.0):
    """Gradient descent on L = w^2. Returns the list of w values."""
    ws = [w0]
    for _ in range(steps):
        ws.append(ws[-1] - lr * 2 * ws[-1])
    return ws


# a small fixed data set (6 + 6 points, a little overlap) that the live app also uses
APP_X = np.array([[-2, 0.5], [-1.5, -1], [-1, 1.5], [-2.5, -0.5], [-0.5, -0.5], [0.8, 0.3],
                  [2, -0.5], [1.5, 1], [1, -1.5], [2.5, 0.5], [0.5, 0.8], [-0.6, 0.2]], dtype=float)
APP_Y = np.array([0.0] * 6 + [1.0] * 6)


def epochs_to_reach(X, y, lr, target, max_epochs=500):
    """Fewest epochs after which the logistic loss is <= target (None if never within max_epochs)."""
    losses = train_logreg(X, y, lr, max_epochs)[2]
    for k, v in enumerate(losses):
        if v <= target:
            return k
    return None


# %% [markdown]
# ## Step 5: the XOR wall
# XOR: inputs (0,0) and (1,1) have label 0, inputs (0,1) and (1,0) have label 1. We try an
# exhaustive grid of lines `n.x = c` (720 directions, 501 offsets, both sides) and record the
# best number of the 4 points a line gets right.

# %%
XOR_X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
XOR_Y = np.array([0, 1, 1, 0])
AND_Y = np.array([0, 0, 0, 1])


def best_line_score(X, y, n_angles=720, n_offsets=501, c_range=(-2.0, 3.0)):
    """Exhaustive search over lines. Returns (best number correct, how many lines get all correct,
    total lines tried, best (angle, offset))."""
    th = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)
    cs = np.linspace(c_range[0], c_range[1], n_offsets)
    N = np.c_[np.cos(th), np.sin(th)]
    proj = N @ X.T                                        # (angles, points)
    pred = proj[:, None, :] > cs[None, :, None]           # (angles, offsets, points)
    correct = (pred == (y == 1)[None, None, :]).sum(axis=2)
    i, j = np.unravel_index(np.argmax(correct), correct.shape)
    return int(correct.max()), int((correct == len(y)).sum()), int(correct.size), (float(th[i]), float(cs[j]))


# %% [markdown]
# ## Step 6: see it

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    z = np.linspace(-6, 6, 241)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.plot(z, sigmoid(z), label="s(z)")
    ax.plot(z, sigmoid_prime(z), label="s'(z) = s (1 - s)")
    ax.axhline(0.25, color="gray", ls=":")
    ax.set_xlabel("score z (no unit)")
    ax.set_ylabel("value (no unit)")
    ax.set_title("Sigmoid and its slope (maximum slope 0.25 at z = 0)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "sigmoid.png", dpi=120)

    X, y = make_blobs(100, 3.0, 0)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    for lr in (0.01, 0.1, 1.0, 100.0):
        L = train_logreg(X, y, lr, 100)[2]
        ax2.plot(L, label=f"lr = {lr:g}")
        print(f"lr = {lr:g}: loss after 100 epochs = {L[-1]:.3f}")
    ax2.set_xlabel("epoch")
    ax2.set_ylabel("cross-entropy loss (no unit)")
    ax2.set_title("Learning rate: too small is slow, too large is erratic")
    ax2.grid(alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "learning_rates.png", dpi=120)

    best, n_perfect, total, (th, c) = best_line_score(XOR_X, XOR_Y)
    b_and = best_line_score(XOR_X, AND_Y)
    print(f"XOR: best line gets {best} of 4; lines tried {total}; perfect lines {n_perfect}")
    print(f"AND: best line gets {b_and[0]} of 4; perfect lines {b_and[1]}")
    fig3, axs = plt.subplots(1, 2, figsize=(8, 3.8))
    for a, yy, name, res in ((axs[0], XOR_Y, "XOR", (best, n_perfect, total, (th, c))), (axs[1], AND_Y, "AND", b_and)):
        a.scatter(*XOR_X[yy == 1].T, c="tab:blue", s=90, label="label 1")
        a.scatter(*XOR_X[yy == 0].T, c="tab:orange", s=90, label="label 0")
        t, cc = res[3]
        n = np.array([np.cos(t), np.sin(t)])
        p0 = n * cc
        d = np.array([-n[1], n[0]])
        a.plot(*np.c_[p0 - 3 * d, p0 + 3 * d].T, "k--", label="best line found")
        a.set_xlim(-0.5, 1.5)
        a.set_ylim(-0.5, 1.5)
        a.set_xlabel("input x1")
        a.set_ylabel("input x2")
        a.set_title(f"{name}: best line gets {res[0]} of 4")
        a.grid(alpha=0.3)
        a.legend(fontsize=7, loc="upper center")
    fig3.tight_layout()
    fig3.savefig(OUT / "xor_wall.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
