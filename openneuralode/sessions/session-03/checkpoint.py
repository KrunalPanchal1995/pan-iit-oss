"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # --- the hand-written gradient through RK4 against finite differences
    P = L.init_params(5, seed=3)
    X = L.make_data(3, 6, 0.0, 1)
    x0, targets = L.make_windows(X, 3)
    loss, G = L.rollout_loss_grad(P, x0, L.DT, targets)
    worst = 0.0
    for key in P:
        idx = (0,) * P[key].ndim
        e = 1e-6
        P[key][idx] += e
        lp = L.rollout_loss_grad(P, x0, L.DT, targets)[0]
        P[key][idx] -= 2 * e
        lm = L.rollout_loss_grad(P, x0, L.DT, targets)[0]
        P[key][idx] += e
        fd = (lp - lm) / (2 * e)
        worst = max(worst, abs(G[key][idx] - fd) / (abs(fd) + 1e-12))
    checks.append((f"backprop through RK4 matches finite differences for all four weight groups (worst relative gap {worst:.1e})", worst < 1e-5))
    checks.append(("the network has 62 parameters at width 12", L.n_params(L.init_params(12)) == 62))
    good = {k: v.copy() for k, v in P.items()}
    tg = L.rollout(good, x0, L.DT, 3)[1:]
    l0, g0 = L.rollout_loss_grad(good, x0, L.DT, tg)
    checks.append(("edge: when the rollout equals the targets, loss and gradients are zero",
                   l0 == 0 and all(float(np.abs(v).max()) == 0 for v in g0.values())))

    # --- RK4 itself against the exact flow
    xe = L.rk4_step(L.true_field, np.array([[1.0, 0.0]]), 0.1)[0]
    ex = L.exact_flow(np.array([[1.0, 0.0]]), 0.1)[0]
    checks.append(("RK4 with the true field: one step of 0.1 s is within 1e-5 of the exact flow",
                   float(np.abs(xe - ex).max()) < 1e-5))

    # --- rollout versus one-step training
    P_roll, h_roll = L.trained(0.05, 8)
    P_one, _ = L.trained(0.05, 1)
    e_roll, e_one = L.prediction_error(P_roll, 60), L.prediction_error(P_one, 60)
    checks.append((f"rollout training: error after 6 s below 0.1 (got {e_roll[60]:.3f})", e_roll[60] < 0.1))
    checks.append((f"one-step training with the same noise is worse: {e_one[60]:.3f} is more than twice the rollout error {e_roll[60]:.3f}",
                   e_one[60] > 2 * e_roll[60]))
    checks.append(("the rollout loss goes down during training by a factor of at least 50", h_roll[0] / h_roll[-1] > 50))

    # --- validation against the known linear system
    ev = L.eigenvalues(L.jacobian_at_origin(P_roll))
    tv = L.eigenvalues(L.A_TRUE)
    checks.append((f"true eigenvalues are -0.2 +- 1.99 i (got {tv[1].real:.2f} +- {tv[1].imag:.2f} i)",
                   abs(tv[1].real + 0.2) < 1e-9 and abs(tv[1].imag - np.sqrt(3.96)) < 1e-9))
    checks.append((f"worked example: damping/stiffness 0.4 and 4 give lambda = -0.2 +- 1.99 i; learned {ev[1].real:.2f} +- {ev[1].imag:.2f} i is within 0.1",
                   abs(ev[1].real - tv[1].real) < 0.1 and abs(ev[1].imag - tv[1].imag) < 0.1 and abs(ev[0] - np.conj(ev[1])) < 1e-9))

    # --- sensitivity to noise and to the rollout horizon
    e_clean = L.prediction_error(L.trained(0.0, 8)[0], 60)[60]
    e_noisy = L.prediction_error(L.trained(0.1, 8)[0], 60)[60]
    checks.append((f"noise: error after 6 s grows from {e_clean:.3f} (no noise) to {e_noisy:.3f} (sigma 0.1), more than 3 times", e_noisy > 3 * e_clean))
    checks.append(("noise: sigma 0.05 gives a smaller error than sigma 0.1", e_roll[60] < e_noisy))
    e1, e3 = L.prediction_error(L.trained(0.05, 1)[0], 60)[60], L.prediction_error(L.trained(0.05, 3)[0], 60)[60]
    checks.append((f"horizon: m = 1 gives {e1:.3f} after 6 s, over twice the {e3:.3f} of m = 3; m = 8 ({e_roll[60]:.3f}) is no worse than m = 3", e1 > 2 * e3 and e_roll[60] <= 1.1 * e3))

    # --- failure cases
    checks.append(("stiff: for z = lambda h = -10 RK4 multiplies by exactly 291 each step", abs(L.rk4_amplification(-10.0) - 291.0) < 1e-9))
    checks.append((f"stiff: the stability limit on the negative real axis is |z| = 2.785 (got {L.stable_limit():.4f})", abs(L.stable_limit() - 2.7853) < 1e-3))
    checks.append(("stiff: lambda = -1000 with h = 0.01 blows up (value above 1e10 after 0.1 s)", abs(L.decay_with_rk4(-1000.0, 0.01, 0.1)) > 1e10))
    checks.append(("stiff: with h = 0.002 (z = -2) the same problem decays to under 1e-6", abs(L.decay_with_rk4(-1000.0, 0.002, 0.1)) < 1e-6))
    checks.append(("stiff: with h = 0.002 (z = -2) each step multiplies by exactly 1/3", abs(L.rk4_amplification(-2.0) - 1.0 / 3.0) < 1e-12))
    checks.append(("hand calculation: for lambda = -500 the largest stable step is 2.7853 / 500 = 0.00557 s", abs(L.stable_limit() / 500.0 - 0.00557) < 1e-5))
    checks.append(("edge: z = 0 gives amplification exactly 1", L.rk4_amplification(0.0) == 1.0))
    inside = L.prediction_error(P_roll, 30, box=1.5)[30]
    outside = L.prediction_error(P_roll, 30, box=3.0)[30]
    checks.append((f"extrapolation: error after 3 s is {inside:.3f} inside the training box but {outside:.2f} when starts are twice as far out (over 10 times worse)", outside > 10 * inside))
    tr_loss, truth_loss, ov_err = L.overfit_demo()
    checks.append((f"overfitting: training loss {tr_loss:.4f} is below the true system's loss {truth_loss:.4f} on the same noisy data", tr_loss < 0.5 * truth_loss))
    checks.append((f"overfitting: yet the test error after 3 s is {ov_err:.2f}, more than 5 times the {inside:.3f} of the well-fed model", ov_err > 5 * inside))

    # --- design: how much data at noise 0.1
    d_small, d_big = L.design_error(6, 0.1), L.design_error(18, 0.1)
    checks.append((f"design: at noise 0.1, 6 runs can leave the error after 6 s above 0.1 (worst of two data sets {d_small:.3f})", d_small > 0.1))
    checks.append((f"design: at noise 0.1, 18 runs keep the error after 6 s below 0.1 (worst of two data sets {d_big:.3f})", d_big < 0.1))

    # --- mini-project: damped pendulum
    Pp, _ = L.pendulum_model()
    e_nn = L.pendulum_angle_error(lambda z: L.field(Pp, z))
    e_lin = L.pendulum_angle_error(L.small_angle_field)
    checks.append((f"mini-project: Neural ODE angle error after 6 s is below 0.1 rad (got {e_nn[60]:.3f})", e_nn[60] < 0.1))
    checks.append((f"mini-project: the small-angle linear model is over 3 times worse (got {e_lin[60]:.3f} rad)", e_lin[60] > 3 * e_nn[60]))
    checks.append(("pendulum field at rest and at the bottom is zero", float(np.abs(L.pendulum_field(np.zeros((1, 2)))).max()) == 0.0))
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
