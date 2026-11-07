"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # ROC and AUC: hand example, scores 0.1 0.4 0.35 0.8, labels 0 0 1 1
    s, y = np.array([0.1, 0.4, 0.35, 0.8]), np.array([0, 0, 1, 1])
    fpr, tpr, thr = L.roc_curve(s, y)
    checks.append(("ROC hand example: points (0,0) (0,.5) (.5,.5) (.5,1) (1,1)",
                   np.allclose(fpr, [0, 0, 0.5, 0.5, 1]) and np.allclose(tpr, [0, 0.5, 0.5, 1, 1])))
    checks.append(("worked example: AUC of the four scores is 0.75 by area and by pairs", abs(L.auc_trapezoid(fpr, tpr) - 0.75) < 1e-12 and abs(L.auc_pairs(s, y) - 0.75) < 1e-12))
    checks.append(("perfect ranking gives AUC 1, reversed ranking gives AUC 0", abs(L.auc_pairs(np.array([0.1, 0.2, 0.8, 0.9]), y) - 1) < 1e-12 and abs(L.auc_pairs(np.array([0.9, 0.8, 0.2, 0.1]), y)) < 1e-12))
    checks.append(("all scores tied: AUC is 0.5 (ties count one half)", abs(L.auc_pairs(np.ones(4), y) - 0.5) < 1e-12 and abs(L.auc_trapezoid(*L.roc_curve(np.ones(4), y)[:2]) - 0.5) < 1e-12))

    Xa, ya = L.make_data(400, 3, flip=0.1)
    Xb, yb = L.make_data(400, 4, flip=0.1)
    sc = L.forest_votes(L.fit_forest(Xa, ya, 25, 5, 1), Xb) + 0.001 * L.tree_scores(L.grow_tree(Xa, ya, 3), Xb)
    f, t_, _ = L.roc_curve(sc, yb)
    a1, a2 = L.auc_trapezoid(f, t_), L.auc_pairs(sc, yb)
    checks.append((f"AUC from the curve equals the pair probability on 400 scored cases: {a1:.4f} = {a2:.4f}", abs(a1 - a2) < 1e-12 and abs(a1 - 0.8244) < 1e-4))
    checks.append(("ROC curve rises monotonically from (0,0) to (1,1)", bool(np.all(np.diff(f) >= 0) and np.all(np.diff(t_) >= 0) and f[0] == 0 and t_[0] == 0 and f[-1] == 1 and t_[-1] == 1)))
    prec, rec, _ = L.precision_recall_points(np.array([0.9, 0.8, 0.7, 0.2]), np.array([1, 0, 1, 0]))
    checks.append(("precision-recall by hand: thresholds 0.9, 0.8, 0.7, 0.2 give precision 1, 1/2, 2/3, 1/2 and recall 1/2, 1/2, 1, 1",
                   np.allclose(prec, [1, 0.5, 2 / 3, 0.5]) and np.allclose(rec, [0.5, 0.5, 1, 1])))

    # forest versus single tree
    single, forest, ws, wf = L.single_vs_forest()
    checks.append((f"forest beats one full tree on average: 0.716 versus 0.677 (got {forest.mean():.3f}, {single.mean():.3f})", abs(forest.mean() - 0.716) < 0.0015 and abs(single.mean() - 0.677) < 0.0015))
    checks.append((f"prediction wobble across training sets falls from 0.157 to 0.112 (got {ws:.3f}, {wf:.3f})", wf < ws and abs(ws - 0.157) < 0.0015 and abs(wf - 0.112) < 0.0015))

    # overfitting with depth
    depths = list(range(1, 21))
    tr, te = L.depth_curve(depths)
    checks.append(("training accuracy never falls as depth grows and reaches 100% by depth 15", bool(np.all(np.diff(tr) >= -1e-12)) and tr[14] == 1.0 and tr[-1] == 1.0))
    checks.append((f"test accuracy peaks at depth 2 (0.7385) and falls to 0.6065 at depth 20", int(np.argmax(te)) == 1 and abs(te[1] - 0.7385) < 1e-6 and abs(te[-1] - 0.6065) < 1e-6))
    checks.append(("a depth-1 tree has train accuracy 0.733", abs(tr[0] - 0.733) < 5e-4))

    # k-fold written by hand
    folds = L.kfold_indices(10, 3, seed=0)
    allidx = np.sort(np.concatenate(folds))
    checks.append(("k-fold: folds of 10 cases into 3 have sizes 4, 3, 3 and cover every case exactly once", [len(x) for x in folds] == [4, 3, 3] and np.array_equal(allidx, np.arange(10))))
    Xc, yc = L.make_data(200, 11, flip=0.15)
    cv, per = L.cross_val_accuracy(lambda a, b, c: L.tree_scores(L.grow_tree(a, b, 3), c) > 0.5, Xc, yc, 5)
    checks.append((f"5-fold cross-validated accuracy of a depth-3 tree is 0.77 (got {cv:.3f})", len(per) == 5 and abs(cv - 0.77) < 5e-4))
    checks.append(("a classifier that always says 0 on balanced labels scores 0.5 in CV", abs(L.cross_val_accuracy(lambda a, b, c: np.zeros(len(c), int), Xc, (np.arange(200) % 2), 5)[0] - 0.5) < 1e-12))

    # calibration
    rng = np.random.default_rng(2)
    p_true = rng.uniform(0, 1, 4000)
    y_cal = (rng.random(4000) < p_true).astype(int)
    p_over = np.clip(0.5 + 1.8 * (p_true - 0.5), 0.001, 0.999)
    e1, e2 = L.expected_calibration_error(p_true, y_cal), L.expected_calibration_error(p_over, y_cal)
    checks.append((f"calibration error: 0.01 for honest probabilities, 0.12 for over-confident ones (got {e1:.3f}, {e2:.3f})", abs(e1 - 0.01) < 0.005 and abs(e2 - 0.12) < 0.005))
    mp, fr, cnt = L.reliability(np.array([0.1, 0.1, 0.9, 0.9]), np.array([0, 0, 1, 1]), 2)
    checks.append(("reliability by hand: two bins, mean scores 0.1 and 0.9, fractions 0 and 1", np.allclose(mp, [0.1, 0.9]) and np.allclose(fr, [0, 1]) and list(cnt) == [2, 2]))

    # fairness
    r = L.group_rates_analytic(1.0, 0.5)
    checks.append(("worked example: threshold 1.0, shift 0.5: FPR A 0.1587, FPR B 0.3085, TPR A 0.6915, TPR B 0.8413",
                   abs(r["fpr_A"] - 0.1587) < 5e-5 and abs(r["fpr_B"] - 0.3085) < 5e-5 and abs(r["tpr_A"] - 0.6915) < 5e-5 and abs(r["tpr_B"] - 0.8413) < 5e-5))
    checks.append(("Phi(0) = 0.5 and Phi(1.96) = 0.975 (reference values)", abs(L.phi(0) - 0.5) < 1e-12 and abs(L.phi(1.96) - 0.975) < 1e-4))
    sa, ya_ = L.simulate_group(20000, 0.0, seed=1)
    sb, yb_ = L.simulate_group(20000, 0.5, seed=2)
    fa_, ta_ = L.empirical_rates(sa, ya_, 1.0)
    fb_, tb_ = L.empirical_rates(sb, yb_, 1.0)
    checks.append((f"simulation agrees with theory within 0.01: FPR A {fa_:.3f}, FPR B {fb_:.3f}", abs(fa_ - r["fpr_A"]) < 0.01 and abs(fb_ - r["fpr_B"]) < 0.01 and abs(ta_ - r["tpr_A"]) < 0.01 and abs(tb_ - r["tpr_B"]) < 0.015))
    checks.append(("one threshold, unequal false-positive rates: group B has about twice the FPR", fb_ > 1.8 * fa_))
    ua, ub = L.auc_pairs(sa[:3000], ya_[:3000]), L.auc_pairs(sb[:3000], yb_[:3000])
    theory = L.phi(1.5 / math.sqrt(2))
    checks.append((f"AUC is the same for both groups (about {theory:.3f}), so ranking alone hides the gap", abs(ua - theory) < 0.02 and abs(ub - theory) < 0.02))
    checks.append(("with no shift the two groups have identical rates", L.group_rates_analytic(1.0, 0.0)["fpr_A"] == L.group_rates_analytic(1.0, 0.0)["fpr_B"]))

    # failure cases
    leaks, honests = [], []
    for sd in range(10):
        Xn, yn = L.make_noise(60, 500, sd)
        leaks.append(L.leaky_cv(Xn, yn))
        honests.append(L.honest_cv(Xn, yn))
    checks.append((f"leakage: on pure noise, leaky CV reads {np.mean(leaks):.3f} (0.825) and honest CV reads {np.mean(honests):.3f} (0.452), true value 0.5",
                   abs(np.mean(leaks) - 0.825) < 0.005 and abs(np.mean(honests) - 0.452) < 0.005))
    acc, recall = L.imbalance_demo()
    checks.append(("accuracy paradox: always saying negative at 1% prevalence has accuracy 0.99 and recall 0", abs(acc - 0.99) < 1e-12 and recall == 0.0))

    # mini-project helper
    cost, cm = L.cost_and_confusion(np.array([1, 1, 0, 0, 0]), np.array([0.9, 0.2, 0.6, 0.1, 0.3]), 0.5)
    checks.append(("cost by hand: scores at threshold 0.5 give TP 1, FP 1, FN 1, TN 2 and cost 20 + 1 = 21", cm == (1, 1, 1, 2) and cost == 21))
    study = L.screening_study()
    costs = {k: v["test_cost"] for k, v in study.items()}
    _, ytest = L.make_screening(3000, 9)
    checks.append(("screening: 115 positives in the test set, so flagging nobody costs 2300", int(ytest.sum()) == 115 and 20 * int(ytest.sum()) == 2300))
    checks.append((f"screening test costs: tree depth 3 = 1360, tree depth 8 = 1685, forest = 1230 (got {costs})",
                   costs["tree depth 3"] == 1360 and costs["tree depth 8"] == 1685 and costs["forest 25 x depth 6"] == 1230))
    checks.append(("screening: forest confusion matrix (TP, FP, FN, TN) = (76, 450, 39, 2435)", study["forest 25 x depth 6"]["confusion"] == (76, 450, 39, 2435)))
    checks.append(("the deeper tree overfits: it is worse than the depth-3 tree on the test set", costs["tree depth 8"] > costs["tree depth 3"]))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
