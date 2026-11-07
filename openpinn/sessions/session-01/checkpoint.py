"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    F, D = L.features(np.array([0.0, 1.0]), 4)
    checks.append(("features: shape is (points, units + 1) and the last column is 1", F.shape == (2, 5) and bool(np.all(F[:, -1] == 1.0))))
    # tanh passes through 0 at its centre (unit 1 is centred at x = 0)
    checks.append(("a tanh bump is 0 at its own centre", abs(F[0, 0]) < 1e-12))
    # slope of each bump against a finite difference
    x = np.array([0.3, 0.9, 1.4])
    h = 1e-6
    Fp, _ = L.features(x + h, 5)
    Fm, _ = L.features(x - h, 5)
    _, D = L.features(x, 5)
    checks.append(("hand-written bump slope matches a finite difference", np.allclose((Fp - Fm) / (2 * h), D, atol=1e-6)))

    c_plain, c_law = L.fit(12, 0.0), L.fit(12, 1.0)
    # worked example: the numbers quoted in Section E
    e_plain, e_law = L.rms_error(c_plain), L.rms_error(c_law)
    checks.append((f"worked example: data-only fit has rms error above 0.5 over 0..2 (got {e_plain:.3f})", e_plain > 0.5))
    checks.append((f"worked example: fit with the law has rms error below 0.001 (got {e_law:.4f})", e_law < 1e-3))
    xs = np.linspace(0, 2, 201)
    rp, rl = np.abs(L.law_residual(c_plain, xs)).max(), np.abs(L.law_residual(c_law, xs)).max()
    checks.append((f"largest |u' + u| is above 2 without the law and below 0.03 with it (got {rp:.2f}, {rl:.3f})", rp > 2.0 and rl < 0.03))

    # the data-only fit still passes close to the six readings
    F6, _ = L.features(L.DATA_X, 12)
    checks.append(("data-only fit passes within 0.05 of every reading", bool(np.abs(F6 @ c_plain - L.DATA_Y).max() < 0.05)))
    # hand calculation of the readings: exp(-0.4) + 0.025
    checks.append(("hand calculation: reading at x = 0.4 is exp(-0.4) + 0.025 = 0.695", abs(L.DATA_Y[2] - 0.695) < 1e-3))
    # edge: lam = 0 is exactly the data-only fit; one unit still works
    checks.append(("edge: lam = 0 gives the same weights as the data-only fit", np.allclose(L.fit(6, 0.0), L.fit(6, 0.0)) and L.fit(1, 1.0).shape == (2,)))
    # the law fit with 6 bumps beats the data-only fit, and too strong a law with only 3 bumps hurts
    checks.append(("6 bumps with law (lam 1) beat 6 bumps without", L.rms_error(L.fit(6, 1.0)) < 0.1 * L.rms_error(L.fit(6, 0.0))))
    checks.append(("trade-off: 3 bumps cannot obey the law well (error stays above 0.05 for lam 1)", L.rms_error(L.fit(3, 1.0)) > 0.05))
    checks.append(("too strong a law (lam 50) with 6 bumps is worse than lam 1", L.rms_error(L.fit(6, 50.0)) > L.rms_error(L.fit(6, 1.0))))
    # app challenge region
    checks.append(("app challenge: 6 to 16 bumps with lam 0.5 to 5 give rms below 0.01",
                   all(L.rms_error(L.fit(n, lam)) < 0.01 for n in (6, 8, 12, 16) for lam in (0.5, 1.0, 2.0, 5.0))))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
