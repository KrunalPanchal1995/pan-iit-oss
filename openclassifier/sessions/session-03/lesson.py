"""Session 3 (Level 3): judge a classifier honestly: ROC and AUC, forests, overfitting, cross-validation, fairness, leakage.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: judging a classifier honestly
# **A. Real-world problem.** A model that looks perfect on the data it was built from can fail on
# new cases, can treat two groups of people unequally, and can look brilliant because of a
# bookkeeping mistake. Today you build the standard tools for honest judging: the ROC curve and
# AUC, a random forest, a train/test comparison across tree depth, k-fold cross-validation, a
# group comparison, and a demonstration of data leakage. All data are synthetic, and nothing
# here says anything about real people.

# %%
import math
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: ROC curve and AUC from scores
# A model gives each case a score. Lower the threshold and you catch more true cases (true-positive
# rate, TPR = TP / (TP + FN)) but raise more false alarms (false-positive rate,
# FPR = FP / (FP + TN)). The ROC curve plots TPR against FPR over all thresholds. The area under
# it (AUC) has a second meaning: **the probability that a random positive case outranks a random
# negative case** (ties count one half). We compute AUC both ways and they must agree.

# %%
def roc_curve(scores, y):
    """Return fpr, tpr, thresholds, one point per distinct score, starting at (0, 0)."""
    scores, y = np.asarray(scores, float), np.asarray(y)
    order = np.argsort(-scores, kind="stable")
    s, yy = scores[order], y[order]
    tps, fps = np.cumsum(yy == 1), np.cumsum(yy == 0)
    keep = np.r_[np.where(np.diff(s) != 0)[0], len(s) - 1]
    n_pos, n_neg = tps[-1], fps[-1]
    fpr = np.r_[0.0, fps[keep] / n_neg]
    tpr = np.r_[0.0, tps[keep] / n_pos]
    return fpr, tpr, np.r_[s[0] + 1.0, s[keep]]


def auc_trapezoid(fpr, tpr):
    return float(np.sum(np.diff(fpr) * (tpr[1:] + tpr[:-1]) / 2.0))


def auc_pairs(scores, y):
    """Probability that a random positive scores above a random negative (ties = 1/2)."""
    scores, y = np.asarray(scores, float), np.asarray(y)
    pos, neg = scores[y == 1], scores[y == 0]
    diff = pos[:, None] - neg[None, :]
    return float((np.sum(diff > 0) + 0.5 * np.sum(diff == 0)) / diff.size)


def precision_recall_points(scores, y):
    """Precision and recall at every distinct threshold (call positive when score >= threshold)."""
    scores, y = np.asarray(scores, float), np.asarray(y)
    thr = np.unique(scores)[::-1]
    prec, rec = [], []
    for t in thr:
        pred = scores >= t
        tp = np.sum(pred & (y == 1))
        prec.append(tp / pred.sum())
        rec.append(tp / np.sum(y == 1))
    return np.array(prec), np.array(rec), thr


# %% [markdown]
# ## Step 2: data and a decision tree (as in Session 2, written compactly)
# `make_data` has two overlapping classes in 2D plus a fraction `flip` of labels flipped at random
# (real labels are never perfect).

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


# %% [markdown]
# ## Step 3: a random forest is bagging
# Draw a **bootstrap sample** (n cases drawn with replacement) and grow a full tree on it; repeat
# `n_trees` times; classify by majority vote. Each tree is unstable (it changes a lot if the
# training set changes), but the vote averages the wobble away, so the forest's test accuracy
# varies less from one training set to the next. (Real random forests also pick random feature
# subsets at each split; this simple bagging shows the main effect.)

# %%
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


def single_vs_forest(reps=20, n_train=150, n_test=500, flip=0.15, seed0=100):
    """Over `reps` different training sets: test accuracy of one full tree and of a 25-tree forest,
    and how much each test point's predicted label wobbles from one training set to the next."""
    Xte, yte = make_data(n_test, 999, flip=flip)
    single, forest, ps, pf = [], [], [], []
    for r in range(reps):
        X, y = make_data(n_train, seed0 + r, flip=flip)
        a = tree_scores(grow_tree(X, y, 12), Xte) > 0.5
        b = forest_votes(fit_forest(X, y, 25, 12, seed=r), Xte) > 0.5
        single.append(accuracy(yte, a)); forest.append(accuracy(yte, b))
        ps.append(a); pf.append(b)
    wobble_s = float(np.mean(np.var(np.array(ps, float), axis=0)))
    wobble_f = float(np.mean(np.var(np.array(pf, float), axis=0)))
    return np.array(single), np.array(forest), wobble_s, wobble_f


# %% [markdown]
# ## Step 4: overfitting with depth
# A deeper tree can memorise the training set (training accuracy reaches 100%), but memorised
# noise does not help on new data. We measure both.

# %%
def depth_curve(depths, n_train=150, n_test=2000, flip=0.2, seed=5):
    X, y = make_data(n_train, seed, flip=flip)
    Xte, yte = make_data(n_test, 998, flip=flip)
    tr, te = [], []
    for d in depths:
        t = grow_tree(X, y, d)
        tr.append(accuracy(y, tree_scores(t, X) > 0.5))
        te.append(accuracy(yte, tree_scores(t, Xte) > 0.5))
    return np.array(tr), np.array(te)


# %% [markdown]
# ## Step 5: k-fold cross-validation
# Shuffle the case numbers, cut them into k folds; for each fold, train on the other k - 1
# folds and test on that fold. Every case is tested exactly once. The mean of the k scores is a
# better estimate of future accuracy than one lucky split.

# %%
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
# ## Step 6: calibration (stretch)
# A score is *calibrated* if, among cases scored about 0.7, about 70% are positive. Group the
# scores into bins and compare the mean score with the fraction of positives in each bin.

# %%
def reliability(p, y, bins=5):
    p, y = np.asarray(p, float), np.asarray(y)
    edges = np.linspace(0, 1, bins + 1)
    ids = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    mean_p, frac, cnt = [], [], []
    for b in range(bins):
        m = ids == b
        cnt.append(int(m.sum()))
        mean_p.append(float(p[m].mean()) if m.any() else np.nan)
        frac.append(float(y[m].mean()) if m.any() else np.nan)
    return np.array(mean_p), np.array(frac), np.array(cnt)


def expected_calibration_error(p, y, bins=5):
    mean_p, frac, cnt = reliability(p, y, bins)
    ok = cnt > 0
    return float(np.sum(cnt[ok] * np.abs(mean_p[ok] - frac[ok])) / cnt.sum())


# %% [markdown]
# ## Step 7: fairness as unequal error rates (education only)
# Two synthetic groups get the same kind of score: negatives centred at 0, positives centred at d,
# spread 1. Group B's scores are all shifted up by `shift` (a biased measuring instrument). One
# single threshold t then gives different false-positive rates. With the standard normal CDF Phi:
#
#     FPR_A = 1 - Phi(t),   FPR_B = 1 - Phi(t - shift),   TPR_g = 1 - Phi(t - shift_g - d)
#
# Notice AUC is the same for both groups: a shift does not change ranking within a group.

# %%
def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def group_rates_analytic(t, shift, d=1.5):
    return {"fpr_A": 1 - phi(t), "tpr_A": 1 - phi(t - d),
            "fpr_B": 1 - phi(t - shift), "tpr_B": 1 - phi(t - shift - d)}


def simulate_group(n, shift, d=1.5, seed=0):
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < 0.3).astype(int)
    return rng.normal(d * y + shift, 1.0), y


def empirical_rates(scores, y, t):
    pred = scores >= t
    return float(np.mean(pred[y == 0])), float(np.mean(pred[y == 1]))


# %% [markdown]
# ## Step 8: failure cases
# **Leakage.** Pick the "best" features using all the data, then cross-validate, and you test on
# cases that already helped choose the features. With pure noise features, accuracy looks well
# above 50%. The honest way picks features inside each training fold only.
# **Class imbalance.** With 1% positives, "always say negative" is 99% accurate and useless.

# %%
def make_noise(n=60, d=500, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, d)), (np.arange(n) % 2).astype(int)


def top_features(X, y, m):
    """Indices of the m features with the largest |correlation| with the label."""
    Xc, yc = X - X.mean(axis=0), y - y.mean()
    corr = (Xc * yc[:, None]).sum(axis=0) / (np.sqrt((Xc ** 2).sum(axis=0) * (yc ** 2).sum()) + 1e-12)
    return np.argsort(-np.abs(corr))[:m]


def centroid_predict(Xtr, ytr, Xte):
    c0, c1 = Xtr[ytr == 0].mean(axis=0), Xtr[ytr == 1].mean(axis=0)
    return (((Xte - c1) ** 2).sum(axis=1) < ((Xte - c0) ** 2).sum(axis=1)).astype(int)


def leaky_cv(X, y, m=10, k=5, seed=0):
    cols = top_features(X, y, m)                       # uses ALL cases, including future test folds
    return cross_val_accuracy(lambda a, b, c: centroid_predict(a[:, cols], b, c[:, cols]), X, y, k, seed)[0]


def honest_cv(X, y, m=10, k=5, seed=0):
    def fp(a, b, c):
        cols = top_features(a, b, m)                   # uses the training fold only
        return centroid_predict(a[:, cols], b, c[:, cols])
    return cross_val_accuracy(fp, X, y, k, seed)[0]


def imbalance_demo(n=1000, prevalence=0.01):
    n_pos = int(round(n * prevalence))
    y = np.r_[np.ones(n_pos, int), np.zeros(n - n_pos, int)]
    pred = np.zeros(n, int)
    tp = int(np.sum((pred == 1) & (y == 1)))
    return accuracy(y, pred), tp / n_pos


# %% [markdown]
# ## Step 9: mini-project helper, a synthetic screening problem
# 5% of 3000 synthetic cases are positive. Four features; positives are shifted by 1.0 in each.
# A miss costs 20 and a false alarm costs 1 (made-up units). Choose a model and a threshold on a
# validation set, then report the confusion matrix and the cost on a separate test set.

# %%
def make_screening(n, seed, prevalence=0.05, shift=1.0):
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < prevalence).astype(int)
    return rng.normal(0, 1, (n, 4)) + shift * y[:, None], y


def cost_and_confusion(y, scores, t, c_fn=20, c_fp=1):
    pred = scores >= t
    tp, fp = int(np.sum(pred & (y == 1))), int(np.sum(pred & (y == 0)))
    fn, tn = int(np.sum(~pred & (y == 1))), int(np.sum(~pred & (y == 0)))
    return c_fn * fn + c_fp * fp, (tp, fp, fn, tn)


def pick_threshold(y, scores, c_fn=20, c_fp=1):
    cands = np.unique(scores)
    costs = [cost_and_confusion(y, scores, t, c_fn, c_fp)[0] for t in cands]
    return float(cands[int(np.argmin(costs))]), float(min(costs))


def screening_study(seed=7):
    Xtr, ytr = make_screening(1500, seed)
    Xva, yva = make_screening(1500, seed + 1)
    Xte, yte = make_screening(3000, seed + 2)
    out = {}
    for name, fit in [("tree depth 3", lambda: (lambda X: tree_scores(grow_tree(Xtr, ytr, 3), X))),
                      ("tree depth 8", lambda: (lambda X: tree_scores(grow_tree(Xtr, ytr, 8), X))),
                      ("forest 25 x depth 6", lambda: (lambda X, f=fit_forest(Xtr, ytr, 25, 6, seed): forest_votes(f, X)))]:
        scorer = fit()
        t, vcost = pick_threshold(yva, scorer(Xva))
        tcost, cm = cost_and_confusion(yte, scorer(Xte), t)
        out[name] = {"threshold": t, "val_cost": vcost, "test_cost": tcost, "confusion": cm}
    return out


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    # 1. ROC and AUC
    s_hand, y_hand = np.array([0.1, 0.4, 0.35, 0.8]), np.array([0, 0, 1, 1])
    print("hand AUC", auc_trapezoid(*roc_curve(s_hand, y_hand)[:2]), auc_pairs(s_hand, y_hand))
    Xa, ya = make_data(400, 3, flip=0.1)
    Xb, yb = make_data(400, 4, flip=0.1)
    sc = forest_votes(fit_forest(Xa, ya, 25, 5, 1), Xb) + 0.001 * tree_scores(grow_tree(Xa, ya, 3), Xb)
    fpr, tpr, thr = roc_curve(sc, yb)
    print("AUC trapezoid", round(auc_trapezoid(fpr, tpr), 4), " AUC pairs", round(auc_pairs(sc, yb), 4))
    prec, rec, _ = precision_recall_points(sc, yb)
    fig, axs = plt.subplots(1, 2, figsize=(9, 4))
    axs[0].plot(fpr, tpr, label=f"AUC {auc_trapezoid(fpr, tpr):.3f}"); axs[0].plot([0, 1], [0, 1], "k:", label="coin flip")
    axs[0].set_xlabel("false-positive rate"); axs[0].set_ylabel("true-positive rate"); axs[0].set_title("ROC curve")
    axs[1].plot(rec, prec); axs[1].set_xlabel("recall"); axs[1].set_ylabel("precision"); axs[1].set_title("Precision-recall trade-off")
    for a in axs:
        a.grid(alpha=0.3)
    axs[0].legend(); fig.tight_layout(); fig.savefig(OUT / "roc_pr.png", dpi=120)

    # 2. forest versus single tree
    single, forest, wob_s, wob_f = single_vs_forest()
    print(f"label wobble single {wob_s:.3f} forest {wob_f:.3f}")
    print(f"single tree: mean {single.mean():.3f} std {single.std():.3f} | forest: mean {forest.mean():.3f} std {forest.std():.3f}")

    # 3. overfitting
    depths = list(range(1, 21))
    tr, te = depth_curve(depths)
    print("train", np.round(tr, 3))
    print("test ", np.round(te, 3))
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(depths, tr, "o-", label="training accuracy"); ax2.plot(depths, te, "s-", label="test accuracy")
    ax2.set_xlabel("tree depth"); ax2.set_ylabel("accuracy"); ax2.set_title("Deeper trees memorise the training set")
    ax2.legend(); ax2.grid(alpha=0.3); fig2.tight_layout(); fig2.savefig(OUT / "overfit_depth.png", dpi=120)

    # 4. cross-validation
    Xc, yc = make_data(200, 11, flip=0.15)
    cv, folds = cross_val_accuracy(lambda a, b, c: tree_scores(grow_tree(a, b, 3), c) > 0.5, Xc, yc, 5)
    print("5-fold CV depth 3:", round(cv, 3), np.round(folds, 3))

    # 5. calibration
    rng = np.random.default_rng(2)
    p_true = rng.uniform(0, 1, 4000)
    y_cal = (rng.random(4000) < p_true).astype(int)
    p_over = np.clip(0.5 + 1.8 * (p_true - 0.5), 0.001, 0.999)
    print("ECE calibrated", round(expected_calibration_error(p_true, y_cal), 3), " over-confident", round(expected_calibration_error(p_over, y_cal), 3))
    fig3, ax3 = plt.subplots(figsize=(4.5, 4.5))
    for p, nm in [(p_true, "calibrated"), (p_over, "over-confident")]:
        mp, fr, _ = reliability(p, y_cal, 10)
        ax3.plot(mp, fr, "o-", label=nm)
    ax3.plot([0, 1], [0, 1], "k:"); ax3.set_xlabel("mean predicted score"); ax3.set_ylabel("fraction actually positive")
    ax3.set_title("Reliability diagram"); ax3.legend(); ax3.grid(alpha=0.3); fig3.tight_layout(); fig3.savefig(OUT / "reliability.png", dpi=120)

    # 6. fairness
    sa, ya_ = simulate_group(20000, 0.0, seed=1)
    sb, yb_ = simulate_group(20000, 0.5, seed=2)
    t = 1.0
    print("analytic", {k: round(v, 4) for k, v in group_rates_analytic(t, 0.5).items()})
    print("empirical A", np.round(empirical_rates(sa, ya_, t), 4), " B", np.round(empirical_rates(sb, yb_, t), 4))
    print("AUC A", round(auc_pairs(sa[:3000], ya_[:3000]), 3), " AUC B", round(auc_pairs(sb[:3000], yb_[:3000]), 3), " theory", round(phi(1.5 / math.sqrt(2)), 3))
    ts = np.linspace(-1.5, 3.5, 100)
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    ax4.plot(ts, [1 - phi(x) for x in ts], label="group A false-positive rate")
    ax4.plot(ts, [1 - phi(x - 0.5) for x in ts], label="group B false-positive rate")
    ax4.axvline(t, color="gray", ls=":")
    ax4.set_xlabel("single threshold on the score"); ax4.set_ylabel("false-positive rate")
    ax4.set_title("One threshold, unequal false-positive rates"); ax4.legend(); ax4.grid(alpha=0.3)
    fig4.tight_layout(); fig4.savefig(OUT / "fairness.png", dpi=120)

    # 7. failure cases
    leaks, honests = [], []
    for sd in range(10):
        Xn, yn = make_noise(60, 500, sd)
        leaks.append(leaky_cv(Xn, yn)); honests.append(honest_cv(Xn, yn))
    print(f"leaky CV mean {np.mean(leaks):.3f}   honest CV mean {np.mean(honests):.3f}   (pure noise, true accuracy 0.5)")
    print("imbalance: accuracy, recall of always-negative:", imbalance_demo())

    # 8. screening
    for k, v in screening_study().items():
        print(k, v)
