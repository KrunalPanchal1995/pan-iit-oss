"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    d_t, d_xx = L.derivative_check()
    checks.append((f"u_t formula matches a finite difference (gap {d_t:.1e})", d_t < 1e-6))
    checks.append((f"u_xx formula matches a finite difference (gap {d_xx:.1e})", d_xx < 1e-5))
    gap = L.gradient_check()
    checks.append((f"hand-coded parameter gradients match finite differences (gap {gap:.1e})", gap < 1e-6))

    # exact solution: hand calculations
    checks.append(("worked example: exact u(0.5, 1) = exp(-0.1 pi^2) = 0.3727", abs(float(L.exact(0.5, 1.0)) - 0.3727) < 5e-5))
    t_half = np.log(2) / (L.ALPHA * np.pi ** 2)
    checks.append(("half-life ln 2 / (alpha pi^2) = 0.702 and the exact amplitude is 0.5 there",
                   abs(t_half - 0.702) < 5e-4 and abs(float(L.exact(0.5, t_half)) - 0.5) < 1e-12))
    h = 1e-4
    x0, t0 = 0.37, 0.4
    ut = (L.exact(x0, t0 + h) - L.exact(x0, t0 - h)) / (2 * h)
    uxx = (L.exact(x0 + h, t0) - 2 * L.exact(x0, t0) + L.exact(x0 - h, t0)) / h ** 2
    checks.append(("the exact solution has zero residual u_t - alpha u_xx", abs(ut - L.ALPHA * uxx) < 1e-5))
    checks.append(("edge: exact solution is 0 at both ends and sin(pi x) at t = 0",
                   abs(float(L.exact(0.0, 0.7))) < 1e-15 and abs(float(L.exact(1.0, 0.7))) < 1e-12 and abs(float(L.exact(0.25, 0.0)) - np.sin(np.pi / 4)) < 1e-15))

    checks.append(("hand calculation: with alpha = 0.2 the amplitude at t = 1 is exp(-0.2 pi^2) = 0.1389; r = 0.1 * 0.01 / 0.05^2 = 0.4",
                   abs(float(L.exact(0.5, 1.0, 0.2)) - 0.1389) < 5e-5 and abs(L.ALPHA * 0.01 / 0.05 ** 2 - 0.4) < 1e-12))

    # main run
    P, _, hist = L.train_pinn()
    err = L.rel_l2_error(P)
    checks.append((f"worked example: PINN relative L2 error is below 0.02 (got {err:.4f})", err < 0.02))
    u_net = float(L.forward(P, np.array([0.5]), np.array([1.0]))[0][0])
    checks.append((f"network value at (0.5, 1) is within 0.01 of 0.3727 (got {u_net:.4f})", abs(u_net - 0.3727) < 0.01))
    checks.append(("all three loss pieces end below 1e-3 and the residual fell by 50x and boundary and initial by 1000x",
                   max(hist["residual"][-1], hist["boundary"][-1], hist["initial"][-1]) < 1e-3 and hist["residual"][0] > 50 * hist["residual"][-1] and hist["boundary"][0] > 1000 * hist["boundary"][-1] and hist["initial"][0] > 1000 * hist["initial"][-1]))

    # classical reference
    e_fd = L.fd_error()
    e_pinn_t1 = L.pinn_error_at_time(P)
    checks.append((f"finite differences (20 intervals, r = 0.4) error at t = 1 is below 0.005 (got {e_fd:.5f})", e_fd < 0.005))
    checks.append((f"the PINN is less accurate than finite differences at t = 1 ({e_pinn_t1:.3f} vs {e_fd:.5f})", e_pinn_t1 > 5 * e_fd))
    _, _, n_steps, dt = L.fd_heat()
    fd_updates = n_steps * 19
    pinn_evals = 1000 * (200 + 100 + 50) * 20
    checks.append((f"work: finite differences 100 steps x 19 nodes = {fd_updates} updates; PINN {pinn_evals} unit evaluations (over 1000 times more)",
                   n_steps == 100 and abs(dt - 0.01) < 1e-12 and pinn_evals > 1000 * fd_updates))
    _, u_stable, _, _ = L.fd_heat(noise=1e-3)
    _, u_bad, _, _ = L.fd_heat(r=0.6, noise=1e-3)
    checks.append((f"stability: r = 0.4 stays below 1 while r = 0.6 reaches {np.abs(u_bad).max():.1e}", np.abs(u_stable).max() < 1 and np.abs(u_bad).max() > 1e3))

    # sensitivity and failure cases
    e = {}
    for key, kw in (("w001", dict(w_res=0.01)), ("w100", dict(w_res=100.0)), ("n5", dict(n_col=5)), ("n20", dict(n_col=20))):
        e[key] = L.rel_l2_error(L.train_pinn(**kw)[0])
    checks.append((f"weight of physics term: 0.01 gives {e['w001']:.3f}, 1 gives {err:.3f}, 100 gives {e['w100']:.3f}; both extremes are worse",
                   e["w001"] > 0.1 and e["w100"] > 0.05 and err < e["w001"] and err < e["w100"]))
    checks.append((f"too few collocation points: N = 5 gives {e['n5']:.3f} (above 0.15); N = 20 gives {e['n20']:.3f} (below 0.03)", e["n5"] > 0.15 and e["n20"] < 0.03))
    Pk, _, _ = L.train_pinn(k=3, steps=1500)
    e_k3 = L.rel_l2_error(Pk, k=3)
    checks.append((f"spectral bias: a start of sin(3 pi x) gives error {e_k3:.2f}, above 0.3 (sin(pi x) gave {err:.3f})", e_k3 > 0.3))

    # inverse problem
    readings = L.make_readings()
    Pi, a_fin, hi = L.train_pinn(readings=readings, alpha_start=0.3, steps=2000)
    checks.append((f"inverse: alpha recovered {a_fin:.3f} from a start of 0.3, within 5 percent of 0.1", abs(a_fin - 0.1) < 0.005 and hi["alpha"][0] == 0.3))
    a_dir = L.fit_alpha_direct(readings)
    checks.append((f"classical direct fit of alpha is {a_dir:.3f}, also within 5 percent (noise limits both)", abs(a_dir - 0.1) < 0.005))
    checks.append(("roadmap: the shipped inverse run misses the truth by more than 2 percent", abs(a_fin - 0.1) / 0.1 > 0.02))

    # mini-project: true alpha 0.15, start 0.5, 30 readings with noise 0.02
    R = L.make_readings(0.15, 30, 0.02, 0)
    Pm, a_m, hm = L.train_pinn(alpha=0.0, readings=R, alpha_start=0.5, steps=2000)
    rel = np.abs(np.array(hm["alpha"]) - 0.15) / 0.15
    steps = np.array(hm["step"])
    first_pass = int(steps[np.argmax(rel < 0.1)])
    settle = int(steps[max(i for i in range(len(rel)) if rel[i] >= 0.1) + 1])
    checks.append((f"mini-project: alpha is first within 10 percent at step {first_pass} (a false alarm) but settles only from step {settle}",
                   first_pass == 200 and settle == 1200))
    checks.append((f"mini-project: final alpha {a_m:.3f} is within 10 percent of 0.15; direct fit {L.fit_alpha_direct(R):.3f}",
                   abs(a_m - 0.15) / 0.15 < 0.1 and abs(L.fit_alpha_direct(R) - 0.15) / 0.15 < 0.05))

    # roadmap: shipped boundary values are not exactly zero
    g = np.linspace(0, 1, 51)
    edge = max(np.abs(L.forward(P, np.zeros_like(g), g)[0]).max(), np.abs(L.forward(P, np.ones_like(g), g)[0]).max())
    checks.append((f"roadmap: the shipped network only approximates the end temperatures (largest |u| at an end {edge:.3f}, above 0.01)", edge > 0.01))
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
