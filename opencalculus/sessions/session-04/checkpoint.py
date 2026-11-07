"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    ex = math.e - 1.0
    # worked example: e^x on [0, 1], three levels
    table, ev = L.romberg_table(math.exp, 0.0, 1.0, 3)
    t0, t1, t2 = table[0][0], table[1][0], table[2][0]
    r11, r21, r22 = table[1][1], table[2][1], table[2][2]
    checks.append((f"worked example: T0, T1, T2 = {t0:.6f}, {t1:.6f}, {t2:.6f} (1.859141, 1.753931, 1.727222)",
                   abs(t0 - 1.859141) < 1e-6 and abs(t1 - 1.753931) < 1e-6 and abs(t2 - 1.727222) < 1e-6))
    checks.append((f"worked example: R11, R21, R22 = {r11:.6f}, {r21:.6f}, {r22:.6f} (1.718861, 1.718319, 1.718284) using {ev} evaluations",
                   abs(r11 - 1.718861) < 1e-6 and abs(r21 - 1.718319) < 1e-6 and abs(r22 - 1.718283) < 1e-6 and ev == 5))
    # hand calculations
    checks.append(("richardson(3.0, 3.1, 2) = (4 x 3.1 - 3.0) / 3 = 3.13333", abs(L.richardson(3.0, 3.1, 2) - 3.1333333333) < 1e-9))
    f_pi = lambda x: 4.0 / (1.0 + x * x)
    tp, _ = L.romberg_table(f_pi, 0.0, 1.0, 3)
    checks.append((f"hand table for pi: first column 3, 3.1, 3.131176; R11 = 3.13333, R21 = 3.141569, R22 = 3.142118",
                   abs(tp[0][0] - 3.0) < 1e-12 and abs(tp[1][0] - 3.1) < 1e-12 and abs(tp[2][0] - 3.131176) < 1e-6
                   and abs(tp[1][1] - 3.133333) < 1e-6 and abs(tp[2][1] - 3.141569) < 1e-6 and abs(tp[2][2] - 3.142118) < 1e-6))
    # column 1 is Simpson's rule
    simp = lambda f, a, b, n: (b - a) / n / 3.0 * (f(a) + f(b) + sum((4 if i % 2 else 2) * f(a + (b - a) * i / n) for i in range(1, n)))
    s4, s16 = simp(math.exp, 0.0, 1.0, 4), simp(math.exp, 0.0, 1.0, 16)
    tb, _ = L.romberg_table(math.exp, 0.0, 1.0, 5)
    checks.append(("column 1 of the table is exactly Simpson's rule (4 and 16 slices)", abs(tb[2][1] - s4) < 1e-13 and abs(tb[4][1] - s16) < 1e-13))
    # exactness for polynomials: column j is exact up to degree 2j + 1
    for j, deg in ((1, 3), (2, 5), (3, 7)):
        tt, _ = L.romberg_table(lambda x, d=deg: x ** d, 0.0, 1.0, j + 1)
        checks.append((f"column {j} is exact for x^{deg} (area 1/{deg + 1})", abs(tt[j][j] - 1.0 / (deg + 1)) < 1e-12))
    # function evaluations are counted and reused
    calls = [0]

    def counted(x):
        calls[0] += 1
        return math.exp(x)

    _, evals = L.romberg_table(counted, 0.0, 1.0, 5)
    checks.append((f"every sample is computed once: 5 levels cost {evals} evaluations and f was called {calls[0]} times (17)",
                   evals == 17 and calls[0] == 17 and L.evaluations_for_levels(5) == 17 and L.evaluations_for_levels(1) == 2))
    # orders of the columns
    oks = []
    for j, want in ((0, 2), (1, 4), (2, 6)):
        hs, es = L.column_errors(math.exp, 0.0, 1.0, ex, 6, j)
        oks.append(abs(L.observed_order(hs[:4], es[:4]) - want) < 0.05)
    checks.append(("observed orders of columns 0, 1, 2 are 2, 4, 6", all(oks)))
    # the roadmap checkpoint
    value, evals17 = L.romberg(math.exp, 0.0, 1.0, 5)
    err = abs(value - ex)
    simp17 = abs(tb[4][1] - ex)
    checks.append((f"roadmap checkpoint: e^x on [0, 1] with {evals17} evaluations has error {err:.1e} (below 1e-12); Simpson with 17 gives {simp17:.1e}",
                   evals17 == 17 and err < 1e-12 and 1e-7 < simp17 < 2e-7))
    checks.append(("round-off floor: 9 levels (257 evaluations) are no better than about 1e-15",
                   abs(L.romberg(math.exp, 0.0, 1.0, 9)[0] - ex) < 1e-15))
    # stopping rule
    v, e, lv, ok = L.romberg_tol(math.exp, 0.0, 1.0, 1e-10)
    checks.append((f"romberg_tol stops by itself: e^x in {e} evaluations ({lv} levels), error {abs(v - ex):.0e}", ok and e == 33 and abs(v - ex) < 1e-14))
    # smooth but bending: the Gaussian
    _, f2, a2, b2, ex2 = L.FUNCTIONS[2]
    r2, e2 = L.romberg(f2, a2, b2, 7)
    checks.append((f"exp(-x^2) on [0, 2]: 65 evaluations give error {abs(r2 - ex2):.0e} (below 1e-12)", e2 == 65 and abs(r2 - ex2) < 1e-12))
    # failure: sqrt(x)
    _, f3, a3, b3, ex3 = L.FUNCTIONS[3]
    t3, _ = L.romberg_table(f3, a3, b3, 8)
    e_tr, e_rb = abs(t3[7][0] - ex3), abs(t3[7][7] - ex3)
    checks.append((f"failure: sqrt(x) with 129 values: trapezoid error {e_tr:.1e}, Romberg {e_rb:.1e} (extrapolation gains less than a factor 10)",
                   e_rb > 1e-5 and e_tr / e_rb < 10))
    # failure: periodic function
    _, f4, a4, b4, ex4 = L.FUNCTIONS[4]
    t4, _ = L.romberg_table(f4, a4, b4, 7)
    checks.append((f"failure: periodic function: trapezoid with 17 values is already at round-off ({abs(t4[4][0] - ex4):.0e}) but Romberg with 65 values is worse ({abs(t4[6][6] - ex4):.0e})",
                   abs(t4[4][0] - ex4) < 1e-12 and abs(t4[6][6] - ex4) > 1e-9))
    v4, e4, lv4, ok4 = L.romberg_tol(f4, a4, b4, 1e-10)
    checks.append((f"failure: the stopping rule is fooled on exp(sin(2 pi x)): it stops at {lv4} levels with {e4} values, claiming success, while the error is {abs(v4 - ex4):.2f}",
                   ok4 and e4 == 3 and abs(v4 - ex4) > 0.2))
    # exact reference values
    checks.append(("exact areas: e - 1, sqrt(pi)/2 erf(2) = 0.882081, 2/3, I0(1) = 1.266066",
                   abs(L.EXACT_GAUSS - 0.882081390762) < 1e-10 and abs(L.EXACT_PERIODIC - 1.2660658777520082) < 1e-14))
    # mini-project reference numbers (Gaussian, evaluations on the 2^k grids)
    need = {r: [L.evaluations_needed(2, t, r) for t in (1e-6, 1e-8, 1e-10, 1e-12)] for r in ("trapezoid", "simpson", "romberg")}
    checks.append((f"mini-project: Simpson needs {need['simpson']}, Romberg {need['romberg']} values for 1e-6, 1e-8, 1e-10, 1e-12; the trapezoid needs {need['trapezoid'][:3]} and more than 131 073 for the last",
                   need["simpson"] == [17, 65, 257, 513] and need["romberg"] == [17, 33, 33, 65] and need["trapezoid"] == [257, 2049, 16385, None]))
    # limits
    bad = 0
    for args in ((math.exp, 0.0, 1.0, 0), (math.exp, 1.0, 1.0, 3), (math.exp, 2.0, 1.0, 3)):
        try:
            L.romberg_table(*args)
        except ValueError:
            bad += 1
    try:
        L.evaluations_needed(1, 1e-3, "midpoint")
        bad_rule = False
    except ValueError:
        bad_rule = True
    checks.append(("limits: zero levels and a >= b are rejected, and an unknown rule name is rejected", bad == 3 and bad_rule))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
