"""Checkpoint for Session 5. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    i6 = L.diode_current(0.6)
    g6 = L.diode_conductance(0.6) - L.GMIN
    checks.append((f"diode law: I(0.6 V) = {1000 * i6:.2f} mA, and 60 mV more multiplies the current by {L.diode_current(0.66) / i6:.2f} (about 10)",
                   abs(i6 - 0.012010) < 1e-5 and abs(L.diode_current(0.66) / i6 - 10.185) < 0.01))
    h = 1e-7
    slope = (L.diode_current(0.6 + h) - L.diode_current(0.6 - h)) / (2 * h)
    checks.append(("the conductance g = (I + Is) / (n VT) matches a numerical slope of the diode curve to 1e-6", abs(g6 / slope - 1) < 1e-6))
    g, i_eq = L.companion(0.6)
    checks.append(("worked example (Section E): at 0.6 V the tangent is g = 0.4646 S and i_eq = -0.2667 A; one Newton step gives 0.5837 V",
                   abs(g - 0.46458) < 1e-4 and abs(i_eq + 0.26674) < 1e-4 and abs(L.newton_step_series(5.0, 1000.0, 0.6) - 0.583654) < 1e-5))
    res_before = (0.6 - 5.0) / 1000 + i6
    v1 = L.newton_step_series(5.0, 1000.0, 0.6)
    res_after = (v1 - 5.0) / 1000 + L.diode_current(v1)
    checks.append((f"the KCL residual falls from {1000 * res_before:.2f} mA to {1000 * res_after:.2f} mA in one step (still not zero: the tangent is not the curve)",
                   abs(res_before - 0.00761) < 1e-5 and 0 < res_after < res_before / 3))

    # the roadmap checkpoint
    net = L.newton_solve(**L.SERIES)
    vd, i = L.series_diode_exact(5.0, 1000.0)
    checks.append((f"roadmap test: 5 V, 1 kohm and a diode converge to a KCL residual of {net['residual']:.0e} A in {net['iterations']} passes (limit: below 1e-9 A in at most 10)",
                   net["residual"] < 1e-9 and net["iterations"] <= 10))
    checks.append((f"the answer agrees with bisection: diode voltage {net['v'][2]:.6f} V and current {1000 * net['j'][0]:.4f} mA (exact {vd:.6f} V, {1000 * i:.4f} mA)",
                   abs(net["v"][2] - vd) < 1e-9 and abs(net["j"][0] - i) < 1e-9 and abs(vd - 0.574192) < 1e-5))
    hist = [x[1] for x in net["history"]]
    checks.append(("quadratic convergence at the end: each of the last two residuals is below the previous one raised to the power 1.5",
                   hist[-1] < hist[-2] ** 1.5 and hist[-2] < hist[-3] ** 1.5))

    # many circuits against bisection
    worst, ok = 0.0, True
    for vs, r in ((1.0, 10000.0), (3.3, 220.0), (5.0, 100.0), (9.0, 4700.0), (12.0, 100.0), (24.0, 1000.0), (0.5, 1000.0)):
        vd_n, i_n, it = L.series_diode(vs, r)
        vd_b, i_b = L.series_diode_exact(vs, r)
        worst = max(worst, abs(vd_n - vd_b))
        ok &= it <= 12 and abs(i_n / i_b - 1) < 1e-6
    checks.append((f"7 more series circuits (0.5 V to 24 V, 100 ohm to 10 kohm): each within 12 passes (most need 6 to 8; 0.5 V needs 11) and within {worst:.0e} V of bisection", ok and worst < 1e-8))

    # a network with the diode between two resistors; power balance and KCL at every node
    t = L.newton_solve(**L.TWO_RESISTOR)
    v, j = t["v"], t["j"]
    vd_b, i_b = L.two_resistor_exact()
    i_loop = (v[1] - v[2]) / 1000.0
    p_supply = 9.0 * j[0]
    p_used = i_loop ** 2 * 1000.0 + (v[3] / 470.0) ** 2 * 470.0 + (v[2] - v[3]) * L.diode_current(v[2] - v[3])
    checks.append((f"network 9 V - 1000 ohm - diode - 470 ohm: diode voltage {v[2] - v[3]:.6f} V (bisection {vd_b:.6f}); supplied power {1000 * p_supply:.3f} mW equals the power used",
                   abs(v[2] - v[3] - vd_b) < 1e-9 and abs(j[0] - i_b) < 1e-9 and abs(p_supply - p_used) < 1e-9 and t["residual"] < 1e-9))

    # failure cases
    msg = L.plain_newton_fails()
    checks.append(("failure: without the limiter the loop started at 0 V jumps to 5 V across the diode, where its conductance is about 1e61 S, and the solver reports a singular matrix",
                   msg is not None and "singular" in msg and L.limit_step(0.0, 5.0) < 0.14 and abs(L.limit_step(0.5, 0.3) - 0.3) < 1e-15))
    works = L.newton_solve(**L.SERIES, limit=False, v0=[0.7])["iterations"]
    fails = L.newton_solve  # the plain loop depends on the start: 0.7 V works, 0.3 V fails
    try:
        fails(**L.SERIES, limit=False, v0=[0.3])
        bad_start = False
    except L.NewtonError:
        bad_start = True
    slow = L.newton_solve(**L.SERIES, v0=[1.0])["iterations"]
    checks.append((f"failure: the plain loop depends on the start: from 0.7 V it takes {works} passes, from 0.3 V it fails; the limiter converges from every start tried (at most 25 passes), but a start above the answer is slow ({slow} passes from 1.0 V) because each pass can only lower the voltage by about VT",
                   works <= 10 and bad_start and slow > 10 and all(L.newton_solve(**L.SERIES, v0=[w])["iterations"] <= 25 for w in (0.0, 0.3, 0.7, 1.0, -2.0))))
    try:
        L.newton_solve(**L.SERIES, max_iter=3)
        stops = False
    except L.NewtonError as e:
        stops = "no convergence" in str(e)
    checks.append(("failure: when max_iter is too small the loop raises an error instead of returning a wrong answer", stops))
    try:
        L.newton_solve(3, [(1, 0, 100.0), (2, 3, 100.0)], [(1, 0, 5.0)], diodes=[(2, 3)])
        floating = False
    except L.NewtonError:
        floating = True
    checks.append(("failure: a diode on a floating part (no path to ground) is reported by the linear solver through NewtonError", floating))
    rev = L.newton_solve(2, [(1, 2, 1000.0)], [(1, 0, 5.0)], diodes=[(0, 2)])
    checks.append((f"reversed diode: only the leakage current flows ({rev['j'][0]:.1e} A) and the whole 5 V is across the diode ({rev['v'][0] - rev['v'][2]:.3f} V), in {rev['iterations']} passes",
                   abs(rev["j"][0] - 1e-12) < 1e-13 and abs(rev["v"][0] - rev["v"][2] + 5.0) < 1e-6 and rev["iterations"] <= 3))

    # constant drop rule and mini-project
    e07 = [L.constant_drop_error(5.0, r, 0.7) for r in (100.0, 1000.0, 10000.0)]
    e06 = L.constant_drop_error(5.0, 1000.0, 0.6)
    checks.append((f"the 0.7 V rule underestimates the current by {-100 * e07[0]:.1f} %, {-100 * e07[1]:.1f} % and {-100 * e07[2]:.1f} % for 100 ohm, 1 kohm and 10 kohm; a 0.6 V drop is {100 * e06:+.1f} % at 1 kohm",
                   abs(e07[0] + 0.015) < 0.002 and abs(e07[1] + 0.028) < 0.002 and abs(e07[2] + 0.041) < 0.002 and abs(e06 + 0.006) < 0.002))
    best, row = L.choose_indicator_resistor()
    tab = {r: (a, b) for r, a, b, _, _ in L.indicator_table([470.0, 560.0, 1200.0, 1500.0])}
    checks.append((f"mini-project: the largest E12 resistor that gives at least 3 mA at 4.5 V and at most 10 mA at 5.5 V is {best} ohm ({1000 * row[1]:.2f} mA and {1000 * row[2]:.2f} mA, {1000 * row[4]:.0f} mW in R); 470 ohm gives too much and 1500 ohm too little",
                   best == 1200.0 and abs(row[1] - 0.003278) < 2e-6 and abs(row[2] - 0.004106) < 2e-6 and tab[470.0][1] > 0.010 and tab[1500.0][0] < 0.003 and tab[560.0][1] < 0.010))
    passing = [r for r, lo, hi, _, _ in L.indicator_table() if lo >= 3e-3 and hi <= 10e-3]
    rule_lo, rule_hi = (4.5 - 0.7) / 1200.0, (5.5 - 0.7) / 1200.0
    checks.append((f"mini-project: the passing E12 resistors are {[int(r) for r in passing]}; the 0.7 V rule would give {1000 * rule_lo:.2f} mA and {1000 * rule_hi:.2f} mA for 1.2 kohm, about 3 percent below the loop",
                   passing == [560.0, 680.0, 820.0, 1000.0, 1200.0] and abs(rule_lo / row[1] - 1) < 0.04 and abs(rule_hi / row[2] - 1) < 0.04 and rule_lo < row[1] and rule_hi < row[2]))
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
