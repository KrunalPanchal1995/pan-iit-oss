"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # --- multi-product mix
    mix = {"loaf": 0.8, "cake": 0.2}
    tot, parts = L.multi_break_even(mix)
    checks.append(("hand calculation: 0.8*2.10 + 0.2*9.00 = 3.48 per unit, break-even 1200/3.48 = 344.8 units",
                   abs(L.weighted_cm(mix) - 3.48) < 1e-9 and abs(tot - 344.8276) < 1e-3))
    checks.append(("the 80/20 break-even is about 275.9 loaves and 69.0 cakes",
                   abs(parts["loaf"] - 275.86) < 0.01 and abs(parts["cake"] - 68.97) < 0.01))
    t90 = L.multi_break_even({"loaf": 0.9, "cake": 0.1})[0]
    t60 = L.multi_break_even({"loaf": 0.6, "cake": 0.4})[0]
    checks.append(("mix shift: more loaves (90/10) raises break-even to 430.1 units; more cakes (60/40) lowers it to 246.9",
                   abs(t90 - 430.11) < 0.01 and abs(t60 - 246.91) < 0.01 and t60 < tot < t90))
    checks.append(("a single-product mix reproduces Session 2 (571.43 loaves)",
                   abs(L.multi_break_even({"loaf": 1.0, "cake": 0.0})[0] - 571.4286) < 1e-3))
    checks.append(("limit: shares that do not add to 1 are rejected", _raises(lambda: L.weighted_cm({"loaf": 0.5, "cake": 0.2}))))
    # --- step-fixed costs
    sc = L.sign_changes(L.profit_step)
    checks.append(("worked example: profit crosses zero up at 572, down at 701 and up again at 1000 loaves",
                   sc == [(571, 572, "up"), (700, 701, "down"), (999, 1000, "up")]))
    be = L.step_break_evens()
    checks.append(("formula crossings 571.43 and 1000 lie inside the scanned intervals",
                   len(be) == 2 and 571 < be[0] <= 572 and 999 < be[1] <= 1000))
    checks.append(("step fixed cost: $1200 up to 700 loaves, $2100 from 701 to 1400",
                   L.step_fixed(700) == 1200 and L.step_fixed(701) == 2100 and L.step_fixed(1400) == 2100
                   and L.step_fixed(0) == 1200))
    checks.append(("profit is $270 at 700 loaves, then -$627.90 at 701", abs(float(L.profit_step(700)) - 270.0) < 1e-9
                   and abs(float(L.profit_step(701)) + 627.9) < 1e-9))
    # --- Monte Carlo
    s = L.summarize(L.simulate_profit())
    checks.append(("seeded run: same numbers every time", L.summarize(L.simulate_profit()) == s))
    checks.append(("Monte Carlo: mean profit about $476 (plan says $480), standard deviation about $375",
                   abs(s["mean"] - 476.4) < 1.0 and abs(s["std"] - 374.9) < 1.0))
    checks.append(("Monte Carlo: loss probability about 9.5 percent; 5th and 95th percentile about -$102 and $1120",
                   abs(s["loss"] - 0.095) < 0.003 and abs(s["p5"] + 101.9) < 2.0 and abs(s["p95"] - 1120.4) < 3.0))
    only = L.simulate_profit(p_sd=0.0, v_sd=0.0)
    ref = L.loss_probability_demand_only()
    checks.append(("validation: with only demand random the simulation matches the formula (6.5 percent simulated, 6.4 percent by the formula)",
                   abs(ref - 0.0638) < 5e-4 and abs(float(np.mean(only < 0)) - ref) < 0.005 and abs(float(np.mean(only < 0)) - 0.065) < 0.001))
    checks.append(("limit: with no randomness at all the profit is exactly $480 every month",
                   np.allclose(L.simulate_profit(n=50, p_sd=0, v_sd=0, d_sd=0), 480.0)))
    # --- tornado
    tor = L.tornado()
    names = [r[0] for r in tor]
    checks.append(("worked example: tornado ranks price, demand, fixed cost, variable cost",
                   names == ["price", "demand", "fixed cost", "variable cost"]))
    sw = {r[0]: r[3] for r in tor}
    checks.append(("tornado swings are $560, $336, $240 and $224",
                   abs(sw["price"] - 560) < 1e-6 and abs(sw["demand"] - 336) < 1e-6
                   and abs(sw["fixed cost"] - 240) < 1e-6 and abs(sw["variable cost"] - 224) < 1e-6))
    pr = {r[0]: (r[1], r[2]) for r in tor}
    checks.append(("price -10 percent gives profit $200 and +10 percent gives $760",
                   abs(pr["price"][0] - 200) < 1e-6 and abs(pr["price"][1] - 760) < 1e-6))
    # --- time value
    flows = [480.0] * 36
    checks.append(("worked example: simple payback of $6000 at $480 a month is month 13 (12.5 months exactly)",
                   L.payback_month(6000, flows) == 13 and abs(6000 / 480 - 12.5) < 1e-12))
    checks.append(("discounted payback at 12 percent a year is month 14", L.payback_month(6000, flows, 0.12) == 14))
    checks.append(("monthly rate for 12 percent a year is 0.9489 percent", abs(L.monthly_rate(0.12) - 0.0094888) < 1e-6))
    checks.append(("NPV over 24 months: $4259 at 12 percent a year, $5520 with no discounting",
                   abs(L.npv(6000, flows[:24], 0.12) - 4259.15) < 0.01 and abs(L.npv(6000, flows[:24], 0.0) - 5520.0) < 1e-9))
    checks.append(("hand calculation: one payment of $1120 after 12 months is worth $1000 today at 12 percent a year",
                   abs(1120 / (1 + L.monthly_rate(0.12)) ** 12 - 1000.0) < 1e-9))
    checks.append(("limit: $150 a month never repays $6000 within 36 months", L.payback_month(6000, [150.0] * 36) is None))
    # --- failure cases
    checks.append(("failure: price equal to variable cost gives a message, not a number",
                   L.plan(1200, 1.4, 1.4).startswith("No break-even") and L.plan(1200, 1.0, 1.4).startswith("No break-even")
                   and L.plan(1200, 3.5, 1.4) == "Break-even at 571.4 units."))
    bp = L.break_even_prices()
    checks.append(("linear demand: break-even prices are $2.56 and $5.54 and profit is positive between them",
                   len(bp) == 2 and abs(bp[0] - 2.5586) < 1e-3 and abs(bp[1] - 5.5414) < 1e-3
                   and all(abs(float(L.profit_at_price(x))) < 1e-9 for x in bp)
                   and float(L.profit_at_price(4.05)) > 0 > float(L.profit_at_price(2.4)) and float(L.profit_at_price(5.7)) < 0))
    grid = np.arange(1.5, 6.5, 0.01)
    checks.append(("failure: with fixed cost $1800 no price breaks even (best profit is -$44.38)",
                   L.break_even_prices(1800.0) == [] and float(np.max(L.profit_at_price(grid, fixed=1800.0))) < 0
                   and abs(float(L.profit_at_price(4.05, fixed=1800.0)) + 44.375) < 1e-9))
    # --- mini-project
    best = None
    rows = []
    for cap in L.OPTIONS:
        for price in np.arange(3.0, 5.0001, 0.25):
            r = L.evaluate(float(price), cap)
            rows.append(r)
            if L.passes(r) and (best is None or r["mean_profit"] > best["mean_profit"]):
                best = r
    checks.append(("mini-project: the best passing choice is the 600-loaf oven at $4.25",
                   best is not None and best["capacity"] == 600 and abs(best["price"] - 4.25) < 1e-9))
    checks.append(("mini-project: it breaks even at 351 loaves, sells about 546 on average, margin of safety about 36 percent",
                   abs(best["break_even"] - 350.9) < 0.1 and abs(best["mean_sold"] - 545.7) < 1.0 and abs(best["mos"] - 0.357) < 0.005))
    checks.append(("mini-project: loss probability about 4 percent, mean profit about $556, payback 9 months",
                   abs(best["loss"] - 0.042) < 0.004 and abs(best["mean_profit"] - 555.7) < 2.0 and best["payback"] == 9))
    passing = sorted((r["capacity"], r["price"]) for r in rows if L.passes(r))
    checks.append(("mini-project: only $4.00 and $4.25 with the 600-loaf oven pass the rule", passing == [(600, 4.0), (600, 4.25)]))
    r35 = L.evaluate(3.5, 600)
    checks.append(("mini-project: the cheap price $3.50 fails (payback 21 months) and the 1000-loaf oven does not pay back within 36 months at $4.00",
                   r35["payback"] == 21 and not L.passes(r35) and L.evaluate(4.0, 1000)["payback"] is None))
    hits = [(c, round(float(p), 2)) for c in L.OPTIONS for p in np.arange(3.0, 5.0001, 0.05)
            if (lambda r: r["loss"] <= 0.02 and r["payback"] is not None and r["payback"] <= 10)(L.evaluate(float(p), c))]
    checks.append(("roadmap claim: no shipped oven size and price reaches loss <= 2 percent with payback <= 10 months", hits == []))
    return checks


def _raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


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
