"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    exact_d, exact_i = np.cos(1.0), np.e - 1.0
    # worked example: sin at x = 1, h = 0.1 and e^x on [0, 1], n = 4
    ef = L.forward_diff(np.sin, 1.0, 0.1) - exact_d
    ec = L.central_diff(np.sin, 1.0, 0.1) - exact_d
    checks.append((f"worked example: forward error {ef:.4f} (about -0.0429), central error {ec:.5f} (about -0.0009)",
                   abs(ef + 0.04294) < 1e-4 and abs(ec + 0.00090) < 1e-5))
    et = L.trapezoid(np.exp, 0, 1, 4) - exact_i
    es = L.simpson(np.exp, 0, 1, 4) - exact_i
    checks.append((f"worked example: trapezoid n = 4 gives 1.7272, Simpson n = 4 gives 1.71832 (errors {et:.5f}, {es:.6f})",
                   abs(L.trapezoid(np.exp, 0, 1, 4) - 1.727222) < 1e-5 and abs(L.simpson(np.exp, 0, 1, 4) - 1.718319) < 1e-5))
    # hand calculations
    checks.append(("trapezoid is exact for a straight line", abs(L.trapezoid(lambda x: 3 * x + 1, 0, 2, 5) - 8.0) < 1e-12))
    checks.append(("Simpson is exact for a cubic (x^3 on [0, 1] is 0.25)", abs(L.simpson(lambda x: x ** 3, 0, 1, 2) - 0.25) < 1e-12))
    checks.append(("central difference is exact for a parabola", abs(L.central_diff(lambda x: x ** 2, 3.0, 0.5) - 6.0) < 1e-12))
    # orders
    hs = np.array([0.1, 0.05, 0.025, 0.0125])
    of = L.observed_order(hs, np.abs(L.forward_diff(np.sin, 1.0, hs) - exact_d))
    oc = L.observed_order(hs, np.abs(L.central_diff(np.sin, 1.0, hs) - exact_d))
    checks.append((f"orders of forward and central differences are 1 and 2 (got {of:.2f}, {oc:.2f})", abs(of - 1) < 0.05 and abs(oc - 2) < 0.05))
    ns = np.array([2, 4, 8, 16])
    ot = L.observed_order(1.0 / ns, [abs(L.trapezoid(np.exp, 0, 1, n) - exact_i) for n in ns])
    os_ = L.observed_order(1.0 / ns, [abs(L.simpson(np.exp, 0, 1, n) - exact_i) for n in ns])
    checks.append((f"orders of trapezoid and Simpson are 2 and 4 (got {ot:.2f}, {os_:.2f})", abs(ot - 2) < 0.1 and abs(os_ - 4) < 0.2))
    # round-off limit
    e_best = abs(L.central_diff(np.sin, 1.0, 1e-5) - exact_d)
    e_tiny = abs(L.central_diff(np.sin, 1.0, 1e-15) - exact_d)
    checks.append(("round-off: a tiny step (1e-15) is worse than a moderate one (1e-5)", e_tiny > 1000 * e_best))
    # adaptive
    val, evals = L.adaptive_simpson(L.peak, 0.0, 1.0, 1e-8)
    checks.append(("adaptive Simpson finds the narrow peak area to 1e-7", abs(val - L.peak_exact()) < 1e-7))
    checks.append(("adaptive Simpson uses fewer evaluations than uniform Simpson (513)", evals < 513))
    # failure cases
    checks.append(("failure: 10-slice trapezoid misses the spike (error above 99 percent)", abs(L.trapezoid(L.peak, 0, 1, 10) - L.peak_exact()) > 0.99 * L.peak_exact()))
    checks.append(("failure: central difference of |x| at 0 says 0, but left slope is -1 and right slope is +1",
                   L.central_diff(np.abs, 0.0, 1e-3) == 0.0 and L.forward_diff(np.abs, 0.0, 1e-3) == 1.0))
    ns_k = np.array([6, 12, 24, 48, 96])
    ek = [abs(L.simpson(lambda x: np.abs(x - L.KINK), 0, 1, n) - L.kink_exact()) for n in ns_k]
    ok_k = L.observed_order(1.0 / ns_k, ek)
    checks.append((f"failure: Simpson falls to order about 2 on a kink (got {ok_k:.2f})", 1.5 < ok_k < 2.6))
    try:
        L.simpson(np.exp, 0, 1, 5)
        odd_ok = False
    except ValueError:
        odd_ok = True
    checks.append(("Simpson refuses an odd number of slices", odd_ok))
    # speedometer log
    t, v = L.speedometer_log()
    d_raw = L.integrate_log(t, v)
    checks.append(("integrating the log: about 2 percent too high (calibration error)", 0.01 < d_raw / float(L.true_distance(60.0)) - 1 < 0.03))
    checks.append(("true distance at 60 s is 821.9 m", abs(float(L.true_distance(60.0)) - 821.86) < 0.01))
    # mini-project reference numbers (seed 4, the default of speedometer_log)
    k30 = t <= 30 + 1e-9
    d30, true30 = L.integrate_log(t[k30], v[k30]), float(L.true_distance(30.0))
    scale = 822.0 / d_raw
    checks.append(("mini-project: raw distance at 30 s is 2.6 percent too high", abs(100 * (d30 / true30 - 1) - 2.6) < 0.1))
    checks.append(("mini-project: calibrated with 822 m the 30 s distance is within 1 percent (0.54)", abs(100 * (scale * d30 / true30 - 1) - 0.54) < 0.05))
    a_true = 8.0 * 2 * np.pi / 40.0 * np.cos(2 * np.pi * t / 40.0)
    rms = {}
    for w in (1, 21):
        vs = np.convolve(v * scale, np.ones(w) / w, mode="same")
        a = np.gradient(vs, t)
        rms[w] = float(np.sqrt(np.mean((a[25:-25] - a_true[25:-25]) ** 2)))
    checks.append((f"mini-project: plain differencing RMS {rms[1]:.2f} (about 5.4), 21-sample smoothing {rms[21]:.2f} (about 0.37) m/s^2",
                   abs(rms[1] - 5.4) < 0.1 and abs(rms[21] - 0.37) < 0.02))
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
