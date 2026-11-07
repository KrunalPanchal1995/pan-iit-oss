"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    x, y = L.make_farm(20, 10)
    a, b = L.fit_normal(x, y)
    pf = np.polyfit(x, y, 1)
    checks.append(("normal equations agree with np.polyfit", np.allclose([b, a], pf, atol=1e-9)))
    checks.append((f"farm fit: a = 0.744, b = 0.385 (got {a:.3f}, {b:.3f})", abs(a - 0.744) < 1e-3 and abs(b - 0.3851) < 5e-4))
    x3, y3 = np.array([1.0, 2.0, 3.0]), np.array([2.0, 2.0, 5.0])
    a3, b3 = L.fit_normal(x3, y3)
    r2 = L.r_squared(y3, a3 + b3 * x3)
    checks.append(("worked example: R^2 = 1 - 1.5/6 = 0.75 for dots (1,2), (2,2), (3,5)", abs(r2 - 0.75) < 1e-9))
    checks.append(("R^2 equals the squared correlation", abs(r2 - np.corrcoef(x3, y3)[0, 1] ** 2) < 1e-9))
    checks.append(("farm data R^2 is 0.880", abs(L.r_squared(y, a + b * x) - 0.880) < 5e-4))
    checks.append(("edge: predicting the mean gives R^2 = 0", abs(L.r_squared(y, np.full_like(y, y.mean()))) < 1e-12))
    xc, yc = L.make_curved(30, 3)
    ac, bc = L.fit_normal(xc, yc)
    rc = yc - ac - bc * xc
    checks.append(("curved data: R^2 is high (0.837) yet residuals bend (curvature -0.90)",
                   abs(L.r_squared(yc, ac + bc * xc) - 0.837) < 5e-3 and abs(L.residual_curvature(xc, rc) + 0.90) < 0.01))
    checks.append(("straight data: residual curvature is small (0.05)", abs(L.residual_curvature(x, y - a - b * x)) < 0.1))
    X2, y2 = L.make_two_inputs(40, 2)
    beta, se, res = L.multi_fit(X2, y2)
    checks.append(("two inputs: normal equations hold, X^T residual = 0", np.allclose(X2.T @ res, 0, atol=1e-8)))
    checks.append(("two inputs: coefficients 0.814, 0.302, 0.115", np.allclose(beta, [0.814, 0.302, 0.115], atol=1e-3)))
    checks.append(("two inputs: true coefficients within 2 standard errors", bool(np.all(np.abs(beta - L.C_TRUE) < 2 * se))))
    checks.append(("t quantile (0.975, 18 df) = 2.101 and (0.975, 8 df) = 2.306",
                   abs(L.t_quantile(0.975, 18) - 2.101) < 1e-3 and abs(L.t_quantile(0.975, 8) - 2.306) < 1e-3))
    yh, lo, hi = L.prediction_interval(6.0, x, y)
    checks.append(("interval at 600 mm: 3.06 (2.47 to 3.64) t/ha", abs(yh - 3.06) < 0.01 and abs(lo - 2.47) < 0.01 and abs(hi - 3.64) < 0.01))
    w = [float(np.ptp(L.prediction_interval(v, x, y)[1:])) for v in (x.mean(), 9.0, 12.0)]
    checks.append(("interval is narrowest at the mean rain and widens away from the data", w[0] < w[1] < w[2]))
    cov = L.coverage()
    checks.append((f"coverage over 2000 repeats is about 95 percent (got {cov:.3f})", 0.935 <= cov <= 0.965))
    line, truth = L.extrapolation_demo()
    checks.append((f"extrapolation to 1000 mm: line says {line:.2f}, truth {truth:.2f} t/ha", abs(line - 8.08) < 0.02 and abs(truth - 5.05) < 0.01))
    pt, safe = L.rain_for_target(3.5, x, y)
    checks.append(("design: 3.5 t/ha needs 716 mm on the line but 872 mm for a 95 percent safe lower bound",
                   abs(pt - 7.155) < 0.01 and abs(safe - 8.722) < 0.01 and safe <= x.max()))
    checks.append(("question B: residuals (0.5, -1, 0.5) are perpendicular to the columns (1,1,1) and (1,2,3); prediction at x = 4 is 6.0",
                   abs(np.dot([1, 1, 1], [0.5, -1, 0.5])) < 1e-12 and abs(np.dot([1, 2, 3], [0.5, -1, 0.5])) < 1e-12 and abs(a3 + b3 * 4 - 6.0) < 1e-9))
    checks.append(("worked example: correlation of the three dots is 0.866", abs(np.corrcoef(x3, y3)[0, 1] - 0.866) < 5e-4))
    checks.append(("design: the extra rain for a safe bound is about 156 mm and both values lie inside the data (max rain above 8.72)",
                   155 <= (safe - pt) * 100 <= 158 and x.max() > 8.722))
    checks.append(("app formula: half-width 0.65 at 600 mm and 0.76 at 1100 mm for n = 20, sd 0.3; 0.449 for n = 40, sd 0.2 at 1100 mm",
                   abs(L.expected_half_width(6, 20) - 0.646) < 1e-3 and abs(L.expected_half_width(11, 20) - 0.763) < 1e-3 and abs(L.expected_half_width(11, 40, 0.2) - 0.449) < 1e-3))
    checks.append(("app t approximation matches the exact quantile (2.100 against 2.101 at 18 df)", abs(L.t_approx(18) - L.t_quantile(0.975, 18)) < 2e-3))
    h = L.coverage_hetero()
    checks.append((f"milestone baseline: with noise growing with rain this interval covers only {h:.2f} at 850 mm", abs(h - 0.84) < 0.01))
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
