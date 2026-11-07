"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # worked example: choosing by hand
    cvh = {1: [0.70, 0.74, 0.72, 0.70, 0.74], 2: [0.80, 0.78, 0.78, 0.78, 0.78], 3: [0.82, 0.76, 0.80, 0.78, 0.79], 4: [0.77, 0.75, 0.74, 0.76, 0.73]}
    means = {d: float(np.mean(v)) for d, v in cvh.items()}
    se3 = float(np.std(cvh[3], ddof=1) / math.sqrt(5))
    checks.append((f"worked example (Section E): fold means 0.72, 0.784, 0.79, 0.75; the best rule picks depth {L.choose_depth(cvh)}, and with SE = {se3:.3f} the one-SE rule picks depth {L.choose_depth(cvh, 'one_se')}",
                   abs(means[2] - 0.784) < 1e-12 and abs(means[3] - 0.79) < 1e-12 and abs(se3 - 0.01) < 1e-12 and L.choose_depth(cvh) == 3 and L.choose_depth(cvh, "one_se") == 2))
    tie = {1: [0.7, 0.7], 2: [0.8, 0.8], 3: [0.8, 0.8], 4: [0.6, 0.6]}
    try:
        L.choose_depth(tie, "median")
        bad_rule = False
    except ValueError:
        bad_rule = True
    checks.append(("a tie in the mean score goes to the shallower depth, and an unknown rule is refused", L.choose_depth(tie) == 2 and bad_rule))

    # pieces
    X, y = L.make_data(150, 100, flip=0.15)
    Xt, _ = L.make_data(300, 5, flip=0.15)
    same = np.abs(L.tree_scores(L.grow_tree(X, y, 6), Xt) - L.tree_scores(L.grow_tree_rf(X, y, 6, np.random.default_rng(0), None), Xt)).max()
    roots = {L.grow_tree_rf(X, y, 1, np.random.default_rng(s), 1)["j"] for s in range(20)}
    checks.append(("random feature subsets: with all features the tree equals the Session 3 tree; with one feature per split the root feature varies from tree to tree (both 0 and 1 occur)",
                   same == 0.0 and roots == {0, 1}))
    cv = L.cv_grid(X, y)
    checks.append((f"the grid has one list of 5 fold scores for each of the depths {L.DEPTHS}; every case is tested once (folds cover 150 cases)",
                   list(cv) == L.DEPTHS and all(len(v) == 5 for v in cv.values()) and sum(len(f) for f in L.kfold_indices(150, 5, 0)) == 150))
    errs = 0
    for k in (1, 151):
        try:
            L.cv_grid(X, y, k=k)
        except ValueError:
            errs += 1
    checks.append(("failure: k = 1 and k larger than the number of cases are refused", errs == 2))
    r3a = L.tuning_table(reps=3, n_test=100)
    r3b = L.tuning_table(reps=3, n_test=500)
    checks.append(("the chosen depths depend on the training data only: a test set of 100 or of 500 cases gives the same choices",
                   [L.choose_depth(r["cv"]) for r in r3a] == [L.choose_depth(r["cv"]) for r in r3b]))

    # the experiment
    rows = L.tuning_table()
    sa, sb = L.shipped_accuracy(), L.shipped_accuracy(test_seed=997)
    rep = L.honest_report(rows, sa, sb)
    checks.append((f"the shipped Session 3 forest (depth 12) gives {rep['shipped_a']:.3f} on test set A, as in Session 3 (0.716)", abs(rep["shipped_a"] - 0.716) < 0.0015))
    checks.append((f"roadmap test: the forest with the depth chosen by 5-fold cross-validation gives mean test accuracy {rep['tuned_a']:.3f} over the 20 training sets (needed: at least 0.75)",
                   rep["tuned_a"] >= 0.75 and abs(rep["tuned_a"] - 0.767) < 0.0015))
    checks.append((f"it beats the shipped forest on {rep['wins']} of 20 training sets; mean gain {rep['gain']:.3f} with a standard error of {rep['gain_se']:.3f}",
                   rep["wins"] >= 18 and rep["gain"] > 4 * rep["gain_se"]))
    ch = rep["chosen"]
    checks.append((f"the chosen depths are shallow and vary with the training set: all between 1 and 4, mean {np.mean(ch):.2f}, {len(set(ch))} different values, never 12",
                   max(ch) <= 6 and min(ch) >= 1 and 12 not in ch and len(set(ch)) >= 3 and 2.0 < np.mean(ch) < 3.2))
    checks.append((f"the one-SE rule picks the same or a shallower depth than the best rule on every set, and still gives {rep['one_se_a']:.3f}",
                   all(a <= b for a, b in zip(rep["chosen_one_se"], ch)) and rep["one_se_a"] >= 0.75))
    checks.append((f"on a fresh test set B the gain holds: tuned {rep['tuned_b']:.3f} against shipped {rep['shipped_b']:.3f}, but every number is lower than on A (set A was an easy draw)",
                   rep["tuned_b"] - rep["shipped_b"] > 0.03 and rep["tuned_b"] < rep["tuned_a"] and rep["shipped_b"] < rep["shipped_a"] and rep["tuned_b"] < 0.75))
    checks.append((f"peeking: choosing the depth on test set A and reporting A's score claims {rep['peek_claimed']:.3f}, but a fresh set gives {rep['peek_honest']:.3f} (optimism at least 0.02)",
                   rep["peek_claimed"] - rep["peek_honest"] > 0.02))
    checks.append((f"the best cross-validation score is optimistic too: mean {rep['cv_claimed']:.3f} against {rep['cv_honest']:.3f} on set B (the maximum of 7 noisy scores)",
                   rep["cv_claimed"] - rep["cv_honest"] > 0.03))
    se = L.binomial_se(rep["tuned_a"], 500)
    checks.append((f"error bar: an accuracy of {rep['tuned_a']:.3f} measured on 500 cases has a standard error of {se:.3f}, larger than its margin of {rep['tuned_a'] - 0.75:.3f} over the target; the paired gain over the shipped forest is far more certain",
                   abs(se - 0.0189) < 0.0005 and se > rep["tuned_a"] - 0.75))

    # failure: tiny data
    chosen, tuned, deep = L.small_data_study()
    checks.append((f"failure: with only 40 training cases the chosen depth is erratic ({len(set(chosen))} different values over 20 sets, from {min(chosen)} to {max(chosen)}); tuned still beats depth 12: {tuned.mean():.3f} against {deep.mean():.3f}",
                   len(set(chosen)) >= 4 and tuned.mean() - deep.mean() > 0.03 and abs(tuned.mean() - 0.7498) < 0.003))
    return checks
# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
