"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    t = np.linspace(0, 10, 101)
    a, b, c = L.exact(t, 0.5, 1.5)
    checks.append(("amounts add up to 1 at all times", bool(np.allclose(a + b + c, 1.0))))
    checks.append(("start: A = 1, B = 0, C = 0", a[0] == 1.0 and b[0] == 0.0 and c[0] == 0.0))
    checks.append(("A, B, C never negative", bool(a.min() >= 0 and b.min() >= -1e-12 and c.min() >= -1e-12)))

    # worked example: k1 = 0.5, k2 = 1.5 -> peak at ln(3) / 1 = 1.0986 s, B = (1/3)^1.5 = 0.19245
    tp = L.peak_time(0.5, 1.5)
    bp = float(L.exact(tp, 0.5, 1.5)[1])
    checks.append((f"worked example: B peaks at ln 3 = 1.0986 s (got {tp:.4f}) with B = 0.1925 (got {bp:.4f})",
                   abs(tp - np.log(3)) < 1e-9 and abs(bp - (1 / 3) ** 1.5) < 1e-9))
    # hand calculation at t = 1: B = 0.5 / 1.0 * (exp(-0.5) - exp(-1.5)) = 0.1917
    checks.append(("hand calculation: B(1 s) = 0.5 (e^-0.5 - e^-1.5) = 0.1917",
                   abs(float(L.exact(1.0, 0.5, 1.5)[1]) - 0.5 * (np.exp(-0.5) - np.exp(-1.5))) < 1e-12
                   and abs(float(L.exact(1.0, 0.5, 1.5)[1]) - 0.1917) < 1e-4))
    # Euler gets better with smaller steps
    errs = []
    for dt in (0.5, 0.1, 0.01):
        te, y = L.euler(0.5, 1.5, dt, 8.0)
        errs.append(np.abs(y[:, 1] - L.exact(te, 0.5, 1.5)[1]).max())
    checks.append(("Euler error shrinks as dt shrinks", errs[0] > errs[1] > errs[2]))
    checks.append(("Euler with dt = 0.01 is within 0.005 mol/L", errs[2] < 0.005))
    te, y = L.euler(0.5, 1.5, 0.1, 5.0)
    checks.append(("Euler also conserves A + B + C = 1", bool(np.allclose(y.sum(axis=1), 1.0))))
    # edge case: k1 == k2 has its own formula; B = k t exp(-k t), peak at 1/k
    kk = 0.8
    checks.append(("edge: k1 = k2 peak time is 1/k and B is finite",
                   abs(L.peak_time(kk, kk) - 1 / kk) < 1e-12 and bool(np.isfinite(L.exact(1 / kk, kk, kk)[1]))))
    nearly = float(L.exact(1.0, 0.8, 0.8 + 1e-6)[1])
    checks.append(("edge: k2 very close to k1 agrees with the k1 = k2 formula", abs(nearly - float(L.exact(1.0, 0.8, 0.8)[1])) < 1e-4))
    # an experiment tells right from wrong
    times = np.array([0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0])
    meas = L.pretend_experiment(0.5, 1.5, times)
    checks.append(("misfit is small for the true rate constants and large for wrong ones",
                   L.misfit(0.5, 1.5, times, meas) < 0.02 and L.misfit(1.0, 0.5, times, meas) > 0.05))
    # exercise answers used in the text: k1 = 0.4, k2 = 0.8 peaks at ln 2 / 0.4 = 1.733 s with B = 0.25
    tp2 = L.peak_time(0.4, 0.8)
    checks.append(("k1 = 0.4, k2 = 0.8: B peaks at 1.733 s with B = 0.25",
                   abs(tp2 - np.log(2) / 0.4) < 1e-12 and abs(float(L.exact(tp2, 0.4, 0.8)[1]) - 0.25) < 1e-12))
    # swapping k1 and k2 multiplies B by k2/k1 at every time, and the peak time stays the same
    tt = np.linspace(0.1, 6, 30)
    checks.append(("swapping k1 and k2 makes B exactly 3 times larger (k2/k1 = 3) with the same peak time",
                   bool(np.allclose(L.exact(tt, 1.5, 0.5)[1], 3 * L.exact(tt, 0.5, 1.5)[1])) and abs(L.peak_time(1.5, 0.5) - L.peak_time(0.5, 1.5)) < 1e-12))
    # at the peak of B: dB/dt = 0, i.e. k1 A = k2 B
    a_p, b_p, _ = L.exact(tp, 0.5, 1.5)
    checks.append(("at the peak of B the gain k1 A equals the loss k2 B", abs(0.5 * float(a_p) - 1.5 * float(b_p)) < 1e-9))
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
