"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    P = 100000.0
    e = L.emi(P, 0.12, 24)
    checks.append(("worked example: EMI for 100000 at 12 percent over 24 months is 4707.35", abs(e - 4707.35) < 0.005))
    g = 1.01 ** 24
    checks.append(("hand calculation: 100000 * 0.01 * 1.01^24 / (1.01^24 - 1) matches emi()",
                   abs(P * 0.01 * g / (g - 1) - e) < 1e-6))
    bal = L.simulate_balance(P, 0.12, 24)
    checks.append(("simulating month by month, the balance hits zero after 24 payments", abs(bal[-1]) < 1e-6))
    checks.append(("the balance never rises and never goes below zero (to rounding)",
                   bool(np.all(np.diff(bal) < 0) and np.all(bal > -1e-6))))
    ok = True
    for ann, m in ((0.05, 12), (0.09, 60), (0.24, 120), (0.15, 7)):
        ok &= abs(L.simulate_balance(50000.0, ann, m)[-1]) < 1e-5
    checks.append(("simulation reaches zero for several other rates and tenures", bool(ok)))
    checks.append(("zero rate: EMI = P / n", abs(L.emi(120000.0, 0.0, 12) - 10000.0) < 1e-9))
    checks.append(("continuous limit: 1000 at 10 percent for 5 years tends to 1648.72",
                   abs(L.continuous_growth(1000, 0.10, 5) - 1648.721) < 1e-3))
    seq = [L.compound_growth(1000, 0.10, n, 5) for n in (1, 2, 4, 12, 365, 100000)]
    checks.append(("more compounding periods always give more, but never above the limit",
                   all(b > a for a, b in zip(seq, seq[1:])) and seq[-1] < L.continuous_growth(1000, 0.10, 5)
                   and abs(seq[-1] - L.continuous_growth(1000, 0.10, 5)) < 1e-3
                   and abs(seq[0] - 1610.51) < 1e-2 and abs(seq[3] - 1645.309) < 1e-3))
    it, pr, b = L.schedule(P, 0.12, 24)
    checks.append(("month 1: interest 1000.00 and principal 3707.35",
                   abs(it[0] - 1000.0) < 1e-6 and abs(pr[0] - 3707.35) < 0.005))
    checks.append(("month 24: interest 46.61 and principal 4660.74",
                   abs(it[-1] - 46.61) < 0.005 and abs(pr[-1] - 4660.74) < 0.005))
    checks.append(("interest part falls and principal part rises every month",
                   bool(np.all(np.diff(it) < 0) and np.all(np.diff(pr) > 0))))
    checks.append(("every month interest + principal = EMI", np.allclose(it + pr, e, atol=1e-9)))
    checks.append(("principal parts add up to P and the last balance is zero",
                   abs(pr.sum() - P) < 1e-6 and abs(b[-1]) < 1e-6))
    checks.append(("total interest = n EMI - P = sum of interest parts = 12976.33",
                   abs(L.total_interest(P, 0.12, 24) - 12976.33) < 0.005 and abs(it.sum() - L.total_interest(P, 0.12, 24)) < 1e-6))
    tab = L.tenure_table(P, 0.12, (12, 24, 36, 48, 60))
    checks.append(("tenure table: EMI 8884.88 (12 months) ... 2224.44 (60 months)",
                   abs(tab[0][1] - 8884.88) < 0.005 and abs(tab[-1][1] - 2224.44) < 0.005))
    checks.append(("tenure table: total interest 6618.55 (12 months) rises to 33466.69 (60 months)",
                   abs(tab[0][2] - 6618.55) < 0.005 and abs(tab[-1][2] - 33466.69) < 0.005))
    checks.append(("longer tenure: EMI always falls, total interest always rises",
                   all(a[1] > b2[1] and a[2] < b2[2] for a, b2 in zip(tab, tab[1:]))))
    checks.append(("5 times the tenure gives about a quarter of the EMI... but over 5 times the interest",
                   abs(tab[-1][1] / tab[0][1] - 0.25) < 0.001 and tab[-1][2] / tab[0][2] > 5.0))
    checks.append(("effective annual rate of 12 percent a year, paid monthly, is 12.683 percent",
                   abs(L.effective_annual_rate(0.12) - 0.126825) < 1e-6 and abs(L.effective_annual_rate(0.0)) < 1e-12))
    ca = L.total_cost(P, 0.090, 36, 0.02)
    cb = L.total_cost(P, 0.098, 36, 0.0)
    checks.append(("design: offer A (9.0 percent + 2 percent fee) costs 16479.04 in total",
                   abs(ca - 16479.04) < 0.005))
    checks.append(("design: offer B (9.8 percent, no fee) costs 15824.13 and is cheaper than A",
                   abs(cb - 15824.13) < 0.005 and cb < ca))
    checks.append(("offer A has the lower EMI (3179.97 against 3217.34) but the higher total cost",
                   abs(L.emi(P, 0.090, 36) - 3179.97) < 0.005 and abs(L.emi(P, 0.098, 36) - 3217.34) < 0.005))
    checks.append(("hand numbers: 1.01^24 = 1.2697 and 1.01^12 = 1.1268",
                   abs(1.01 ** 24 - 1.269735) < 1e-6 and abs(1.01 ** 12 - 1.126825) < 1e-6))
    checks.append(("tenure table: 36 months gives EMI 3321.43 and interest 19571.52; 24 months already gives EMI above 4000",
                   abs(tab[2][1] - 3321.43) < 0.005 and abs(tab[2][2] - 19571.52) < 0.005 and tab[1][1] > 4000))
    checks.append(("daily compounding (n = 365) gives 1648.61 for 1000 at 10 percent over 5 years",
                   abs(seq[4] - 1648.608) < 1e-3))
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
