"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c0 = [1.0, 0.0, 0.0]
    # A -> B only: compare with the analytic first-order solution
    S1, r1 = L.abc_network(0.5, 0.0, 0.0)
    t1, y1 = L.rk4(L.rhs(S1, r1), c0, 10.0, 0.01)
    err = float(np.abs(y1[:, 0] - np.exp(-0.5 * t1)).max())
    checks.append((f"RK4 for A -> B matches A0 exp(-k t) (error {err:.1e})", err < 1e-8))
    # full A <-> B -> C against the eigen-solution
    S, rates = L.abc_network(0.5, 0.2, 0.1)
    t, y = L.rk4(L.rhs(S, rates), c0, 30.0, 0.01)
    ex = L.exact_linear(L.linear_matrix(0.5, 0.2, 0.1), c0, t)
    checks.append(("RK4 for A <-> B -> C matches the exact eigen-solution", float(np.abs(y - ex).max()) < 1e-8))
    checks.append(("sum of A, B, C stays 1 (mass conservation)", float(np.abs(y.sum(1) - 1).max()) < 1e-12))
    checks.append(("no concentration goes negative", bool(y.min() > -1e-12)))
    checks.append(("S has columns that each conserve atoms: every column sums to zero", bool(np.allclose(S.sum(axis=0), 0))))
    # order of accuracy
    K = L.linear_matrix(0.5, 0.2, 0.1)
    e = []
    for h in (0.2, 0.1):
        th, yh = L.rk4(lambda c: K @ c, c0, 10.0, h)
        e.append(float(np.abs(yh - L.exact_linear(K, c0, th)).max()))
    checks.append((f"halving the step cuts the RK4 error about 16 times (got {e[0] / e[1]:.1f})", 12 < e[0] / e[1] < 20))
    # enzyme cycle
    te, ye = L.full_enzyme(10.0, 5.0, 1.0, 0.1, 1.0, 20.0, 0.005)
    cs = L.conserved_sums(ye)
    checks.append(("enzyme: E + ES stays 0.1 and S + ES + P stays 1.0", float(np.abs(cs[:, 0] - 0.1).max()) < 1e-12 and float(np.abs(cs[:, 1] - 1.0).max()) < 1e-12))
    checks.append(("enzyme: all four species stay non-negative", bool(ye.min() > -1e-12)))
    checks.append(("enzyme: the substrate ends up as product (P above 0.8 at 20 s)", ye[-1, 3] > 0.8))
    # worked example: Michaelis-Menten numbers
    Vmax, Km = 1.0 * 0.1, (5.0 + 1.0) / 10.0
    v1 = L.michaelis_menten(1.0, Vmax, Km)
    checks.append((f"worked example: Vmax = 0.1, Km = 0.6, so v(S = 1.0) = 0.1 / 1.6 = 0.0625 mol/(L s) (got {v1:.4f})", abs(v1 - 0.0625) < 1e-12 and abs(Km - 0.6) < 1e-12))
    checks.append(("at S = Km the rate is exactly Vmax / 2", abs(L.michaelis_menten(Km, Vmax, Km) - Vmax / 2) < 1e-15))
    i = 200   # t = 1 s
    s_now, es_now = ye[i, 1], ye[i, 2]
    checks.append(("the full model's product rate k2 [ES] at 1 s is within 2 percent of Michaelis-Menten at the same S", abs(1.0 * es_now - L.michaelis_menten(s_now, Vmax, Km)) / L.michaelis_menten(s_now, Vmax, Km) < 0.02))
    # QSSA error as a function of E0/S0
    errs = [L.qssa_error(r) for r in (0.01, 0.1, 1.0)]
    checks.append(("QSSA error grows with the enzyme-to-substrate ratio", errs[0] < errs[1] < errs[2]))
    checks.append((f"QSSA error is under 1 percent of S0 at E0/S0 = 0.01 (got {errs[0]:.4f})", errs[0] < 0.01))
    checks.append((f"QSSA is poor (over 10 percent) at E0/S0 = 1 (got {errs[2]:.3f})", errs[2] > 0.10))
    # rate-determining step
    ks = [0.8, 0.05, 0.6]
    base = L.chain_yield(ks, 10.0)
    gains = [L.chain_yield(L.speed_up_one(ks, i, 10), 10.0) for i in range(3)]
    checks.append(("chain: speeding up the slowest step (2) helps most", gains[1] > gains[0] and gains[1] > gains[2]))
    checks.append(("chain: speeding up a fast step gives under 20 percent more yield", gains[0] < 1.2 * base and gains[2] < 1.2 * base))
    checks.append(("chain: with no speed-up the yield is unchanged", abs(L.chain_yield(L.speed_up_one(ks, 1, 1.0), 10.0) - base) < 1e-15))
    checks.append(("chain: a 1000 times faster fast step still stays finite (step adapts)", bool(np.isfinite(L.chain_yield(L.speed_up_one(ks, 0, 1000), 10.0)))))
    # stiffness
    Ks = L.stiff_matrix()
    exact = L.exact_linear(Ks, c0, [2.0])[0]
    _, bad = L.explicit_rk4_linear(Ks, c0, 2.0, 1e-3)
    checks.append(("failure case: explicit RK4 with h = 1e-3 (h k = 10) blows up", not bool(np.isfinite(bad[-1]).all())))
    _, good = L.explicit_rk4_linear(Ks, c0, 2.0, 1e-4)
    checks.append(("explicit RK4 with h = 1e-4 is stable and accurate", float(np.abs(good[-1] - exact).max()) < 1e-6))
    _, be = L.backward_euler_linear(Ks, c0, 2.0, 0.05)
    checks.append(("backward Euler with h = 0.05 (40 steps) is stable, within 0.01 of exact", bool(np.isfinite(be).all()) and float(np.abs(be[-1] - exact).max()) < 0.01))
    _, be2 = L.backward_euler_linear(Ks, c0, 2.0, 0.5)
    checks.append(("backward Euler stays stable and non-negative even at h = 0.5", bool(np.isfinite(be2).all()) and be2.min() > -1e-12))
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
