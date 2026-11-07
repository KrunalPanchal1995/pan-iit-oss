"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # Gini on hand-checkable cases
    checks.append(("Gini of a 50/50 node is 0.5", abs(L.gini([0, 0, 1, 1]) - 0.5) < 1e-12))
    checks.append(("Gini of a pure node is 0", L.gini([1, 1, 1]) == 0.0 and L.gini([0, 0]) == 0.0))
    checks.append(("Gini of a 3:1 node is 0.375", abs(L.gini([0, 0, 0, 1]) - 0.375) < 1e-12))
    checks.append(("Gini of an empty node is 0 (edge case)", L.gini([]) == 0.0))

    # best split on 1..4 with labels 0,0,1,1: threshold 2.5, weighted Gini 0
    j, t, g = L.best_split(np.array([[1.0], [2.0], [3.0], [4.0]]), np.array([0, 0, 1, 1]))
    checks.append(("best split of [1,2,3,4] with labels [0,0,1,1] is at 2.5 with Gini 0", j == 0 and abs(t - 2.5) < 1e-12 and abs(g) < 1e-12))
    j2, t2, g2 = L.best_split(np.array([[1.0], [1.0], [1.0], [1.0]]), np.array([0, 0, 1, 1]))
    checks.append(("no split exists when all values are equal", j2 is None and abs(g2 - 0.5) < 1e-12))
    # weighted Gini by hand: split [0,0,1 | 1] gives (3 * 4/9 + 1 * 0) / 4 = 1/3
    Xh, yh = np.array([[1.0], [2.0], [3.0], [4.0]]), np.array([0, 0, 1, 1])
    m = Xh[:, 0] <= 3.5
    wg = (m.sum() * L.gini(yh[m]) + (~m).sum() * L.gini(yh[~m])) / 4
    checks.append(("weighted Gini of the split [0,0,1 | 1] is 1/3 (hand calculation)", abs(wg - 1 / 3) < 1e-12))

    # trees and kNN on seeded moons
    Xtr, ytr = L.make_moons(100, 0.3, seed=0)
    Xte, yte = L.make_moons(100, 0.3, seed=1)
    T1, T3 = L.build_tree(Xtr, ytr, 1), L.build_tree(Xtr, ytr, 3)
    acc = lambda pred: L.metrics(*L.confusion(yte, pred))["accuracy"]
    a_stump, a_tree = acc(L.tree_predict(T1, Xte)), acc(L.tree_predict(T3, Xte))
    a_k1, a_k15 = acc(L.knn_predict(Xtr, ytr, Xte, 1)), acc(L.knn_predict(Xtr, ytr, Xte, 15))
    checks.append((f"test accuracy: stump 0.745, depth-3 tree 0.865 (got {a_stump:.3f}, {a_tree:.3f})", abs(a_stump - 0.745) < 1e-9 and abs(a_tree - 0.865) < 1e-9))
    checks.append((f"test accuracy: kNN k=1 0.830, k=15 0.910 (got {a_k1:.3f}, {a_k15:.3f})", abs(a_k1 - 0.83) < 1e-9 and abs(a_k15 - 0.91) < 1e-9))
    checks.append(("a deeper tree beats the stump on this curved data", a_tree > a_stump))
    checks.append(("a depth-0 tree is a single leaf holding the class fraction", L.build_tree(Xtr, ytr, 0)["leaf"] and abs(L.build_tree(Xtr, ytr, 0)["p1"] - 0.5) < 1e-12))
    checks.append(("a stump has exactly two leaves", (not T1["leaf"]) and T1["left"]["leaf"] and T1["right"]["leaf"]))
    # kNN by hand: query 0.1 with training 0,0.2 (class 0) and 1 (class 1), k=1 -> class 0; k=3 -> 1/3 -> class 0
    Xk, yk = np.array([[0.0, 0], [0.2, 0], [1.0, 0]]), np.array([0, 0, 1])
    checks.append(("kNN by hand: k=1 and k=3 both call the point 0.1 class 0", int(L.knn_predict(Xk, yk, np.array([[0.1, 0]]), 1)[0]) == 0 and abs(L.knn_score(Xk, yk, np.array([[0.1, 0]]), 3)[0] - 1 / 3) < 1e-12))
    r1 = L.roughness(L.grid_predict(lambda P: L.knn_predict(Xtr, ytr, P, 1))[2])
    r15 = L.roughness(L.grid_predict(lambda P: L.knn_predict(Xtr, ytr, P, 15))[2])
    checks.append((f"the boundary is smoother for k=15 (roughness {r15}) than k=1 ({r1}): 115 versus 257", r15 < r1 and r1 == 257 and r15 == 115))

    # confusion matrix and metrics: TP 40, FP 10, FN 20, TN 130
    y_true = np.r_[np.ones(60, int), np.zeros(140, int)]
    y_pred = np.r_[np.ones(40, int), np.zeros(20, int), np.ones(10, int), np.zeros(130, int)]
    checks.append(("confusion counts are TP 40, FP 10, FN 20, TN 130", L.confusion(y_true, y_pred) == (40, 10, 20, 130)))
    mt = L.metrics(40, 10, 20, 130)
    checks.append((f"worked example: accuracy 0.85, precision 0.8, recall 0.667, F1 0.727 (got {mt['accuracy']:.3f}, {mt['precision']:.3f}, {mt['recall']:.3f}, {mt['f1']:.3f})",
                   abs(mt["accuracy"] - 0.85) < 1e-12 and abs(mt["precision"] - 0.8) < 1e-12 and abs(mt["recall"] - 2 / 3) < 1e-12 and abs(mt["f1"] - 80 / 110) < 1e-12))
    z = L.metrics(0, 0, 5, 5)
    checks.append(("no predicted positives: precision and F1 reported as 0, no division error", z["precision"] == 0.0 and z["f1"] == 0.0 and abs(z["accuracy"] - 0.5) < 1e-12))

    # base-rate trap
    q = L.ppv(0.01, 0.99, 0.95)
    checks.append((f"worked example: prevalence 1%, sensitivity 99%, specificity 95% gives PPV 16.7% (got {100 * q:.2f}%)", abs(q - 99 / 594) < 1e-12 and abs(q - 0.1667) < 1e-4))
    pop = 10000
    tp, fn_ = pop * 0.01 * 0.99, pop * 0.01 * 0.01
    fp, tn = pop * 0.99 * 0.05, pop * 0.99 * 0.95
    checks.append(("per 10000 people: 99 true positives, 1 miss, 495 false alarms, 9405 true negatives", (round(tp), round(fn_), round(fp), round(tn)) == (99, 1, 495, 9405)))
    checks.append(("overall accuracy of that test is 95.04% yet most positives are false", abs((tp + tn) / pop - 0.9504) < 1e-9 and fp > tp))
    checks.append(("PPV at 1% prevalence: 9.1% for specificity 90%, 50% for 99%; 83% at 20% prevalence with specificity 95%",
                   abs(L.ppv(0.01, 0.99, 0.90) - 0.0909) < 1e-4 and abs(L.ppv(0.01, 0.99, 0.99) - 0.5) < 1e-12 and abs(L.ppv(0.2, 0.99, 0.95) - 0.832) < 1e-3))
    checks.append(("PPV rises with prevalence", L.ppv(0.2, 0.99, 0.95) > L.ppv(0.01, 0.99, 0.95)))
    checks.append(("PPV is 1 for a perfectly specific test and 0 when there are no true cases", abs(L.ppv(0.01, 0.99, 1.0) - 1.0) < 1e-12 and L.ppv(0.0, 0.99, 0.95) == 0.0))

    # threshold design
    checks.append(("hand rule: cost 10 per miss and 1 per false alarm gives threshold 1/11 = 0.0909", abs(L.bayes_threshold(10, 1) - 1 / 11) < 1e-12))
    rng = np.random.default_rng(0)
    p = rng.uniform(0, 1, 20000)
    ysim = (rng.random(20000) < p).astype(int)
    tb, _ = L.best_threshold(ysim, p, 10, 1)
    checks.append((f"searched threshold on true probabilities is close to 1/11 (got {tb:.3f})", abs(tb - 1 / 11) < 0.03))
    Xva, yva = L.make_moons(100, 0.3, seed=2)
    sv, st = L.knn_score(Xtr, ytr, Xva, 15), L.knn_score(Xtr, ytr, Xte, 15)
    thr, _ = L.best_threshold(yva, sv, 10, 1)
    c_tuned, c_half = L.total_cost(yte, st, thr, 10, 1), L.total_cost(yte, st, 0.5, 10, 1)
    checks.append((f"design: a miss costs 10, a false alarm 1: threshold 4/15 = 0.267 gives test cost 55 versus 90 at 0.5 (got {thr:.3f}, {c_tuned:.0f}, {c_half:.0f})",
                   abs(thr - 4 / 15) < 1e-9 and c_tuned == 55 and c_half == 90))
    checks.append(("equal costs: the cost is the same as 'number of mistakes'", L.total_cost(yte, st, 0.5, 1, 1) == len(yte) - sum(1 for a, b in zip(yte, st >= 0.5) if a == int(b))))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
