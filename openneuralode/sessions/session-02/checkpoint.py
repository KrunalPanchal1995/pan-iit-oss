"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # --- hand calculation: the rule at (1, 0) and one step of each method
    f0 = L.true_field(np.array([1.0, 0.0]))
    checks.append(("hand calculation: at x = 1, v = 0 the rule gives dx/dt = 0 and dv/dt = -4", np.allclose(f0, [0.0, -4.0])))
    x1 = np.array([1.0, 0.0])
    eu, rk, ex = L.euler_step(L.true_field, x1, 0.1), L.rk4_step(L.true_field, x1, 0.1), L.exact_state(x1, 0.1)
    err_eu, err_rk = float(np.linalg.norm(eu - ex)), float(np.linalg.norm(rk - ex))
    checks.append((f"worked example: from (1, 0) one Euler step of 0.1 s gives (1.0, -0.4); RK4 gives (0.9803, -0.3895) = exact to 1e-5",
                   np.allclose(eu, [1.0, -0.4], atol=1e-12) and np.allclose(rk, [0.9803, -0.3895], atol=1e-4) and err_rk < 1e-5))
    checks.append((f"worked example: the Euler step is off by {err_eu:.3f} (about 0.022), the RK4 step by under 1e-5", abs(err_eu - 0.0223) < 5e-4))

    k1 = L.true_field(x1)
    k2 = L.true_field(x1 + 0.05 * k1)
    k3 = L.true_field(x1 + 0.05 * k2)
    k4 = L.true_field(x1 + 0.1 * k3)
    checks.append(("worked example: RK4 stages from (1, 0) are k1 = (0, -4), k2 = (-0.2, -3.92), k3 = (-0.196, -3.8816), k4 = (-0.38816, -3.766336)",
                   np.allclose(k1, [0, -4]) and np.allclose(k2, [-0.2, -3.92]) and np.allclose(k3, [-0.196, -3.8816]) and np.allclose(k4, [-0.38816, -3.766336])))

    # --- order of accuracy
    hs = np.array([0.2, 0.1, 0.05, 0.025, 0.0125])
    pe, pr = L.observed_order(L.euler_step, hs), L.observed_order(L.rk4_step, hs)
    checks.append((f"Euler is first order: measured slope {pe:.2f} is between 0.9 and 1.2", 0.9 < pe < 1.2))
    checks.append((f"RK4 is fourth order: measured slope {pr:.2f} is between 3.8 and 4.3", 3.8 < pr < 4.3))
    r_eu = L.error_at_T(L.euler_step, 0.1) / L.error_at_T(L.euler_step, 0.05)
    r_rk = L.error_at_T(L.rk4_step, 0.1) / L.error_at_T(L.rk4_step, 0.05)
    checks.append((f"halving h divides the Euler error by about 2 ({r_eu:.2f}) and the RK4 error by about 16 ({r_rk:.1f})", 1.8 < r_eu < 2.5 and 14 < r_rk < 20))
    e1, e4, r1 = L.error_at_T(L.euler_step, 0.1), L.error_at_T(L.euler_step, 0.025), L.error_at_T(L.rk4_step, 0.1)
    checks.append((f"Euler error at 2 s is {e1:.3f} for h = 0.1 and {e4:.3f} for h = 0.025 (a first-order guess says a quarter of the first: 0.144); RK4 at h = 0.1 gives {r1:.1e}",
                   abs(e1 - 0.575) < 0.002 and abs(e4 - 0.128) < 0.002 and 4.2e-5 < r1 < 4.4e-5))
    checks.append(("exact solution at t = 0 is the starting state", np.allclose(L.exact_state([1.0, 0.5], 0.0), [1.0, 0.5])))

    # --- derivatives and least squares
    t = 0.1 * np.arange(6)
    lin = np.stack([np.stack([3.0 * t, -2.0 * t], axis=1)], axis=1)       # (6, 1, 2): straight line
    S, D = L.central_difference(lin, 0.1)
    checks.append(("edge: central differences of a straight line give its slope exactly, and drop the two ends",
                   S.shape == (4, 2) and np.allclose(D, [3.0, -2.0])))
    X = L.make_data(10, 20, 0.1, 0.01)
    A_hat = L.fit_linear_field(X, 0.1)
    e_fit = float(np.linalg.norm(A_hat - L.A_TRUE))
    checks.append((f"least squares recovers A to within 0.06 with 10 runs and noise 0.01 (error {e_fit:.3f})", e_fit < 0.06))
    checks.append(("the fitted A has the structure of the truth: upper right near 1 and lower left near -4",
                   abs(A_hat[0, 1] - 1.0) < 0.05 and abs(A_hat[1, 0] + 4.0) < 0.2))

    # --- design problem: how much data and how little noise
    e_k10 = L.mean_fit_error(10, 0.05)
    e_k1 = L.mean_fit_error(1, 0.05)
    e_s1 = L.mean_fit_error(1, 0.01)
    e_k3 = L.mean_fit_error(3, 0.05)
    checks.append((f"design: noise 0.01 with a single run already passes (error {e_s1:.3f}); noise 0.05 with 3 runs just passes on average (error {e_k3:.3f}, between 0.08 and 0.1)", e_s1 < 0.1 and 0.08 < e_k3 < 0.1))
    e_n30 = L.mean_fit_error(30, 0.2)
    e_n10 = L.mean_fit_error(10, 0.2)
    checks.append((f"design: noise 0.05 with 10 runs reaches error {e_k10:.3f}, below the target 0.1", e_k10 < 0.1))
    checks.append((f"design: noise 0.05 with only 1 run fails the target (error {e_k1:.3f})", e_k1 > 0.1))
    checks.append((f"design: at noise 0.2 even 30 runs leave error {e_n30:.2f} (above 0.3) and gain under 10 percent over 10 runs ({e_n10:.2f})",
                   e_n30 > 0.3 and e_n30 > 0.9 * e_n10))

    # --- the network: gradient check, then training
    P = L.init_mlp(5, seed=2)
    S2 = np.random.default_rng(0).normal(size=(7, 2))
    D2 = np.random.default_rng(1).normal(size=(7, 2))
    _, G = L.mlp_loss_grad(P, S2, D2)
    worst = 0.0
    for key in P:
        idx = (0,) * P[key].ndim
        e = 1e-6
        P[key][idx] += e
        lp = L.mlp_loss_grad(P, S2, D2)[0]
        P[key][idx] -= 2 * e
        lm = L.mlp_loss_grad(P, S2, D2)[0]
        P[key][idx] += e
        fd = (lp - lm) / (2 * e)
        worst = max(worst, abs(G[key][idx] - fd) / (abs(fd) + 1e-12))
    checks.append((f"hand-written backpropagation matches finite differences (worst relative gap {worst:.1e})", worst < 1e-6))
    checks.append(("the network has 82 parameters at width 16", sum(v.size for v in L.init_mlp(16).values()) == 82))
    S, D = L.central_difference(X, 0.1)
    Pn, hist = L.train_one_step(S, D)
    checks.append((f"training: the one-step loss falls from {hist[0]:.2f} to {hist[-1]:.4f} (below 0.01)", hist[-1] < 0.01 < hist[0]))
    e_nn = L.field_rms_error(lambda g: L.mlp(Pn, g))
    e_ls = L.field_rms_error(lambda g: g @ A_hat.T)
    checks.append((f"the network's field is within 0.15 RMS of the truth (got {e_nn:.3f})", e_nn < 0.15))
    checks.append((f"for a linear truth the 4-number least-squares fit is more accurate ({e_ls:.3f}) than the 82-number network", e_ls < e_nn))
    r_nn = L.rollout_error(lambda g: L.mlp(Pn, g))
    checks.append((f"predicting 3 s ahead with the network and RK4 is within 0.2 of the truth (got {r_nn:.3f})", r_nn < 0.2))
    checks.append(("edge: an untrained network with zero weights gives zero field",
                   float(np.abs(L.mlp({"W1": np.zeros((4, 2)), "b1": np.zeros(4), "W2": np.zeros((2, 4)), "b2": np.zeros(2)}, np.ones((3, 2)))).max()) == 0.0))
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
