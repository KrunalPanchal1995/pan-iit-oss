"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # --- worked example: a 2-2-1 tanh network, one sample, by hand ---
    W1 = np.array([[0.5, -0.3], [0.2, 0.4]])
    W2 = np.array([[0.6], [-0.4]])
    params = [[W1.copy(), np.zeros(2)], [W2.copy(), np.zeros(1)]]
    x = np.array([[1.0, 0.0]])
    y1 = np.array([1.0])
    P, cache = L.forward(params, x)
    H = np.tanh(cache[0][1])
    checks.append(("worked example: Z1 = (0.5, -0.3), H = (0.4621, -0.2913)",
                   np.allclose(cache[0][1], [[0.5, -0.3]]) and np.allclose(H, [[0.4621, -0.2913]], atol=1e-4)))
    checks.append(("worked example: Z2 = 0.3938, P = 0.5972, loss = -ln P = 0.5155",
                   abs(cache[1][1][0, 0] - 0.3938) < 1e-4 and abs(P[0] - 0.5972) < 1e-4 and abs(L.bce(P, y1) - 0.5155) < 1e-4))
    g = L.backward(params, cache, P, y1)
    checks.append(("worked example: dZ2 = P - y = -0.4028 and dL/dW2 = (-0.1861, 0.1173)",
                   abs(g[1][1][0] + 0.4028) < 1e-4 and np.allclose(g[1][0].ravel(), [-0.1861, 0.1173], atol=1e-4)))
    checks.append(("worked example: dL/dW1 first row = (-0.1901, 0.1474), second row = 0 (because x2 = 0)",
                   np.allclose(g[0][0][0], [-0.1901, 0.1474], atol=1e-4) and np.allclose(g[0][0][1], 0.0)))
    # hand chain rule for the first weight, written out
    dH = (P[0] - 1.0) * W2.ravel()
    dz1 = dH * (1 - H.ravel() ** 2)
    checks.append(("chain rule by hand: dL/dH = (-0.2417, 0.1611), tanh slope (0.7865, 0.9151)",
                   np.allclose(dH, [-0.2417, 0.1611], atol=1e-4) and np.allclose(1 - H.ravel() ** 2, [0.7865, 0.9151], atol=1e-4)
                   and np.allclose(dz1, g[0][1], atol=1e-12)))
    err0 = L.grad_check(params, x, y1)
    checks.append((f"worked example passes the gradient check (relative error {err0:.1e} < 1e-6)", err0 < 1e-6))

    Hh = np.array([0.5, -0.5])
    checks.append(("hand calculation: P = 0.8, y = 1, H = (0.5, -0.5) gives dZ2 = -0.2, dL/dW2 = (-0.1, 0.1) and loss 0.2231",
                   np.allclose((0.8 - 1.0) * Hh, [-0.1, 0.1]) and abs(L.bce(np.array([0.8]), np.array([1.0])) - 0.2231) < 1e-4))

    # --- the key correctness test ---
    Xg, yg = L.make_moons(40, 0.2, 0)
    errs = {}
    for act in ("tanh", "sigmoid", "relu"):
        errs[act] = L.grad_check(L.init_params([2, 6, 1], 0), Xg, yg, act)
    checks.append(("gradient check, two layers 2-6-1, tanh / sigmoid / relu: worst relative error below 1e-6 (about 1e-9)",
                   max(errs.values()) < 1e-6))
    err3 = L.grad_check(L.init_params([2, 5, 4, 1], 3), Xg, yg, "tanh")
    checks.append((f"gradient check also passes for three layers 2-5-4-1 ({err3:.1e} < 1e-6)", err3 < 1e-6))
    saved = L.ACT["tanh"]
    L.ACT["tanh"] = (np.tanh, lambda z: np.ones_like(z))          # a deliberate bug: forget the slope phi'
    bad = L.grad_check(L.init_params([2, 6, 1], 0), Xg, yg, "tanh")
    L.ACT["tanh"] = saved
    checks.append((f"the check catches a bug: dropping phi' gives relative error {bad:.2f} (> 1e-2)", bad > 1e-2))

    # --- Adam by hand ---
    pa = [[np.array([[1.0]]), np.array([0.0])]]
    opt = L.Optimiser(pa, "adam", lr=0.1)
    opt.step(pa, [[np.array([[2.0]]), np.array([0.0])]])
    checks.append(("hand calculation: the first Adam step with gradient 2 moves the weight by lr = 0.1 (m_hat = 2, sqrt(v_hat) = 2)",
                   abs(pa[0][0][0, 0] - 0.9) < 1e-6))
    pm = [[np.array([[1.0]]), np.array([0.0])]]
    om = L.Optimiser(pm, "momentum", lr=0.1, beta=0.9)
    gm = [[np.array([[1.0]]), np.array([0.0])]]
    om.step(pm, gm)
    om.step(pm, gm)
    checks.append(("hand calculation: momentum with constant gradient 1: steps of 0.1 then 0.19, so w = 1 - 0.29",
                   abs(pm[0][0][0, 0] - 0.71) < 1e-12))

    # --- XOR ---
    p = L.init_params([2, 4, 1], 1)
    L.train(p, L.XOR_X, L.XOR_Y, lr=0.05, epochs=300)
    checks.append(("XOR: a 2-4-1 tanh network gets all 4 points right after 300 Adam epochs (a line gets at most 3)",
                   L.accuracy(p, L.XOR_X, L.XOR_Y) == 1.0))

    # --- spirals ---
    X, y = L.make_spirals(400, 0.05, 0)
    Xtr, ytr, Xte, yte = L.split(X, y, 0.25, 0)
    checks.append(("spirals data: 300 training and 100 test points, both classes present",
                   len(ytr) == 300 and len(yte) == 100 and 0.3 < ytr.mean() < 0.7))
    p = L.init_params([2, 64, 1], 0)
    h = L.train(p, Xtr, ytr, lr=0.02, epochs=600, batch=32, seed=0, Xt=Xte, yt=yte)
    checks.append((f"spirals: 2-64-1 network reaches test accuracy {h['test_acc'][-1]:.2f} (>= 0.95; measured 1.00) on unseen points",
                   h["test_acc"][-1] >= 0.95))
    checks.append((f"spirals: training accuracy {h['acc'][-1]:.3f} (>= 0.97; measured 0.993), loss fell from 0.566 to {h['loss'][-1]:.3f}",
                   h["acc"][-1] >= 0.97 and abs(h["loss"][0] - 0.566) < 0.02 and h["loss"][-1] < 0.1))
    pl = L.init_params([2, 1], 0)
    hl = L.train(pl, Xtr, ytr, lr=0.05, epochs=300, batch=32, seed=0, Xt=Xte, yt=yte)
    checks.append(("spirals: a single neuron (one straight line) reaches only 0.70 test accuracy", abs(hl["test_acc"][-1] - 0.70) < 0.05))

    # --- optimisers on moons ---
    Xm, ym = L.make_moons(300, 0.2, 1)
    res = {}
    for kind in ("sgd", "momentum", "adam"):
        pp = L.init_params([2, 16, 1], 2)
        res[kind] = L.train(pp, Xm, ym, kind=kind, lr=0.05, epochs=40, batch=32, seed=3)["loss"][-1]
    checks.append((f"after 40 epochs the loss is SGD {res['sgd']:.2f} > momentum {res['momentum']:.2f} > Adam {res['adam']:.2f} (about 0.30, 0.15, 0.06)",
                   res["sgd"] > res["momentum"] > res["adam"] and abs(res["sgd"] - 0.30) < 0.04
                   and abs(res["momentum"] - 0.15) < 0.04 and abs(res["adam"] - 0.06) < 0.03))

    # --- overfitting ---
    Xo, yo = L.make_moons(1040, 0.35, 5)
    Xs, ys, Xt, yt = Xo[:40], yo[:40], Xo[40:], yo[40:]
    gaps = {}
    for hid in (3, 100):
        pp = L.init_params([2, hid, 1], 4)
        hh = L.train(pp, Xs, ys, lr=0.01, epochs=1500, Xt=Xt, yt=yt)
        gaps[hid] = (hh["acc"][-1], hh["test_acc"][-1])
    checks.append((f"overfitting: 100 hidden neurons memorise 40 points (train {gaps[100][0]:.2f}) but test only {gaps[100][1]:.2f}; gap {gaps[100][0] - gaps[100][1]:.2f}",
                   gaps[100][0] == 1.0 and abs(gaps[100][1] - 0.80) < 0.03 and gaps[100][0] - gaps[100][1] > 0.15))
    checks.append((f"overfitting: 3 hidden neurons give train {gaps[3][0]:.3f}, test {gaps[3][1]:.2f}; a smaller gap of {gaps[3][0] - gaps[3][1]:.2f}",
                   abs(gaps[3][0] - 0.925) < 1e-9 and abs(gaps[3][1] - 0.82) < 0.03 and (gaps[3][0] - gaps[3][1]) < (gaps[100][0] - gaps[100][1])))

    # --- initialisation ---
    out = {}
    for sch in ("zeros", "const", "xavier"):
        pp = L.init_params([2, 4, 1], 1, sch)
        hh = L.train(pp, L.XOR_X, L.XOR_Y, lr=0.05, epochs=300)
        spread = float(np.abs(pp[0][0] - pp[0][0][:, [0]]).max())
        out[sch] = (hh["acc"][-1], hh["loss"][-1], spread)
    checks.append(("zero weights: nothing learns; accuracy 0.50 and loss stays at ln 2 = 0.693 after 300 epochs",
                   out["zeros"][0] == 0.5 and abs(out["zeros"][1] - np.log(2)) < 1e-9))
    checks.append(("equal weights (all 0.5): hidden neurons stay identical (spread 0) and XOR stays unsolved at 0.75",
                   out["const"][2] == 0.0 and out["const"][0] == 0.75))
    checks.append(("random weights: hidden neurons differ (spread > 1) and XOR is solved (1.00)", out["xavier"][2] > 1.0 and out["xavier"][0] == 1.0))

    # --- learning rate too high ---
    lrs = {}
    for lr in (0.05, 5.0, 50.0, 500.0):
        pp = L.init_params([2, 16, 1], 2)
        hh = L.train(pp, Xm, ym, kind="sgd", lr=lr, epochs=30, batch=32, seed=3)
        lrs[lr] = (hh["loss"][0], hh["loss"][-1], hh["acc"][-1])
    checks.append((f"lr 0.05 and 5: SGD loss falls to {lrs[0.05][1]:.2f} and {lrs[5.0][1]:.2f} (about 0.31 and 0.05)",
                   abs(lrs[0.05][1] - 0.31) < 0.05 and lrs[5.0][1] < 0.15))
    checks.append((f"lr 50 and 500: loss is {lrs[50.0][1]:.1f} and {lrs[500.0][1]:.1f} after 30 epochs, far above the start (about 0.7) and accuracy {lrs[500.0][2]:.2f}",
                   lrs[50.0][1] > 2.0 and lrs[500.0][1] > 5.0 and lrs[500.0][2] < 0.75))

    # --- activations on moons ---
    ar = {}
    for act in ("tanh", "relu", "sigmoid"):
        pp = L.init_params([2, 16, 1], 2, "he" if act == "relu" else "xavier")
        ar[act] = L.train(pp, Xm, ym, act=act, kind="adam", lr=0.05, epochs=40, batch=32, seed=3)["loss"][-1]
    checks.append((f"hidden activations after 40 Adam epochs: loss tanh {ar['tanh']:.2f}, relu {ar['relu']:.2f}, sigmoid {ar['sigmoid']:.2f} (all three learn; sigmoid slowest)",
                   ar["sigmoid"] > ar["tanh"] and ar["sigmoid"] > ar["relu"] and max(ar.values()) < 0.2))

    # --- vanishing gradients ---
    Xv, yv = L.make_moons(200, 0.2, 7)
    rat = {}
    for act, sch in (("sigmoid", "xavier"), ("tanh", "xavier"), ("relu", "he")):
        gn = L.layer_grad_norms(10, 16, act, sch, Xv, yv)
        rat[act] = gn[0] / gn[-1]
        rat[act + "_n"] = len(gn)
    checks.append((f"10 hidden layers: first-layer / last-layer gradient norm is {rat['sigmoid']:.1e} for sigmoid (vanishing), {rat['tanh']:.2f} for tanh, {rat['relu']:.2f} for relu",
                   rat["sigmoid_n"] == 11 and 5e-7 < rat["sigmoid"] < 3e-6 and 0.25 < rat["tanh"] < 0.5 and 0.25 < rat["relu"] < 0.5))
    g20 = L.layer_grad_norms(20, 16, "sigmoid", "xavier", Xv, yv)
    checks.append((f"20 hidden layers of sigmoid: first / last = {g20[0] / g20[-1]:.0e} (below 1e-10)", g20[0] / g20[-1] < 1e-10))
    z = np.linspace(-10, 10, 2001)
    checks.append(("slopes: sigmoid <= 0.25 everywhere, tanh <= 1, relu is 0 or 1",
                   float(L.ACT["sigmoid"][1](z).max()) <= 0.25 + 1e-12 and float(L.ACT["tanh"][1](z).max()) <= 1.0
                   and set(np.unique(L.ACT["relu"][1](z))) <= {0.0, 1.0}))

    # --- mini-project ---
    X, y = L.make_moons(400, 0.25, 11)
    a, b, c, d = L.split(X, y, 0.25, 0)
    accs = {}
    for hid in (2, 4, 16):
        pp = L.init_params([2, hid, 1], 0)
        hh = L.train(pp, a, b, lr=0.02, epochs=300, batch=32, seed=0, Xt=c, yt=d)
        accs[hid] = hh["test_acc"][-1]
        if hid == 16:
            cm = L.confusion(d, L.predict(pp, c))
    checks.append((f"mini-project: test accuracy {accs[2]:.2f} with 2 hidden, {accs[4]:.2f} with 4, {accs[16]:.2f} with 16 (target 0.92 needs at least 4)",
                   accs[2] < 0.92 and accs[4] >= 0.92 and accs[16] >= 0.92))
    checks.append((f"mini-project: confusion matrix for 16 hidden is {cm.tolist()} on 100 test points (3 mistakes)",
                   cm.tolist() == [[50, 2], [1, 47]] and cm.sum() == 100))
    # --- edge cases ---
    cm0 = L.confusion(np.array([0, 1]), np.array([1, 0]))
    checks.append(("edge: confusion matrix of two completely wrong answers is [[0, 1], [1, 0]]", cm0.tolist() == [[0, 1], [1, 0]]))
    checks.append(("edge: loss is finite even when the network is certain and wrong",
                   np.isfinite(L.bce(np.array([0.0, 1.0]), np.array([1.0, 0.0])))))
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
