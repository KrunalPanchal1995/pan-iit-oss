"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    gap = L.gradient_check()
    checks.append((f"hand-coded backpropagation matches finite differences (worst gap {gap:.1e})", gap < 1e-6))

    # slope formula against a finite difference
    P = L.init_net(6, 2)
    x = np.array([0.2, 0.9, 1.7])
    h = 1e-6
    ux_fd = (L.forward(P, x + h)[0] - L.forward(P, x - h)[0]) / (2 * h)
    checks.append(("du/dx formula matches a finite difference", np.allclose(L.forward(P, x)[1], ux_fd, atol=1e-6)))

    # worked example: trial function exp(-0.8 x) at x = 0, 1, 2
    k = 0.8
    xs = np.array([0.0, 1.0, 2.0])
    u, ux = np.exp(-k * xs), -k * np.exp(-k * xs)
    loss = L.ode_loss(u, ux, u[0])
    hand = ((0.2) ** 2 + (0.2 * np.exp(-0.8)) ** 2 + (0.2 * np.exp(-1.6)) ** 2) / 3
    checks.append((f"worked example: trial exp(-0.8 x) at x = 0, 1, 2 has loss 0.0166 (got {loss:.4f})", abs(loss - 0.0166) < 5e-5 and abs(loss - hand) < 1e-12))
    checks.append(("the exact solution exp(-x) has zero loss", L.ode_loss(np.exp(-xs), -np.exp(-xs), 1.0) < 1e-24))

    # hand calculation (Section F, B): one unit u = tanh(x) at x = 0.5 has u' + u = 1.249
    Q = {"a": np.array([1.0]), "d": np.array([0.0]), "c": np.array([1.0]), "e": np.zeros(1)}
    uq, uxq, _ = L.forward(Q, np.array([0.5]))
    checks.append((f"hand calculation: a single unit tanh(x) has u' + u = 1.249 at x = 0.5 (got {uq[0] + uxq[0]:.3f})", abs(uq[0] + uxq[0] - 1.249) < 5e-4))

    # data fit
    xd, yd = L.noisy_samples()
    Pd = L.fit_data(xd, yd)
    rms_data = float(np.sqrt(np.mean((L.forward(Pd, xd)[0] - yd) ** 2)))
    xt = np.linspace(0, 1, 201)
    rms_true = float(np.sqrt(np.mean((L.forward(Pd, xt)[0] - np.sin(2 * np.pi * xt)) ** 2)))
    checks.append((f"data fit: rms to samples {rms_data:.3f} is below the noise level 0.1 (a fit this tight follows noise)", rms_data < 0.1))
    checks.append((f"data fit: rms to the true curve is below 0.12 (got {rms_true:.3f})", rms_true < 0.12))

    # Adam moves downhill on a simple bowl
    Q = {"w": np.array([3.0])}
    opt = L.Adam(Q, lr=0.1)
    for _ in range(200):
        opt.step(Q, {"w": 2 * Q["w"]})
    checks.append(("Adam minimises w^2 from w = 3", abs(Q["w"][0]) < 0.05))

    # collocation study (Section E and F numbers)
    errs = {n: L.ode_errors(L.train_ode(n)) for n in (2, 3, 5, 8, 20)}
    checks.append((f"N = 2 points: error above 0.3 (got {errs[2][0]:.3f})", errs[2][0] > 0.3))
    checks.append((f"N = 5 points: error between 0.01 and 0.02 (got {errs[5][0]:.4f})", 0.01 < errs[5][0] < 0.02))
    checks.append((f"N = 8 points: error below 0.01 (got {errs[8][0]:.4f})", errs[8][0] < 0.01))
    checks.append((f"N = 20 points: error below 0.002 (got {errs[20][0]:.4f})", errs[20][0] < 0.002))
    checks.append(("the largest residual between points is larger than the error (N = 3, residual 0.30)", errs[3][1] > errs[3][0] and abs(errs[3][1] - 0.30) < 0.01))
    checks.append(("error falls as N grows (2 > 3 > 5 > 8)", errs[2][0] > errs[3][0] > errs[5][0] > errs[8][0]))

    # linear cousin used by the app
    e_lin = {n: L.linear_errors(L.linear_pinn(n, 8))[0] for n in (3, 5, 10, 25)}
    checks.append((f"edge: the linear cousin with 3 points is poor (error {e_lin[3]:.2f}) and with 10 points good (error {e_lin[10]:.4f})", e_lin[3] > 0.2 and e_lin[10] < 0.01))
    c = L.linear_pinn(6, 8)
    xc = np.linspace(0, 2, 6)
    F, D = L.bump_features(xc, 8)
    xm = np.linspace(0, 2, 401)
    Fm, Dm = L.bump_features(xm, 8)
    checks.append(("linear cousin: residual is ~0 at the 6 points but not between them",
                   bool(np.abs((F + D) @ c).max() < 1e-3 and np.abs((Fm + Dm) @ c).max() > 0.1)))
    checks.append(("app challenge: 8 to 16 units and 10 to 30 points give error below 0.01",
                   all(L.linear_errors(L.linear_pinn(n, H))[0] < 0.01 for H in (8, 10, 12, 16) for n in (10, 15, 30))))
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
