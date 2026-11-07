"""Checkpoint for Session 5. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    ex = math.e - 1.0
    # hand calculations: Legendre polynomials and the small rules
    p2, dp2 = L.legendre_and_derivative(2, 0.5)
    checks.append((f"Legendre P2(0.5) = (3 x 0.25 - 1) / 2 = {p2:.3f} and P2'(0.5) = 3 x 0.5 = {dp2:.2f}", abs(p2 + 0.125) < 1e-12 and abs(dp2 - 1.5) < 1e-12))
    t2, w2 = L.gauss_legendre_nodes(2)
    t3, w3 = L.gauss_legendre_nodes(3)
    checks.append(("2-point rule: nodes +-1/sqrt(3) = +-0.577350, weights 1 and 1",
                   np.allclose(t2, [-1 / math.sqrt(3), 1 / math.sqrt(3)], atol=1e-14) and np.allclose(w2, [1, 1], atol=1e-14)))
    checks.append(("3-point rule: nodes -sqrt(0.6), 0, +sqrt(0.6) = -0.774597, 0, 0.774597; weights 5/9, 8/9, 5/9",
                   np.allclose(t3, [-math.sqrt(0.6), 0, math.sqrt(0.6)], atol=1e-14) and np.allclose(w3, [5 / 9, 8 / 9, 5 / 9], atol=1e-14)))
    g2, g3 = L.gauss_legendre(math.exp, 0.0, 1.0, 2), L.gauss_legendre(math.exp, 0.0, 1.0, 3)
    checks.append((f"worked example: 2 points give {g2:.6f} (error {g2 - ex:.1e}), 3 points give {g3:.6f} (error {g3 - ex:.1e})",
                   abs(g2 - 1.717896) < 1e-6 and abs(g3 - 1.718281) < 1e-6 and abs(abs(g2 - ex) - 3.85e-4) < 1e-5 and abs(abs(g3 - ex) - 8.24e-7) < 1e-8))
    # nodes and weights against numpy
    worst, ok = 0.0, True
    for n in range(1, 21):
        t, w = L.gauss_legendre_nodes(n)
        tn, wn = np.polynomial.legendre.leggauss(n)
        worst = max(worst, float(np.max(np.abs(t - tn))), float(np.max(np.abs(w - wn))))
        ok &= bool(np.all(np.diff(t) > 0) and np.all(np.abs(t) < 1) and np.all(w > 0) and abs(w.sum() - 2.0) < 1e-13 and np.allclose(t, -t[::-1], atol=1e-14))
    checks.append((f"nodes and weights for n = 1 ... 20: sorted, inside (-1, 1), positive weights summing to 2, symmetric, and equal to numpy's to {worst:.0e}", ok and worst < 1e-13))
    # degree of exactness
    degs = [L.exact_degree(n) for n in range(1, 9)]
    checks.append((f"the n-point rule is exact up to degree 2n - 1 (n = 1 ... 8 gives {degs}) and not beyond",
                   degs == [1, 3, 5, 7, 9, 11, 13, 15] and L.monomial_errors(3)[6] > 1e-4))
    # interval mapping
    checks.append(("any interval: x^2 on [2, 5] is 39 with 2 points", abs(L.gauss_legendre(lambda x: x * x, 2.0, 5.0, 2) - 39.0) < 1e-12))
    # counting evaluations
    calls = [0]

    def counted(x):
        calls[0] += 1
        return math.exp(x)

    L.gauss_legendre(counted, 0.0, 1.0, 5)
    checks.append((f"the 5-point rule costs {calls[0]} function values", calls[0] == 5))
    # the roadmap checkpoint
    simp5 = abs((0.25 / 3.0) * (1 + 4 * math.exp(0.25) + 2 * math.exp(0.5) + 4 * math.exp(0.75) + math.e) - ex)
    err5 = abs(L.gauss_legendre(math.exp, 0.0, 1.0, 5) - ex)
    checks.append((f"roadmap checkpoint: e^x on [0, 1] with 5 function values has error {err5:.1e} (below 1e-11); Simpson with 5 values gives {simp5:.1e}",
                   err5 < 1e-11 and 3.6e-5 < simp5 < 3.8e-5))
    err4 = abs(L.gauss_legendre(math.exp, 0.0, 1.0, 4) - ex)
    checks.append((f"4 values are not enough for the roadmap target (error {err4:.1e}, above 1e-11)", err4 > 1e-11))
    # the bell curve budget
    need = [L.gauss_values_needed(2, t) for t in (1e-6, 1e-8, 1e-10, 1e-12)]
    checks.append((f"mini-project: the bell curve needs {need} Gauss values for 1e-6, 1e-8, 1e-10, 1e-12 (Romberg needs 17, 33, 33, 65; Simpson 17, 65, 257, 513)",
                   need == [6, 7, 9, 10]))
    f2, a2, b2 = L.FUNCTIONS[2][1], L.FUNCTIONS[2][2], L.FUNCTIONS[2][3]
    stop = [L.gauss_tol(f2, a2, b2, t) for t in (1e-6, 1e-12)]
    checks.append((f"not nested: the stopping rule at 1e-6 ends at n = {stop[0][1]} after {stop[0][2]} values, and at 1e-12 at n = {stop[1][1]} after {stop[1][2]} values (the same 65 as Romberg)",
                   stop[0][1:] == (7, 27, True) and stop[1][1:] == (11, 65, True)))
    # smooth enough, fast: e^x
    checks.append(("round-off floor: 7 points on e^x are at 2e-16", L.gauss_error(1, 7) < 1e-15))
    # failure: sqrt(x)
    ns = [20, 40, 80, 160]
    ord_sqrt = L.observed_order([1.0 / n for n in ns], [L.gauss_error(3, n) for n in ns])
    checks.append((f"failure: sqrt(x) falls only like n^-3 (observed order {ord_sqrt:.2f}); 160 values give {L.gauss_error(3, 160):.1e}, not round-off",
                   2.8 < ord_sqrt < 3.2 and L.gauss_error(3, 160) > 1e-9))
    # failure: periodic
    f4, ex4 = L.FUNCTIONS[4][1], L.FUNCTIONS[4][4]
    trap17 = abs(L.trapezoid_values(f4, 0.0, 1.0, 17) - ex4)
    checks.append((f"failure: periodic function: the trapezoid rule with 17 values is at round-off ({trap17:.0e}), Gauss with 17 values has error {L.gauss_error(4, 17):.1e}",
                   trap17 < 1e-14 and L.gauss_error(4, 17) > 1e-11))
    # failure: corner and the fix
    kink_f, kink_exact = L.FUNCTIONS[5][1], L.FUNCTIONS[5][4]
    one = abs(L.gauss_legendre(kink_f, 0.0, 1.0, 10) - kink_exact)
    split = abs(L.composite_gauss(kink_f, [0.0, L.KINK, 1.0], 1) - kink_exact)
    checks.append((f"failure and fix: |x - 0.37| with one 10-point rule has error {one:.1e}; split at 0.37 with 1 point per piece (2 values) the error is {split:.0e}",
                   one > 1e-3 and split < 1e-14))
    # failure: narrow peak
    peak = lambda x: math.exp(-((x - 0.35) / 0.005) ** 2)
    peak_exact = 0.005 * math.sqrt(math.pi) / 2.0 * (math.erf((1 - 0.35) / 0.005) - math.erf((0 - 0.35) / 0.005))
    miss = abs(L.gauss_legendre(peak, 0.0, 1.0, 20) - peak_exact) / peak_exact
    checks.append((f"failure: a narrow peak (width 0.005) is missed by 20 Gauss points (error {100 * miss:.0f} percent)", miss > 0.99))
    # exact areas
    checks.append(("exact areas: sqrt(pi)/2 erf(2) = 0.882081 and I0(1) = 1.266066", abs(L.FUNCTIONS[2][4] - 0.882081390762) < 1e-10 and abs(L.FUNCTIONS[4][4] - 1.2660658777520082) < 1e-14))
    # limits
    bad = 0
    for call in (lambda: L.gauss_legendre_nodes(0), lambda: L.gauss_legendre(math.exp, 1.0, 1.0, 3),
                 lambda: L.composite_gauss(math.exp, [0.0], 3), lambda: L.composite_gauss(math.exp, [0.0, 1.0, 0.5], 3)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("limits: zero points, a >= b, and edges that are not increasing are rejected", bad == 4))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson5", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
