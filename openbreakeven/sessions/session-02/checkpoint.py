"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    q = L.break_even_qty()
    checks.append(("worked example: contribution margin 3.50 - 1.40 = 2.10 and ratio 0.60",
                   abs(L.contribution_margin() - 2.1) < 1e-12 and abs(L.contribution_ratio() - 0.6) < 1e-12))
    checks.append(("worked example: break-even quantity 1200 / 2.10 = 571.43 loaves, 572 whole loaves",
                   abs(q - 571.4286) < 1e-3 and L.whole_units(q) == 572))
    checks.append(("scanning q on a fine grid finds the same break-even", abs(L.scan_break_even() - q) < 0.011))
    checks.append(("break-even revenue is $2000 = 1200 / 0.60", abs(L.break_even_revenue() - 2000.0) < 1e-9))
    checks.append(("profit is zero at break-even and $480 at 800 loaves",
                   abs(float(L.profit(q))) < 1e-9 and abs(float(L.profit(800)) - 480.0) < 1e-9))
    checks.append(("worked example: margin of safety at 800 loaves is 28.57 percent",
                   abs(L.margin_of_safety() - 0.285714) < 1e-5))
    checks.append(("target profit $600 needs 857.14 loaves, 858 whole loaves",
                   abs(L.target_qty(600) - 857.142857) < 1e-5 and L.whole_units(L.target_qty(600)) == 858
                   and float(L.profit(858)) >= 600 > float(L.profit(857))))
    checks.append(("worked example: degree of operating leverage is 3.5 (formula and recomputation)",
                   abs(L.dol() - 3.5) < 1e-9 and abs(L.dol_numeric() - 3.5) < 1e-9))
    checks.append(("sales +10 percent gives profit $648 (+35 percent)",
                   abs(float(L.profit(880)) - 648.0) < 1e-9 and abs(float(L.profit(880)) / 480.0 - 1.35) < 1e-9))
    checks.append(("sales -10 percent gives profit $312 (-35 percent)",
                   abs(float(L.profit(720)) - 312.0) < 1e-9 and abs(float(L.profit(720)) / 480.0 - 0.65) < 1e-9))
    # hand calculation: F=900, p=5, v=2 -> cm 3
    checks.append(("hand calculation: F=900, p=5, v=2 gives 300 loaves, revenue $1500, 500 loaves for $600",
                   abs(L.break_even_qty(900, 5, 2) - 300) < 1e-9 and abs(L.break_even_revenue(900, 5, 2) - 1500) < 1e-9
                   and abs(L.target_qty(600, 900, 5, 2) - 500) < 1e-9))
    checks.append(("profit line: -$1200 at zero loaves, slope $2.10 per loaf",
                   abs(float(L.profit(0)) + 1200) < 1e-9 and abs(float(L.profit(101) - L.profit(100)) - 2.1) < 1e-9))
    # risk comparison with the same profit at 800 loaves
    q2 = L.profit(720, 3.5, 2.15, 600.0)
    checks.append(("a low-fixed-cost bakery with the same $480 profit loses only 22.5 percent when sales fall 10 percent",
                   abs(float(L.profit(800, 3.5, 2.15, 600.0)) - 480.0) < 1e-9 and abs(float(q2) - 372.0) < 1e-9
                   and abs(float(q2) / 480.0 - 0.775) < 1e-9 and abs(L.dol(800, 600.0, 3.5, 2.15) - 2.25) < 1e-9))
    # design problem
    t = L.prices_for_target(500)
    checks.append(("design: two prices, 3.58 and 4.52 dollars, reach a $500 profit",
                   len(t) == 2 and abs(t[0] - 3.5783) < 1e-3 and abs(t[1] - 4.5217) < 1e-3
                   and all(abs(float(L.profit_at_price(x)) - 500) < 1e-9 for x in t)))
    s = L.scan_prices_for_target(500)
    checks.append(("design: scanning prices finds the same two roots", len(s) == 2 and all(abs(a - b) < 2e-3 for a, b in zip(s, t))))
    d = L.demand(t)
    checks.append(("design: the two prices sell 780 and 545 loaves", abs(d[0] - 780.4) < 0.1 and abs(d[1] - 544.6) < 0.1))
    mos = [L.margin_of_safety(float(d[i]), 1200, t[i], 1.4) for i in range(2)]
    be = [L.break_even_qty(1200, t[i], 1.4) for i in range(2)]
    checks.append(("design: both prices have break-even near 551 and 384 loaves and margin of safety 500/1700 = 29.4 percent",
                   abs(be[0] - 550.9) < 0.1 and abs(be[1] - 384.4) < 0.1
                   and all(abs(m - 500 / 1700) < 1e-9 for m in mos)))
    checks.append(("design: best price is $4.05 with profit about $555.6",
                   abs(L.best_price() - 4.05) < 1e-12 and abs(float(L.profit_at_price(4.05)) - 555.625) < 1e-9))
    grid = np.arange(1.5, 6.5, 0.01)
    checks.append(("design: a scan over prices agrees the best price is 4.05",
                   abs(float(grid[np.argmax(L.profit_at_price(grid))]) - 4.05) < 0.011))
    checks.append(("design: a $600 target cannot be reached at any price", L.prices_for_target(600) == []
                   and float(np.max(L.profit_at_price(grid))) < 600))
    # edge and limit cases
    checks.append(("limit: price equal to variable cost has no break-even", L.break_even_qty(1200, 1.4, 1.4) is None
                   and L.break_even_revenue(1200, 1.0, 1.4) is None and L.scan_break_even(1200, 1.4, 1.4) is None))
    checks.append(("limit: DOL is not defined when profit is exactly zero", L.dol(q) is None))
    checks.append(("limit: margin of safety is negative below break-even", L.margin_of_safety(400) < 0))
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
