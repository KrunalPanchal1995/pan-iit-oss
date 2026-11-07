"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # --- sigmoid ---
    checks.append(("sigmoid(0) = 0.5 and the slope there is 0.25",
                   abs(float(L.sigmoid(0.0)) - 0.5) < 1e-12 and abs(float(L.sigmoid_prime(0.0)) - 0.25) < 1e-12))
    checks.append(("worked example: sigmoid(2) = 0.8808 and s'(2) = 0.8808 * 0.1192 = 0.1050",
                   abs(float(L.sigmoid(2.0)) - 0.8808) < 1e-4 and abs(float(L.sigmoid_prime(2.0)) - 0.1050) < 1e-4))
    z = np.linspace(-8, 8, 1001)
    h = 1e-6
    num = (L.sigmoid(z + h) - L.sigmoid(z - h)) / (2 * h)
    checks.append(("s' = s (1 - s) matches a numerical derivative everywhere on [-8, 8] (error < 1e-8)",
                   float(np.max(np.abs(num - L.sigmoid_prime(z)))) < 1e-8))
    checks.append(("edge: sigmoid(-800) = 0 and sigmoid(800) = 1 without overflow",
                   float(L.sigmoid(-800.0)) == 0.0 and float(L.sigmoid(800.0)) == 1.0))
    checks.append(("sigmoid(-2) = 1 - sigmoid(2) = 0.1192", abs(float(L.sigmoid(-2.0)) - 0.1192) < 1e-4))
    # --- perceptron convergence ---
    ok, within, n_runs = True, True, 0
    for seed in range(10):
        for gap in (0.3, 0.1):
            X, y, wt, bt = L.make_separable(60, gap, seed)
            w, ups, epochs = L.perceptron_fit(X, y)
            n_runs += 1
            ok &= epochs > 0 and bool(np.all((np.c_[X, np.ones(len(X))] @ w > 0) == (y == 1)))
            within &= ups <= L.novikoff_bound(X, y, wt, bt)
    checks.append((f"perceptron rule stops with a perfect line in all {n_runs} seeded runs", ok))
    checks.append(("updates never exceed the bound (R / gamma)^2 in any run", within))
    X, y, wt, bt = L.make_separable(60, 0.3, 0)
    w, ups, epochs = L.perceptron_fit(X, y)
    checks.append(("seed 0, gap 0.3: 5 updates in 2 passes, bound 203.9",
                   ups == 5 and epochs == 2 and abs(L.novikoff_bound(X, y, wt, bt) - 203.9) < 0.05))
    X, y, wt, bt = L.make_separable(60, 0.1, 9)
    w, ups, epochs = L.perceptron_fit(X, y)
    checks.append(("seed 9, gap 0.1 (a thin gap): 29 updates in 13 passes", ups == 29 and epochs == 13))
    # --- logistic regression ---
    X1 = np.array([[1.0, 2.0]])
    y1 = np.array([1.0])
    g = L.logreg_grad(np.zeros(2), 0.0, X1, y1)
    checks.append(("worked example: one point (1, 2), label 1, w = 0, b = 0 gives p = 0.5 and gradient (-0.5, -1), -0.5",
                   np.allclose(g[0], [-0.5, -1.0]) and abs(g[1] + 0.5) < 1e-12))
    l0 = L.logreg_loss(np.zeros(2), 0.0, X1, y1)
    l1 = L.logreg_loss(np.array([0.5, 1.0]), 0.5, X1, y1)
    checks.append(("worked example: the loss falls from ln 2 = 0.6931 to 0.0486 after one step with lr = 1",
                   abs(l0 - np.log(2)) < 1e-12 and abs(l1 - 0.0486) < 1e-4))
    X, y = L.make_blobs(100, 3.0, 0)
    w = np.array([0.3, -0.2])
    b = 0.1
    ga, gb = L.logreg_grad(w, b, X, y)
    na, nb = L.numeric_grad(w, b, X, y)
    A = np.r_[ga, gb]
    Nn = np.r_[na, nb]
    rel = float(np.linalg.norm(A - Nn) / np.linalg.norm(A + Nn))
    checks.append((f"gradient (p - y) x matches finite differences (relative error {rel:.1e} < 1e-6)", rel < 1e-6))
    x2 = np.array([[2.0, -1.0]])
    y2 = np.array([0.0])
    g2 = L.logreg_grad(np.zeros(2), 0.0, x2, y2)
    w2, b2 = -0.4 * g2[0], -0.4 * g2[1]
    checks.append(("hand calculation: point (2, -1), label 0, w = 0, b = 0: p = 0.5, gradient (1, -0.5) and 0.5 for the bias",
                   np.allclose(g2[0], [1.0, -0.5]) and abs(g2[1] - 0.5) < 1e-12))
    z2 = float((np.array([2.0, -1.0]) @ w2) + b2)
    checks.append(("hand calculation: one step with lr = 0.4 gives w = (-0.4, 0.2), b = -0.2, z = -1.2, p = 0.2315 and loss 0.2633 (down from 0.6931)",
                   np.allclose(w2, [-0.4, 0.2]) and abs(b2 + 0.2) < 1e-12 and abs(z2 + 1.2) < 1e-12
                   and abs(float(L.sigmoid(z2)) - 0.2315) < 1e-4 and abs(L.logreg_loss(w2, b2, x2, y2) - 0.2633) < 1e-4))
    # --- learning rates ---
    L_small = L.train_logreg(X, y, 0.01, 100)[2]
    L_mid = L.train_logreg(X, y, 1.0, 100)[2]
    L_big = L.train_logreg(X, y, 100.0, 100)[2]
    checks.append(("lr = 0.01 is too slow: loss 0.414 after 100 epochs, still above 0.2", abs(L_small[-1] - 0.414) < 5e-4 and L_small[-1] > 0.2))
    checks.append(("lr = 1 settles at loss 0.188", abs(L_mid[-1] - 0.188) < 5e-4))
    checks.append(("lr = 100 is too large: loss 0.699 after 100 epochs, worse than the start (ln 2 = 0.693)",
                   abs(L_big[-1] - 0.699) < 5e-4 and L_big[-1] > L_big[0]))
    checks.append(("design: loss <= 0.2 first reached after 15 epochs at lr = 1, 156 at lr = 0.1, never within 500 at lr = 0.01",
                   L.epochs_to_reach(X, y, 1.0, 0.2) == 15 and L.epochs_to_reach(X, y, 0.1, 0.2) == 156
                   and L.epochs_to_reach(X, y, 0.01, 0.2) is None))
    checks.append(("trap: lr = 100 touches 0.2 at epoch 22 but ends at 0.699 (look at the whole curve)",
                   L.epochs_to_reach(X, y, 100.0, 0.2) == 22 and L_big[-1] > 0.6))
    q = L.gd_quadratic(0.4, 5)
    checks.append(("L = w^2: lr = 0.4 shrinks w by 0.2 each step (1 -> 0.2 -> 0.04)", abs(q[1] - 0.2) < 1e-12 and abs(q[2] - 0.04) < 1e-12))
    q = L.gd_quadratic(1.1, 5)
    checks.append(("L = w^2: lr = 1.1 multiplies w by -1.2 each step and diverges (|w| = 2.49 after 5 steps)",
                   abs(q[5] + 2.48832) < 1e-5))
    q = L.gd_quadratic(1.0, 4)
    checks.append(("edge: lr = 1 on L = w^2 flips the sign forever and never converges", q == [1.0, -1.0, 1.0, -1.0, 1.0]))
    # --- the app data set ---
    _, _, la = L.train_logreg(L.APP_X, L.APP_Y, 1.0, 10)
    _, _, lb = L.train_logreg(L.APP_X, L.APP_Y, 0.05, 10)
    wa, ba, lc = L.train_logreg(L.APP_X, L.APP_Y, 1.0, 100)
    checks.append(("app data set: lr = 1 reaches loss 0.353 in 10 epochs; lr = 0.05 only 0.570; the floor is 0.350",
                   abs(la[-1] - 0.353) < 5e-4 and abs(lb[-1] - 0.570) < 5e-4 and abs(lc[-1] - 0.350) < 5e-4))
    checks.append(("app data set: accuracy 10 of 12 points (0.833)", abs(L.accuracy(wa, ba, L.APP_X, L.APP_Y) - 10 / 12) < 1e-9))
    # --- XOR ---
    best, perfect, total, _ = L.best_line_score(L.XOR_X, L.XOR_Y)
    checks.append((f"XOR: exhaustive search over {total} lines finds none with 4 of 4 and the best gets {best}",
                   total == 720 * 501 and perfect == 0 and best == 3))
    bA, pA, _, _ = L.best_line_score(L.XOR_X, L.AND_Y)
    checks.append(("control: the same search finds 4 of 4 for AND (6723 perfect lines)", bA == 4 and pA == 6723))
    # hand proof: z(0,0) + z(1,1) = z(0,1) + z(1,0) for every line
    rng = np.random.default_rng(0)
    okp = True
    for _ in range(1000):
        wv, bv = rng.normal(size=2), rng.normal()
        zz = L.XOR_X @ wv + bv
        okp &= abs(zz[0] + zz[3] - zz[1] - zz[2]) < 1e-12
    checks.append(("proof step: for every line, z(0,0) + z(1,1) = z(0,1) + z(1,0)", okp))
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
