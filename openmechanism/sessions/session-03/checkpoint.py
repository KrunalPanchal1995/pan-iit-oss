"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # Arrhenius factor by hand: k2(900 K) = 30 * exp(-60000 / 8.314462618 * (1/900 - 1/1000))
    k900 = float(L.rate_constants(900.0)[1])
    hand = 30.0 * np.exp(-60000.0 / 8.314462618 * (1 / 900 - 1 / 1000))
    checks.append((f"hand calculation: k2 at 900 K = {hand:.3f} L/(mol s) (got {k900:.3f})", abs(k900 - hand) < 1e-9))
    checks.append(("at 1000 K the rate constants equal their reference values and scale factors multiply them",
                   bool(np.allclose(L.rate_constants(1000.0), L.K_REF)) and bool(np.allclose(L.rate_constants(1000.0, [2, 1, 1, 1])[0], 2 * L.K_REF[0]))))

    # solver validated against a formula: only k1 on -> tau = ln 2 / k1
    k1 = float(L.rate_constants(1000.0)[0])
    tau = float(L.simulate_tau(1000.0, 1.0, [1.0, 1e-12, 1e-12, 1e-12], h=0.02))
    checks.append((f"solver vs formula: tau = ln2/k1 = {np.log(2) / k1:.2f} s (got {tau:.2f})", abs(tau / (np.log(2) / k1) - 1) < 1e-3))
    # step halving converges
    t1, t2, t3 = (float(L.simulate_tau(1000.0, 1.0, h=h, max_steps=20000)) for h in (0.2, 0.1, 0.05))
    checks.append(("halving the step shrinks the change in tau (second-order behaviour)", abs(t3 - t2) < abs(t2 - t1) / 3))
    checks.append(("worked example: nominal ignition delay at 1000 K, F0 = 1 mol/L is 0.4523 s",
                   abs(float(L.simulate_tau(1000.0, 1.0)) - 0.4523) < 5e-4))
    # hotter is faster, more fuel is faster
    Ts = np.linspace(900, 1400, 8)
    taus = L.simulate_tau(Ts, 1.0)
    checks.append(("ignition delay falls as temperature rises", bool(np.all(np.diff(taus) < 0))))
    checks.append(("more starting fuel ignites sooner", bool(np.all(L.simulate_tau(Ts, 2.0) < taus))))
    # edge: no ignition when k2 F0 < k3 (radicals die faster than they are made)
    with np.errstate(all="ignore"):
        no_ign = L.simulate_tau(900.0, 1.0, [1.0, 0.1, 1.0, 1.0], max_steps=300)
    checks.append(("edge: a very slow branching step gives nan (no ignition) and a finite residual",
                   bool(np.isnan(no_ign).all()) and bool(np.isfinite(L.residuals(np.array([0.0, np.log(0.1)]), L.make_dataset(1))).all())))

    # hand calculation of a covariance: J = [[1, 0], [0, 2]] -> (J^T J)^-1 = diag(1, 0.25)
    J = np.array([[1.0, 0.0], [0.0, 2.0]])
    checks.append(("hand calculation: (J^T J)^-1 for J = diag(1, 2) is diag(1, 0.25)",
                   bool(np.allclose(np.linalg.inv(J.T @ J), np.diag([1.0, 0.25])))))

    # noise-free data: the fit must recover the truth
    data = L.make_dataset(seed=1)
    exact = dict(data, ln_tau=data["clean"])
    th0, _ = L.calibrate(exact, [0.0, 0.0])
    checks.append((f"noise-free data: fit recovers the truth to 0.01 in ln s (got {np.round(th0, 4)})", bool(np.abs(th0 - L.TRUTH).max() < 0.01)))

    # noisy data: truth inside 2 sigma, ellipse formula, weights
    th, path = L.calibrate(data, [0.0, 0.0])
    cov = L.covariance(th, data)
    z = (th - L.TRUTH) / np.sqrt(np.diag(cov))
    checks.append((f"worked example: with noisy data the fit is within 2 sigma of the truth (z = {np.round(z, 2)})", bool(np.abs(z).max() < 2.0)))
    checks.append(("the fit is much better than the nominal mechanism",
                   float(np.sum(L.residuals(th, data) ** 2)) < 0.1 * float(np.sum(L.residuals(np.zeros(2), data) ** 2))))
    checks.append(("ln s1 is much less certain than ln s2, and they are strongly correlated",
                   bool(np.sqrt(cov[0, 0]) > 5 * np.sqrt(cov[1, 1])) and abs(cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])) > 0.9))
    e = L.ellipse_points(th, cov, 1.0, 50) - th
    q = np.einsum("ij,jk,ik->i", e, np.linalg.inv(cov), e)
    checks.append(("every point of the 1-sigma ellipse satisfies d^T Cov^-1 d = 1", bool(np.allclose(q, 1.0))))
    checks.append(("reduced chi-square is of order 1 (0.2 to 3)", 0.2 < L.reduced_chi2(th, data) < 3.0))
    # the start does not matter here
    th_b, _ = L.calibrate(data, [0.7, -0.7])
    checks.append(("a different starting guess reaches the same fit", bool(np.abs(th_b - th).max() < 1e-3)))
    # power-mean weights: dataset of 8 points vs dataset of 4 points, p = 2 -> weight per point 1/8 and 1/4
    r = np.ones(12)
    w = L.weights_power_mean(r, data["group"], 2)
    checks.append(("power-mean p = 2 gives each dataset equal total weight", abs(w[:8].sum() - w[8:].sum()) < 1e-9))
    # the Session 2 formula is a decent but imperfect approximation (6 to 9 percent too short)
    Tq = np.linspace(900, 1400, 6)
    ratio = L.tau_linearised(Tq, 1.0) / L.simulate_tau(Tq, 1.0)
    checks.append(("the linearised formula is 5 to 10 percent shorter than the full solution", bool(np.all((ratio > 0.90) & (ratio < 0.95)))))
    # design: replicate everything -> sigma halves; spread temperatures -> smaller uncertainty than the shipped design
    rep = {k: (np.tile(v, 4) if isinstance(v, np.ndarray) else v) for k, v in data.items()}
    sd1 = np.sqrt(np.diag(L.covariance(L.TRUTH, data)))
    sd4 = np.sqrt(np.diag(L.covariance(L.TRUTH, rep)))
    checks.append(("replicating every experiment 4 times halves the predicted uncertainty", bool(np.allclose(sd4, sd1 / 2, rtol=1e-3))))
    Tends = np.array([900.0] * 6 + [1400.0] * 6)
    ends = {"T": Tends, "F0": np.ones(12), "group": np.zeros(12, dtype=int), "sigma": np.full(12, 0.05)}
    ends["ln_tau"] = np.log(L.simulate_tau(Tends, ends["F0"], L.scales_from(L.TRUTH)))
    sd_ends = np.sqrt(np.diag(L.covariance(L.TRUTH, ends)))
    checks.append((f"design: 6 experiments at 900 K and 6 at 1400 K (F0 = 1) give ln s1 uncertainty {sd_ends[0]:.2f}, better than {sd1[0]:.2f}",
                   sd_ends[0] < 0.8 * sd1[0]))
    # mini-project data set (seed 42)
    d42 = L.make_dataset(seed=42)
    t42, _ = L.calibrate(d42, [0.0, 0.0])
    c42 = L.covariance(t42, d42)
    dl = t42 - L.TRUTH
    checks.append((f"mini-project (seed 42): k2 scale {np.exp(t42[1]):.2f} is in 1.1 to 1.4 and the truth is inside the 2-sigma ellipse",
                   1.1 < np.exp(t42[1]) < 1.4 and float(dl @ np.linalg.inv(c42) @ dl) < 6.18))
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
