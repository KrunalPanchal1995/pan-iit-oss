"""Session 2 (Level 2): trees, nearest neighbours, the confusion matrix and the base-rate trap.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: measuring a classifier
# **A. Real-world problem.** A screening test says "positive". How likely is it that the
# person really has the condition? A test that is 99% accurate can still be wrong most of the
# time it says positive, if the condition is rare. Today you write two classifiers (a decision
# tree and nearest neighbours), build the confusion matrix, and compute this effect with
# Bayes' rule. (General education only, with made-up numbers: never personal medical advice.)

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: synthetic data with a curved boundary
# Two interleaved half-moons plus noise. A straight line cannot separate them well, so we need
# classifiers with bendy boundaries.

# %%
def make_moons(n_each=100, noise=0.3, seed=0):
    rng = np.random.default_rng(seed)
    t = rng.uniform(0, np.pi, n_each)
    a = np.stack([np.cos(t), np.sin(t)], axis=1)
    t2 = rng.uniform(0, np.pi, n_each)
    b = np.stack([1 - np.cos(t2), 0.5 - np.sin(t2)], axis=1)
    X = np.vstack([a, b]) + rng.normal(0, noise, (2 * n_each, 2))
    y = np.r_[np.zeros(n_each, int), np.ones(n_each, int)]
    return X, y


# %% [markdown]
# ## Step 2: Gini impurity, the "how mixed is this group" number
# For a group where a fraction p1 is class 1 and p0 = 1 - p1 is class 0:
#
#     Gini = 1 - p0^2 - p1^2
#
# A pure group has Gini 0. A 50/50 group has Gini 1 - 0.25 - 0.25 = 0.5, the worst case for
# two classes. A split is good when the weighted Gini of the two halves is small.

# %%
def gini(y):
    y = np.asarray(y)
    if len(y) == 0:
        return 0.0
    p1 = float(np.mean(y == 1))
    return 1.0 - p1 * p1 - (1.0 - p1) ** 2


def best_split(X, y):
    """Search every feature and every midpoint; return (feature, threshold, weighted_gini).
    Returns (None, None, gini(y)) when no split separates anything."""
    X, y = np.asarray(X, float), np.asarray(y)
    n = len(y)
    best = (None, None, gini(y))
    for j in range(X.shape[1]):
        order = np.argsort(X[:, j], kind="stable")
        xs, ys = X[order, j], y[order]
        ones_left = np.cumsum(ys == 1)
        total_ones = ones_left[-1]
        for i in range(1, n):
            if xs[i] == xs[i - 1]:
                continue
            nl, nr = i, n - i
            p_l = ones_left[i - 1] / nl
            p_r = (total_ones - ones_left[i - 1]) / nr
            g = (nl * (1 - p_l ** 2 - (1 - p_l) ** 2) + nr * (1 - p_r ** 2 - (1 - p_r) ** 2)) / n
            if g < best[2] - 1e-12:
                best = (j, 0.5 * (xs[i] + xs[i - 1]), g)
    return best


# %% [markdown]
# ## Step 3: a tree is repeated splitting
# Split the data at the best question, then split each half again, down to `max_depth`.
# A tree of depth 1 is called a *stump*. A leaf predicts the fraction of class 1 inside it
# (a score between 0 and 1); we call it class 1 when that is above 0.5.

# %%
def build_tree(X, y, max_depth):
    X, y = np.asarray(X, float), np.asarray(y)
    if max_depth == 0 or gini(y) == 0.0:
        return {"leaf": True, "p1": float(np.mean(y == 1)), "n": int(len(y))}
    j, t, g = best_split(X, y)
    if j is None:
        return {"leaf": True, "p1": float(np.mean(y == 1)), "n": int(len(y))}
    m = X[:, j] <= t
    return {"leaf": False, "feature": j, "threshold": float(t),
            "left": build_tree(X[m], y[m], max_depth - 1), "right": build_tree(X[~m], y[~m], max_depth - 1)}


def tree_score(node, X):
    """Fraction of class 1 in the leaf each row falls into."""
    X = np.asarray(X, float)
    out = np.empty(len(X))
    for i, row in enumerate(X):
        nd = node
        while not nd["leaf"]:
            nd = nd["left"] if row[nd["feature"]] <= nd["threshold"] else nd["right"]
        out[i] = nd["p1"]
    return out


def tree_predict(node, X):
    return (tree_score(node, X) > 0.5).astype(int)


# %% [markdown]
# ## Step 4: k nearest neighbours
# To classify a new point, look at the k closest training points (straight-line distance)
# and take a majority vote. Small k follows every wiggle; large k smooths the boundary.

# %%
def knn_score(X_train, y_train, X_query, k):
    """Fraction of the k nearest training points that are class 1."""
    X_train, X_query = np.asarray(X_train, float), np.asarray(X_query, float)
    d2 = ((X_query[:, None, :] - X_train[None, :, :]) ** 2).sum(axis=2)
    idx = np.argsort(d2, axis=1, kind="stable")[:, :k]
    return np.asarray(y_train)[idx].mean(axis=1)


def knn_predict(X_train, y_train, X_query, k):
    return (knn_score(X_train, y_train, X_query, k) > 0.5).astype(int)


def grid_predict(predict_fn, xlim=(-1.8, 2.8), ylim=(-1.4, 1.8), n=60):
    gx, gy = np.meshgrid(np.linspace(*xlim, n), np.linspace(*ylim, n))
    pts = np.stack([gx.ravel(), gy.ravel()], axis=1)
    return gx, gy, predict_fn(pts).reshape(n, n)


def roughness(grid):
    """Number of neighbouring grid cells whose predictions differ: a measure of boundary length."""
    return int(np.sum(grid[:, 1:] != grid[:, :-1]) + np.sum(grid[1:, :] != grid[:-1, :]))


# %% [markdown]
# ## Step 5: the confusion matrix and four metrics
#                       predicted 1        predicted 0
#     actually 1        TP (hit)           FN (miss)
#     actually 0        FP (false alarm)   TN (correct rejection)
#
#     accuracy  = (TP + TN) / all            precision = TP / (TP + FP)
#     recall    = TP / (TP + FN)             F1 = 2 * precision * recall / (precision + recall)

# %%
def confusion(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    return tp, fp, fn, tn


def metrics(tp, fp, fn, tn):
    """accuracy, precision, recall, F1. A ratio with a zero denominator is reported as 0."""
    n = tp + fp + fn + tn
    acc = (tp + tn) / n if n else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}


# %% [markdown]
# ## Step 6: the base-rate trap
# Bayes' rule for a test with sensitivity (true-positive rate) and specificity
# (true-negative rate) on a population with prevalence q:
#
#     PPV = q * sens / ( q * sens + (1 - q) * (1 - spec) )
#
# PPV (positive predictive value) is the chance that a positive result is a true case.

# %%
def ppv(prevalence, sensitivity, specificity):
    tp = prevalence * sensitivity
    fp = (1 - prevalence) * (1 - specificity)
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0


# %% [markdown]
# ## Step 7: choosing a threshold when the two mistakes cost different amounts
# Score each case between 0 and 1 and call it positive when score >= threshold.
# Total cost = c_fn * (misses) + c_fp * (false alarms). Try every threshold, keep the cheapest.
# Hand rule: if the score were the true probability p, predicting positive is cheaper when
# (1 - p) * c_fp < p * c_fn, i.e. when p > c_fp / (c_fp + c_fn).

# %%
def total_cost(y_true, scores, threshold, c_fn, c_fp):
    pred = (np.asarray(scores) >= threshold).astype(int)
    tp, fp, fn, tn = confusion(y_true, pred)
    return c_fn * fn + c_fp * fp


def bayes_threshold(c_fn, c_fp):
    """If scores are true probabilities, call positive when the score exceeds this value."""
    return c_fp / (c_fp + c_fn)


def best_threshold(y_true, scores, c_fn, c_fp):
    """Try each distinct score (and one above the top) as a threshold; return (threshold, cost).
    Ties go to the larger threshold."""
    cands = np.unique(np.r_[np.asarray(scores, float), np.max(scores) + 1.0])
    costs = [total_cost(y_true, scores, t, c_fn, c_fp) for t in cands]
    i = len(cands) - 1 - int(np.argmin(costs[::-1]))
    return float(cands[i]), float(costs[i])


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    Xtr, ytr = make_moons(100, 0.3, seed=0)
    Xte, yte = make_moons(100, 0.3, seed=1)
    print("gini 50/50:", gini([0, 0, 1, 1]), " gini 3:1:", gini([0, 0, 0, 1]))
    print("best split of 1..4:", best_split(np.array([[1.0], [2.0], [3.0], [4.0]]), np.array([0, 0, 1, 1])))

    T1, T3 = build_tree(Xtr, ytr, 1), build_tree(Xtr, ytr, 3)
    models = {
        "stump (depth 1)": lambda P: tree_predict(T1, P),
        "tree depth 3": lambda P: tree_predict(T3, P),
        "kNN k = 1": lambda P: knn_predict(Xtr, ytr, P, 1),
        "kNN k = 15": lambda P: knn_predict(Xtr, ytr, P, 15),
    }
    fig, axs = plt.subplots(2, 2, figsize=(8, 7), sharex=True, sharey=True)
    for ax, (name, fn) in zip(axs.ravel(), models.items()):
        gx, gy, g = grid_predict(fn)
        ax.contourf(gx, gy, g, levels=[-0.5, 0.5, 1.5], colors=["#cfe8cf", "#f4cccc"])
        ax.scatter(*Xtr[ytr == 0].T, c="tab:green", s=10)
        ax.scatter(*Xtr[ytr == 1].T, c="tab:red", s=10)
        acc = metrics(*confusion(yte, fn(Xte)))["accuracy"]
        ax.set_title(f"{name}: test accuracy {acc:.3f}\nboundary roughness {roughness(g)}", fontsize=9)
        print(f"{name:16s} test accuracy {acc:.3f}  roughness {roughness(g)}")
    for ax in axs[1]:
        ax.set_xlabel("feature 1 (units)")
    for ax in axs[:, 0]:
        ax.set_ylabel("feature 2 (units)")
    fig.tight_layout(); fig.savefig(OUT / "boundaries.png", dpi=120)

    tp, fp, fn_, tn = 40, 10, 20, 130
    m = metrics(tp, fp, fn_, tn)
    print("hand example", {k: round(v, 4) for k, v in m.items()})
    fig2, ax2 = plt.subplots(figsize=(4.5, 4))
    cm = np.array([[tp, fn_], [fp, tn]])
    ax2.imshow(cm, cmap="Blues")
    for (i, j), v in np.ndenumerate(cm):
        ax2.text(j, i, f"{['TP', 'FN', 'FP', 'TN'][2 * i + j]}\n{v}", ha="center", va="center", fontsize=12)
    ax2.set_xticks([0, 1], ["predicted 1", "predicted 0"]); ax2.set_yticks([0, 1], ["actually 1", "actually 0"])
    ax2.set_title("Confusion matrix (hand example, 200 cases)")
    fig2.tight_layout(); fig2.savefig(OUT / "confusion_matrix.png", dpi=120)

    print("PPV 1%, 99%, 95%:", round(ppv(0.01, 0.99, 0.95), 4))
    q = np.linspace(0.001, 0.5, 200)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    for sp in (0.90, 0.95, 0.99):
        ax3.plot(100 * q, [100 * ppv(v, 0.99, sp) for v in q], label=f"specificity {sp:.0%}")
    ax3.axvline(1, color="gray", ls=":")
    ax3.set_xlabel("prevalence (% of people who have the condition)")
    ax3.set_ylabel("positive predictive value (%)")
    ax3.set_title("A positive result means little when the condition is rare")
    ax3.legend(); ax3.grid(alpha=0.3)
    fig3.tight_layout(); fig3.savefig(OUT / "base_rate.png", dpi=120)

    # threshold design: choose on a validation set (seed 2), then report the cost on the test set (seed 1)
    Xva, yva = make_moons(100, 0.3, seed=2)
    sv, st = knn_score(Xtr, ytr, Xva, 15), knn_score(Xtr, ytr, Xte, 15)
    for c_fn in (1, 10):
        t, c = best_threshold(yva, sv, c_fn, 1)
        print(f"cost of a miss {c_fn}: threshold {t:.3f} chosen on validation; test cost {total_cost(yte, st, t, c_fn, 1):.0f}, test cost at 0.5: {total_cost(yte, st, 0.5, c_fn, 1):.0f}")
