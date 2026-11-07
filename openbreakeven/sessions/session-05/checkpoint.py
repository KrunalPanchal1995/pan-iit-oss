"""Checkpoint for Session 5. Prints PASS or FAIL."""
import numpy as np


def _raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    pr = L.monthly_profits()
    flat_month = (L.P - L.V) * L.Q - L.F
    # --- the pattern and the roadmap checkpoint
    checks.append(("the 12 seasonal factors average exactly 1.0 and December is the peak (1.55)",
                   abs(sum(L.SEASON) / 12 - 1.0) < 1e-12 and L.SEASON.index(max(L.SEASON)) == 11))
    total = float(pr[:12].sum())
    checks.append((f"roadmap check: the twelve monthly profits add up to ${total:.0f}, 12 times the flat monthly profit ${flat_month:.0f} (within 1 percent)",
                   abs(total - 12 * flat_month) < 0.01 * 12 * flat_month and abs(total - 5760.0) < 1e-6))
    checks.append(("worked example: monthly profits are 228, 144, 312, 396, 480, 396, 312, 312, 480, 564, 732 and 1404 dollars",
                   np.allclose(pr[:12], [228, 144, 312, 396, 480, 396, 312, 312, 480, 564, 732, 1404])))
    checks.append(("the pattern repeats: month 13 equals month 1 and the profits are a straight line in the factor",
                   abs(pr[12] - pr[0]) < 1e-9 and np.allclose(pr[:12], 2.1 * 800 * np.array(L.SEASON) - 1200)))
    checks.append(("the total over any 12 consecutive months does not depend on the opening month",
                   all(abs(L.monthly_profits(L.SEASON, 12, s).sum() - 5760.0) < 1e-6 for s in range(1, 13))))
    checks.append(("limit: a pattern that does not average 1.0, has the wrong length or a negative factor is rejected",
                   _raises(lambda: L.check_season([1.0] * 11)) and _raises(lambda: L.check_season([1.2] * 12)) and _raises(lambda: L.check_season([-0.5] + [1.0454545454545454] * 11))))
    flat = L.scale_season(L.SEASON, 0.0)
    checks.append(("scale_season: k = 0 is a flat year, k = 1 is unchanged, k = 1.5 still averages 1.0, k = 6 is rejected",
                   all(abs(x - 1.0) < 1e-12 for x in flat) and np.allclose(L.scale_season(L.SEASON, 1.0), L.SEASON)
                   and abs(sum(L.scale_season(L.SEASON, 1.5)) / 12 - 1.0) < 1e-9 and _raises(lambda: L.scale_season(L.SEASON, 6.0))))
    # --- the loan
    a12 = L.loan_payment(4000, 0.09, 12)
    checks.append((f"worked example: 4000 dollars at 9 percent over 12 months is repaid by instalments of ${a12:.2f}", abs(a12 - 349.81) < 0.005))
    sch = L.loan_schedule(4000, 0.09, 12)
    checks.append(("validation: the schedule ends with a balance of 0 and the repaid parts add up to the 4000 borrowed",
                   abs(sch[-1]["balance"]) < 1e-6 and abs(sum(r["repaid"] for r in sch) - 4000.0) < 1e-6))
    checks.append(("the first instalment holds 30.00 dollars of interest (4000 x 0.0075) and the interest falls every month",
                   abs(sch[0]["interest"] - 30.0) < 1e-9 and all(b["interest"] < a["interest"] for a, b in zip(sch, sch[1:]))))
    checks.append((f"total interest is ${L.total_interest(4000, 0.09, 12):.1f} for 12 months and ${L.total_interest(4000, 0.09, 24):.1f} for 24: a longer loan costs more interest but has a smaller instalment",
                   abs(L.total_interest(4000, 0.09, 12) - 197.7) < 0.1 and abs(L.total_interest(4000, 0.09, 24) - 385.7) < 0.1
                   and L.loan_payment(4000, 0.09, 24) < a12))
    checks.append(("limit: with a rate of 0 the instalment is the principal over the term (1000 for 4000 over 4 months)", abs(L.loan_payment(4000, 0.0, 4) - 1000.0) < 1e-12))
    checks.append(("limit: a zero or negative term and a negative rate are rejected", _raises(lambda: L.loan_payment(1000, 0.09, 0)) and _raises(lambda: L.loan_payment(1000, -0.01, 12))))
    # --- the running total
    rt = L.running_total(pr, loan=4000, term=12)
    checks.append((f"month by month: the running total starts at -2000 (the owner's part) and is {rt[0]:.0f}, {rt[1]:.0f}, {rt[2]:.0f} after January, February and March",
                   len(rt) == 24 and abs(rt[0] + 2121.81) < 0.01 and abs(rt[1] + 2327.61) < 0.01 and abs(rt[2] + 2365.42) < 0.01))
    m, low = L.lowest_month(pr, loan=4000, term=12)
    checks.append((f"worked example: the lowest point is in month {m}, ${-low:.1f} below the starting level, so the owner needs ${L.extra_cash_needed(pr, 4000, 0.09, 12):.1f} of extra cash",
                   m == 3 and abs(-low - 365.4) < 0.1 and abs(L.extra_cash_needed(pr, 4000, 0.09, 12) - 365.4) < 0.1))
    checks.append(("a flat bakery with the same yearly profit never dips: the extra cash needed is 0, a seasonal one needs 365.4",
                   L.extra_cash_needed(L.monthly_profits(flat), 4000, 0.09, 12) == 0.0 and abs(L.extra_cash_needed(pr, 4000, 0.09, 12) - 365.4) < 0.1))
    checks.append(("the first year's cash change is the profit total minus 12 instalments: 5760 - 12 x 349.81 = 1562.3",
                   abs(float(np.cumsum(pr - np.where(np.arange(24) < 12, a12, 0.0))[11]) - 1562.33) < 0.01))
    need = [L.extra_cash_needed(pr, 4000, 0.09, t) for t in (6, 12, 18, 24)]
    checks.append((f"a longer term needs less extra cash: {need[0]:.0f}, {need[1]:.0f}, {need[2]:.0f} and {need[3]:.0f} dollars for 6, 12, 18 and 24 months",
                   need[0] > need[1] > need[2] > need[3] == 0.0 and abs(need[2] - 104.8) < 0.1))
    checks.append(("no loan: the running total starts at -6000 and the owner's money is back in month 14; with 4000 over 12 months in month 15",
                   abs(L.running_total(pr, loan=0.0)[0] - (-6000 + pr[0])) < 1e-9 and L.equity_recovered_month(pr, loan=0.0) == 14
                   and L.equity_recovered_month(pr, loan=4000, term=12) == 15))
    by = L.extra_cash_by_start(4000, 0.09, 12)
    checks.append(("the opening month matters: January needs 365.4 dollars, April, May and September to December need none",
                   abs(by[1] - 365.4) < 0.1 and all(by[s] == 0.0 for s in (4, 5, 9, 10, 11, 12))))
    # --- random demand
    cs0 = L.simulate_cash(n=10, d_sd=0.0)
    checks.append(("limit: with no randomness every simulated year equals the planned year",
                   np.allclose(cs0, np.cumsum(pr - np.where(np.arange(24) < 12, a12, 0.0)))))
    mean_sim = L.simulate_cash(n=50000).mean(axis=0)
    plan = np.cumsum(pr - np.where(np.arange(24) < 12, a12, 0.0))
    checks.append((f"validation: the mean of 50000 simulated years follows the plan to within ${np.abs(mean_sim - plan).max():.1f}", np.abs(mean_sim - plan).max() < 12.0))
    checks.append(("seeded run: the same numbers every time", L.shortfall_probability(500) == L.shortfall_probability(500)))
    s_loan = [L.shortfall_probability(1000, loan=4000, term=t) for t in (6, 12, 18, 24)]
    checks.append((f"the chance of needing more than 1000 dollars falls with the term: {', '.join(f'{100 * x:.1f}' for x in s_loan)} percent for 6, 12, 18 and 24 months",
                   all(b < a for a, b in zip(s_loan, s_loan[1:])) and abs(s_loan[2] - 0.087) < 0.01))
    checks.append(("with no loan the chance of needing more than 200 dollars is about 15 percent: demand noise alone causes loss months in winter",
                   abs(L.shortfall_probability(200, loan=0.0) - 0.152) < 0.01))
    # --- mini-project
    grid = {(loan, t): L.evaluate_loan(loan, t) for loan in (1000, 2000, 3000, 4000, 5000, 6000) for t in (6, 12, 18, 24)}
    ok = [k for k, r in grid.items() if L.loan_passes(r)]
    best = max(ok, key=lambda k: (k[0], -grid[k]["interest"]))
    checks.append((f"mini-project: {len(ok)} of the 24 loan choices pass; the one that borrows the most is {best[0]} dollars over {best[1]} months",
                   len(ok) == 12 and best == (5000, 24)))
    r = grid[(5000, 24)]
    checks.append((f"mini-project: 5000 over 24 months has an instalment of ${r['payment']:.1f}, interest ${r['interest']:.1f}, extra cash ${r['extra']:.1f} and a {100 * r['risk']:.1f} percent chance of needing more than the 1000 buffer",
                   abs(r["payment"] - 228.4) < 0.1 and abs(r["interest"] - 482.2) < 0.1 and abs(r["extra"] - 84.8) < 0.1 and abs(r["risk"] - 0.076) < 0.01))
    checks.append(("mini-project: 5000 over 18 months and 4000 over 12 months fail (risk 19 and 33 percent)",
                   not L.loan_passes(grid[(5000, 18)]) and not L.loan_passes(grid[(4000, 12)])))
    checks.append(("edge: no loan means no instalment and no interest", L.evaluate_loan(0.0, 12)["payment"] == 0.0 and L.evaluate_loan(0.0, 12)["interest"] == 0.0))
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
