"""Session 4 (Level 3): tune a forest honestly: choose the depth by cross-validation on the training data only.

Run:  python start.py 4
"""
# %% [markdown]
# # Session 4: tune the forest by cross-validation
# **A. Real-world problem.** In Session 3 the forest of depth 12 gave a test accuracy of 0.716, and the
# depth curve showed that a shallow tree does better on new cases. So choose the depth that does best, no?
# Not on the *test* set: if you pick the setting that scores best on the test set, the test set has helped
# build the model, and its score is no longer an honest forecast. Today you choose the depth with k-fold
# cross-validation on the **training data only**, keep the test set locked until the choice is made, add
# random feature subsets at each split, and measure what the choice buys (accuracy) and what it cannot
# promise (the size of the test-set error bar). All data are synthetic.
#
# **Plan.** (1) random feature subsets, (2) a cross-validated grid, (3) two rules for choosing,
# (4) the experiment over 20 training sets, (5) the cost of peeking, (6) when the data are tiny.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 0: the pieces from Session 3, unchanged
# `make_data` (two overlapping classes plus label noise), `grow_tree` (a gini tree), `tree_scores`,
# `accuracy`, the k-fold helpers, and the bagging forest `fit_forest` with its `forest_votes`.

# %%
def make_data(n, seed, sep=4.0, flip=0.1):
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < 0.5).astype(int)
    X = rng.normal(0, 1.0, (n, 2)) + np.outer(y, [sep / 2, sep / 2]) - sep / 4
    flipped = rng.random(n) < flip
    return X, np.where(flipped, 1 - y, y)


def _gini_from(ones, n):
    p = ones / n
    return 1 - p * p - (1 - p) ** 2


def grow_tree(X, y, max_depth):
    n = len(y)
    leaf = {"leaf": True, "p1": float(np.mean(y == 1))}
    if max_depth == 0 or n < 2 or y.min() == y.max():
        return leaf
    best, total = None, int(y.sum())
    for j in range(X.shape[1]):
        o = np.argsort(X[:, j], kind="stable")
        xs, c1 = X[o, j], np.cumsum(y[o])
        for i in range(1, n):
            if xs[i] == xs[i - 1]:
                continue
            g = (i * _gini_from(c1[i - 1], i) + (n - i) * _gini_from(total - c1[i - 1], n - i)) / n
            if best is None or g < best[0] - 1e-12:
                best = (g, j, 0.5 * (xs[i] + xs[i - 1]))
    if best is None:
        return leaf
    _, j, t = best
    m = X[:, j] <= t
    return {"leaf": False, "j": j, "t": float(t),
            "L": grow_tree(X[m], y[m], max_depth - 1), "R": grow_tree(X[~m], y[~m], max_depth - 1)}


def tree_scores(tree, X):
    out = np.empty(len(X))
    for i, row in enumerate(X):
        nd = tree
        while not nd["leaf"]:
            nd = nd["L"] if row[nd["j"]] <= nd["t"] else nd["R"]
        out[i] = nd["p1"]
    return out


def accuracy(y, pred):
    return float(np.mean(np.asarray(y) == np.asarray(pred)))


def fit_forest(X, y, n_trees=25, max_depth=12, seed=0):
    rng = np.random.default_rng(seed)
    trees = []
    for _ in range(n_trees):
        idx = rng.integers(0, len(y), len(y))
        trees.append(grow_tree(X[idx], y[idx], max_depth))
    return trees


def forest_votes(trees, X):
    """Fraction of trees that vote class 1 (a tree votes 1 when its leaf fraction is above 0.5)."""
    return np.mean([tree_scores(t, X) > 0.5 for t in trees], axis=0)


def kfold_indices(n, k, seed=0):
    perm = np.random.default_rng(seed).permutation(n)
    return np.array_split(perm, k)


def cross_val_accuracy(fit_predict, X, y, k=5, seed=0):
    """fit_predict(X_train, y_train, X_test) returns predicted labels."""
    scores = []
    for fold in kfold_indices(len(y), k, seed):
        mask = np.ones(len(y), bool)
        mask[fold] = False
        scores.append(accuracy(y[fold], fit_predict(X[mask], y[mask], X[fold])))
    return float(np.mean(scores)), scores


# %% [markdown]
# ## Step 1: random feature subsets at each split
# A real random forest adds a second source of randomness to bagging: at **each split** a tree looks at
# only a random subset of the features (`max_features`) instead of all of them. Different trees then
# make different mistakes, and their vote cancels more of them. With two features, `max_features = 1`
# means each split picks one feature by a coin flip, and then picks the best threshold on it.

# %%
def grow_tree_rf(X, y, max_depth, rng, max_features=None):
    """Like grow_tree, but each split only looks at max_features features chosen at random."""
    n = len(y)
    leaf = {"leaf": True, "p1": float(np.mean(y == 1))}
    if max_depth == 0 or n < 2 or y.min() == y.max():
        return leaf
    feats = np.arange(X.shape[1]) if max_features is None else rng.permutation(X.shape[1])[:max_features]
    best, total = None, int(y.sum())
    for j in feats:
        o = np.argsort(X[:, j], kind="stable")
        xs, c1 = X[o, j], np.cumsum(y[o])
        for i in range(1, n):
            if xs[i] == xs[i - 1]:
                continue
            g = (i * _gini_from(c1[i - 1], i) + (n - i) * _gini_from(total - c1[i - 1], n - i)) / n
            if best is None or g < best[0] - 1e-12:
                best = (g, int(j), 0.5 * (xs[i] + xs[i - 1]))
    if best is None:
        return leaf
    _, j, t = best
    m = X[:, j] <= t
    return {"leaf": False, "j": j, "t": float(t),
            "L": grow_tree_rf(X[m], y[m], max_depth - 1, rng, max_features),
            "R": grow_tree_rf(X[~m], y[~m], max_depth - 1, rng, max_features)}


def fit_forest_rf(X, y, n_trees=25, max_depth=12, max_features=1, seed=0):
    """Bagging with random feature subsets: a list of trees, voted by forest_votes."""
    rng = np.random.default_rng(seed)
    trees = []
    for _ in range(n_trees):
        idx = rng.integers(0, len(y), len(y))
        trees.append(grow_tree_rf(X[idx], y[idx], max_depth, rng, max_features))
    return trees


# %% [markdown]
# ## Step 2: a cross-validated grid
# We want the depth that will do best on *new* cases. We cannot ask new cases, and we must not ask the
# test set. So we ask **the training data itself, cut into folds**: for each depth, train on k - 1
# folds, test on the fold that was held out, rotate. The k fold scores per depth are the evidence; the
# test set is not touched at all.

# %%
DEPTHS = [1, 2, 3, 4, 6, 8, 12]


def cv_grid(X, y, depths=DEPTHS, n_trees=25, max_features=1, k=5, seed=0):
    """For each depth, the k held-out fold accuracies of a forest (training data only). Returns {depth: [k scores]}."""
    if not 2 <= k <= len(y):
        raise ValueError("k must be between 2 and the number of training cases")

    def make(d):
        return lambda a, b, c: forest_votes(fit_forest_rf(a, b, n_trees, d, max_features, seed), c) > 0.5
    return {d: cross_val_accuracy(make(d), X, y, k, seed)[1] for d in depths}


# %% [markdown]
# ## Step 3: two rules for choosing
# * **best**: the depth with the highest mean fold score; on a tie take the shallower one.
# * **one standard error**: the *shallowest* depth whose mean is within one standard error of the best
#   (SE = standard deviation of the k scores divided by the square root of k). The idea: scores that close
#   cannot be told apart, so prefer the simpler model.

# %%
def choose_depth(cv, rule="best"):
    means = {d: float(np.mean(v)) for d, v in cv.items()}
    best_mean = max(means.values())
    d_best = min(d for d in means if means[d] >= best_mean - 1e-12)      # ties (up to round-off) go to the shallower depth
    if rule == "best":
        return d_best
    if rule == "one_se":
        se = float(np.std(cv[d_best], ddof=1) / math.sqrt(len(cv[d_best])))
        return min(d for d in means if means[d] >= best_mean - se - 1e-12)
    raise ValueError("rule must be 'best' or 'one_se'")


# %% [markdown]
# ## Step 4: the experiment, 20 training sets
# The Session 3 experiment: 20 different training sets of 150 cases, one fixed test set of 500 (15%
# of the labels flipped). For every training set we (a) pick the depth by cross-validation, using the
# training data only, and (b) only then fit the forest at that depth and score it on the test set. To
# compare with other choices we also score every depth on the test set (the table `test`), **but that
# table is never used to choose**, only to look back afterwards. A second, fresh test set B is used in
# Step 5.

# %%
def tuning_table(reps=20, n_train=150, n_test=500, flip=0.15, seed0=100, depths=DEPTHS, n_trees=25, max_features=1, k=5):
    """For each training set: fold scores per depth, and test accuracy per depth on test set A and on a fresh set B."""
    Xa, ya = make_data(n_test, 999, flip=flip)
    Xb, yb = make_data(n_test, 997, flip=flip)
    X_ab = np.vstack([Xa, Xb])
    rows = []
    for r in range(reps):
        X, y = make_data(n_train, seed0 + r, flip=flip)
        cv = cv_grid(X, y, depths, n_trees, max_features, k, seed=r)
        test_a, test_b = {}, {}
        for d in depths:
            v = forest_votes(fit_forest_rf(X, y, n_trees, d, max_features, r), X_ab) > 0.5
            test_a[d], test_b[d] = accuracy(ya, v[:n_test]), accuracy(yb, v[n_test:])
        rows.append({"cv": cv, "test_a": test_a, "test_b": test_b})
    return rows


def shipped_accuracy(reps=20, n_train=150, n_test=500, flip=0.15, seed0=100, test_seed=999):
    """The Session 3 forest (25 trees, depth 12, all features at every split), per training set, on test set A
    (test_seed 999) or on the fresh set B (test_seed 997)."""
    Xte, yte = make_data(n_test, test_seed, flip=flip)
    out = []
    for r in range(reps):
        X, y = make_data(n_train, seed0 + r, flip=flip)
        out.append(accuracy(yte, forest_votes(fit_forest(X, y, 25, 12, seed=r), Xte) > 0.5))
    return np.array(out)


def tuned_accuracy(rows, rule="best"):
    """Per training set: the depth chosen by cross-validation and the test-set-A accuracy at that depth."""
    chosen = [choose_depth(r["cv"], rule) for r in rows]
    return chosen, np.array([r["test_a"][d] for r, d in zip(rows, chosen)])


# %% [markdown]
# ## Step 5: the cost of peeking
# Suppose instead we choose the depth that scores best on test set A, and report that score. That is
# **peeking**: the test set picked the winner, so the winner's score on it is flattered by luck. The
# honest check is a fresh set B that nobody looked at. The gap between the claimed score on A and the
# score on B is the **optimism** of peeking. Cross-validation has a smaller version of the same effect:
# the best fold score is a maximum over several noisy numbers.

# %%
def peeking_report(rows):
    """Mean claimed accuracy (best depth chosen on A, scored on A), honest accuracy of that depth on B, and
    mean of the best cross-validation score; all averaged over the training sets."""
    claimed, honest, cv_best, cv_honest = [], [], [], []
    for r in rows:
        d_peek = max(r["test_a"], key=lambda d: (r["test_a"][d], -d))
        claimed.append(r["test_a"][d_peek])
        honest.append(r["test_b"][d_peek])
        d_cv = choose_depth(r["cv"], "best")
        cv_best.append(float(np.mean(r["cv"][d_cv])))
        cv_honest.append(r["test_b"][d_cv])
    return {"peek_claimed": float(np.mean(claimed)), "peek_honest": float(np.mean(honest)),
            "cv_claimed": float(np.mean(cv_best)), "cv_honest": float(np.mean(cv_honest))}


def honest_report(rows, shipped_a, shipped_b):
    """Everything the mini-project reports, from the tuning table and the shipped forest's accuracies on A and B."""
    ch_b, acc_b = tuned_accuracy(rows, "best")
    ch_s, acc_s = tuned_accuracy(rows, "one_se")
    tuned_b = np.array([r["test_b"][d] for r, d in zip(rows, ch_b)])
    diff = acc_b - shipped_a
    return {"shipped_a": float(np.mean(shipped_a)), "shipped_b": float(np.mean(shipped_b)),
            "tuned_a": float(acc_b.mean()), "tuned_b": float(tuned_b.mean()), "one_se_a": float(acc_s.mean()),
            "chosen": ch_b, "chosen_one_se": ch_s, "wins": int(np.sum(diff > 0)), "reps": len(rows),
            "gain": float(diff.mean()), "gain_se": float(diff.std(ddof=1) / math.sqrt(len(diff))),
            "test_se": binomial_se(float(acc_b.mean()), 500), **peeking_report(rows)}


def binomial_se(p, n):
    """Standard error of an accuracy p measured on n test cases."""
    return math.sqrt(p * (1.0 - p) / n)


# %% [markdown]
# ## Step 6: when the data are tiny
# Cross-validation is only as good as its folds. With 40 training cases each fold has 8 cases; the fold
# scores wobble by a few cases and the chosen depth jumps around. The tuned forest is still no worse than
# the depth-12 forest, but it needs much more luck, and the honest message is a wide error bar.

# %%
def small_data_study(n_train=40, reps=20, seed0=300, depths=DEPTHS, k=5):
    """Chosen depths and test accuracy when only n_train cases are available (test set of 2000)."""
    Xte, yte = make_data(2000, 996, flip=0.15)
    chosen, tuned, deep = [], [], []
    for r in range(reps):
        X, y = make_data(n_train, seed0 + r, flip=0.15)
        d = choose_depth(cv_grid(X, y, depths, 25, 1, k, seed=r), "best")
        chosen.append(d)
        tuned.append(accuracy(yte, forest_votes(fit_forest_rf(X, y, 25, d, 1, r), Xte) > 0.5))
        deep.append(accuracy(yte, forest_votes(fit_forest(X, y, 25, 12, seed=r), Xte) > 0.5))
    return chosen, np.array(tuned), np.array(deep)


# %% [markdown]
# ## See it
# Figure 1: for one training set, the cross-validation score and the test score against depth (the CV
# curve finds the same neighbourhood without the test set). Figure 2: the 20 chosen depths and the
# accuracy of shipped, tuned and peeking choices. Figure 3: the 40-case study.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    BLUE, ORANGE, MAGENTA, GREY = "#0072b2", "#c86a00", "#d81b60", "#555555"
    rows = tuning_table()
    shipped = shipped_accuracy()
    shipped_b = shipped_accuracy(test_seed=997)
    ch_b, acc_b = tuned_accuracy(rows, "best")
    ch_s, acc_s = tuned_accuracy(rows, "one_se")
    print("shipped forest depth 12:", round(shipped.mean(), 4))
    print("tuned, best rule:  mean", round(acc_b.mean(), 4), "chosen depths", ch_b)
    print("tuned, 1-SE rule:  mean", round(acc_s.mean(), 4), "chosen depths", ch_s)
    fixed = {d: float(np.mean([r["test_a"][d] for r in rows])) for d in DEPTHS}
    print("fixed depth, test A:", {d: round(v, 4) for d, v in fixed.items()})
    print("fixed depth, test B:", {d: round(float(np.mean([r["test_b"][d] for r in rows])), 4) for d in DEPTHS})
    rep = peeking_report(rows)
    print("shipped forest on fresh set B:", round(shipped_b.mean(), 4), " tuned (best rule) on B:", round(float(np.mean([r["test_b"][d] for r, d in zip(rows, ch_b)])), 4))
    print("peeking:", {k: round(v, 4) for k, v in rep.items()})
    print("binomial SE of 0.755 on 500 cases:", round(binomial_se(0.755, 500), 4))
    diff = acc_b - shipped
    print("paired difference tuned - shipped: mean", round(diff.mean(), 4), "SE", round(diff.std(ddof=1) / math.sqrt(len(diff)), 4), " better in", int(np.sum(diff > 0)), "of 20")
    ch_small, t_small, d_small = small_data_study()
    print("40 cases: chosen depths", ch_small, " tuned", round(t_small.mean(), 4), "deep", round(d_small.mean(), 4))

    # Figure 1: CV curve and test curve for training set 0 and the mean over sets
    fig1, axs = plt.subplots(1, 2, figsize=(9.6, 4))
    for ax, title, cvm, tem in (
        (axs[0], "one training set", [np.mean(rows[0]["cv"][d]) for d in DEPTHS], [rows[0]["test_a"][d] for d in DEPTHS]),
        (axs[1], "mean of 20 training sets", [np.mean([np.mean(r["cv"][d]) for r in rows]) for d in DEPTHS], [fixed[d] for d in DEPTHS])):
        ax.plot(DEPTHS, cvm, "o-", color=BLUE, label="5-fold cross-validation (training data only)")
        ax.plot(DEPTHS, tem, "s--", color=ORANGE, label="test set (never used to choose)")
        ax.set_xlabel("tree depth"); ax.set_ylabel("accuracy"); ax.set_title(title, fontsize=10); ax.grid(alpha=0.3)
    axs[0].legend(fontsize=8)
    fig1.tight_layout(); fig1.savefig(OUT / "cv_vs_test.png", dpi=120)

    # Figure 2: chosen depths and accuracies
    fig2, axs2 = plt.subplots(1, 2, figsize=(9.6, 4))
    vals, cnts = np.unique(ch_b, return_counts=True)
    axs2[0].bar([str(v) for v in vals], cnts, color=BLUE)
    axs2[0].set_xlabel("depth chosen by cross-validation"); axs2[0].set_ylabel("number of training sets (of 20)")
    axs2[0].set_title("The chosen depth varies with the training set", fontsize=10)
    labels = ["shipped\ndepth 12", "tuned\n(best rule)", "tuned\n(1-SE rule)", "peeking\n(claimed on A)", "peeking\n(honest, on B)"]
    means = [shipped.mean(), acc_b.mean(), acc_s.mean(), rep["peek_claimed"], rep["peek_honest"]]
    cols = [GREY, BLUE, BLUE, MAGENTA, ORANGE]
    axs2[1].bar(range(5), means, color=cols)
    axs2[1].axhline(0.75, color="black", ls=":", lw=1.5)
    axs2[1].set_xticks(range(5)); axs2[1].set_xticklabels(labels, fontsize=8)
    axs2[1].set_ylim(0.65, 0.80); axs2[1].set_ylabel("mean test accuracy"); axs2[1].set_title("Dotted line: the roadmap target 0.75", fontsize=10)
    for i, m in enumerate(means):
        axs2[1].text(i, m + 0.003, f"{m:.3f}", ha="center", fontsize=8)
    fig2.tight_layout(); fig2.savefig(OUT / "chosen_and_accuracy.png", dpi=120)

    # Figure 3: tiny data
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    vals, cnts = np.unique(ch_small, return_counts=True)
    ax3.bar([str(v) for v in vals], cnts, color=BLUE)
    ax3.set_xlabel("depth chosen with only 40 training cases"); ax3.set_ylabel("number of training sets (of 20)")
    ax3.set_title(f"Tiny data: the chosen depth is erratic (tuned {t_small.mean():.3f}, depth 12 {d_small.mean():.3f})", fontsize=9)
    fig3.tight_layout(); fig3.savefig(OUT / "tiny_data.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
