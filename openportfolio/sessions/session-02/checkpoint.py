"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    r = L.simulate_returns(100000, 0.3)
    checks.append(("the simulation is repeatable for a given seed", np.array_equal(r, L.simulate_returns(100000, 0.3))))
    m1, s1 = L.mean_std(r[:, 0])
    m2, s2 = L.mean_std(r[:, 1])
    checks.append((f"sample mean/std of asset 1 are 0.0997 / 0.1997 and of asset 2 are 0.0603 / 0.1001 (got {m1:.4f} {s1:.4f} {m2:.4f} {s2:.4f})",
                   abs(m1 - 0.0997) < 5e-5 and abs(s1 - 0.1997) < 5e-5 and abs(m2 - 0.0603) < 5e-5 and abs(s2 - 0.1001) < 5e-5))
    checks.append(("sample means and stds are close to the stated 10%/20% and 6%/10% (within 0.5 percentage points)",
                   abs(m1 - 0.10) < 0.005 and abs(s1 - 0.20) < 0.005 and abs(m2 - 0.06) < 0.005 and abs(s2 - 0.10) < 0.005))
    c = float(np.corrcoef(r.T)[0, 1])
    checks.append((f"sample correlation is 0.3027, close to rho = 0.3 (got {c:.4f})", abs(c - 0.3027) < 5e-5 and abs(c - 0.3) < 0.01))

    # worked example: w = 0.5, rho = 0.3 -> return 8%, variance 0.0155, std 12.45%
    w, rho = 0.5, 0.3
    var_hand = 0.25 * 0.04 + 0.25 * 0.01 + 2 * 0.25 * 0.3 * 0.02
    checks.append(("worked example: w = 0.5, rho = 0.3 gives return 0.0800, variance 0.0155 and std 0.1245",
                   abs(L.port_return(w) - 0.08) < 1e-12 and abs(L.port_var(w, rho) - 0.0155) < 1e-12
                   and abs(var_hand - 0.0155) < 1e-12 and abs(L.port_std(w, rho) - 0.1245) < 5e-5))
    # the formula is an exact identity with sample statistics, and close to the stated parameters
    ok_exact, ok_close = True, True
    for w in (0.0, 0.25, 0.5, 0.8, 1.0):
        pm, pv = L.sampled_portfolio(r, w)
        v1, v2 = np.var(r[:, 0]), np.var(r[:, 1])
        cov = np.cov(r.T, bias=True)[0, 1]
        ident = w ** 2 * v1 + (1 - w) ** 2 * v2 + 2 * w * (1 - w) * cov
        ok_exact &= abs(ident - pv) < 1e-12
        ok_close &= abs(pv - L.port_var(w, 0.3)) / L.port_var(w, 0.3) < 0.02 and abs(pm - L.port_return(w)) < 0.005
    checks.append(("sampled portfolio variance equals the formula built from sample variances and covariance (exact identity)", ok_exact))
    checks.append(("sampled portfolio mean/variance match the formula within 0.5 points and 2 percent", ok_close))
    pm, pv = L.sampled_portfolio(r, 0.5)
    checks.append((f"sampled w = 0.5 portfolio: return 0.0800 and std 0.1245 (got {pm:.4f}, {np.sqrt(pv):.4f})",
                   abs(pm - 0.0800) < 5e-5 and abs(np.sqrt(pv) - 0.1245) < 5e-5))

    # edge: all in one asset reproduces that asset
    checks.append(("edge: w = 1 gives asset 1 (return 0.10, std 0.20) and w = 0 gives asset 2 (0.06, 0.10)",
                   abs(L.port_std(1.0, 0.3) - 0.2) < 1e-12 and abs(L.port_std(0.0, 0.3) - 0.1) < 1e-12
                   and L.port_return(1.0) == 0.10 and L.port_return(0.0) == 0.06))
    # rho = 1: no benefit, std is the weighted average of the stds
    ws = np.linspace(0, 1, 11)
    checks.append(("rho = 1: risk is the weighted average of the two risks (no benefit)",
                   np.allclose(L.port_std(ws, 1.0), ws * 0.2 + (1 - ws) * 0.1, atol=1e-12)))
    checks.append(("lower rho never raises the risk: std(rho=1) >= std(0.3) >= std(0) >= std(-1) for every w",
                   all(a >= b - 1e-12 >= c - 1e-12 >= d - 1e-12 for a, b, c, d in zip(*[L.port_std(ws, q) for q in (1.0, 0.3, 0.0, -1.0)]))))
    # rho = -1: zero variance at w = s2 / (s1 + s2) = 1/3
    wz = L.zero_variance_weight()
    checks.append(("rho = -1: the weight s2/(s1+s2) = 1/3 gives zero variance", abs(wz - 1 / 3) < 1e-12 and L.port_var(wz, -1.0) < 1e-15))
    checks.append(("rho = -1: the zero-variance mix still earns 0.0733 (= 1/3 * 0.10 + 2/3 * 0.06)", abs(L.port_return(wz) - 0.0733333333) < 1e-9))
    # minimum variance weight: formula vs scan
    ok = all(abs(L.min_var_weight(q) - L.scan_min_var_weight(q)) < 1e-4 for q in (0.0, 0.3, -0.5, -1.0))
    checks.append(("minimum-variance weight w* matches a scan of 100001 weights for rho = 0, 0.3, -0.5, -1", ok))
    checks.append(("w* is 0.2000 at rho = 0, 0.1053 at rho = 0.3, 0.2857 at rho = -0.5",
                   abs(L.min_var_weight(0.0) - 0.2) < 5e-5 and abs(L.min_var_weight(0.3) - 0.1053) < 5e-5
                   and abs(L.min_var_weight(-0.5) - 0.2857) < 5e-5))
    checks.append(("risk at w* is 0.0894 (rho = 0), 0.0979 (rho = 0.3), 0.0655 (rho = -0.5)",
                   abs(L.port_std(L.min_var_weight(0.0), 0.0) - 0.0894) < 5e-5
                   and abs(L.port_std(L.min_var_weight(0.3), 0.3) - 0.0979) < 5e-5
                   and abs(L.port_std(L.min_var_weight(-0.5), -0.5) - 0.0655) < 5e-5))
    checks.append(("at rho = 0 the minimum-risk mix (w = 0.2) earns 0.068 with variance 0.008",
                   abs(L.port_return(0.2) - 0.068) < 1e-12 and abs(L.port_var(0.2, 0.0) - 0.008) < 1e-12))
    checks.append(("edge: equal risks s1 = s2 give w* = 0.5 whatever rho", all(abs(L.min_var_weight(q, 0.15, 0.15) - 0.5) < 1e-12 for q in (-0.9, 0.0, 0.7))))
    checks.append(("edge: rho = 1 gives w* = -1 (outside 0..1), so within 0..1 the safest is all asset 2 (std 0.10)",
                   abs(L.min_var_weight(1.0) + 1.0) < 1e-12 and abs(L.scan_min_var_weight(1.0)) < 1e-12))
    # design problem
    wd = L.weight_for_return(0.07)
    checks.append(("design: a 7% target return needs w = 0.25; at rho = 0.3 its risk is 0.1019",
                   abs(wd - 0.25) < 1e-12 and abs(L.port_std(wd, 0.3) - 0.1019) < 5e-5))
    rmax = L.max_rho_for_risk(0.5, 0.11)
    checks.append(("design: an 8% return (w = 0.5) with risk at most 11% needs rho <= -0.04",
                   abs(rmax + 0.04) < 1e-9 and abs(L.port_std(0.5, rmax) - 0.11) < 1e-9))
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
