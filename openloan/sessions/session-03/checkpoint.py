"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    P = 100000.0
    k, tot, hist = L.simulate(P, lambda m: 0.12, L.emi(P, 0.12, 24))
    checks.append(("simulator agrees with Session 2: clears in 24 months, interest 12976.33",
                   k == 24 and abs(tot - 12976.33) < 0.005 and abs(hist[-1]) < 1e-5))
    checks.append(("zero rate edge case: 1200 paid at 100 a month clears in 12 months with no interest",
                   L.simulate(1200.0, lambda m: 0.0, 100.0)[:2] == (12, 0.0)))
    c = L.prepayment_case()
    checks.append(("prepayment base: EMI 4448.89, 60 months, interest 66933.37",
                   abs(c["emi"] - 4448.89) < 0.005 and c["base"][0] == 60 and abs(c["base"][1] - 66933.37) < 0.005))
    checks.append(("worked example: a 50000 lump sum after month 12 ends the loan in 44 months with interest 42482.30",
                   c["lump"][0] == 44 and abs(c["lump"][1] - 42482.30) < 0.005))
    checks.append(("lump sum saves 24451.07 of interest", abs(c["base"][1] - c["lump"][1] - 24451.07) < 0.005))
    checks.append(("EMI + 10 percent ends in 53 months, interest 58407.24, saving 8526.13",
                   c["higher"][0] == 53 and abs(c["higher"][1] - 58407.24) < 0.005
                   and abs(c["base"][1] - c["higher"][1] - 8526.13) < 0.005))
    bl = c["balances"][1]
    checks.append(("the balance curve drops by exactly the lump sum at month 12 (kink)",
                   abs((bl[11] * 1.01 - c["emi"]) - 50000.0 - bl[12]) < 1e-6))
    checks.append(("a lump sum larger than the balance just clears the loan",
                   L.simulate(10000.0, lambda m: 0.12, 500.0, 1e9, 3)[0] == 3))
    f = L.floating_case()
    checks.append(("floating rate: EMI 3226.72 at 10 percent, balance 69925.75 after 12 months",
                   abs(f["emi_old"] - 3226.72) < 0.005 and abs(f["balance_at_change"] - 69925.75) < 0.005))
    checks.append(("floating rate: recomputed EMI at 12 percent for 24 months is 3291.65",
                   abs(f["emi_new"] - 3291.65) < 0.005))
    checks.append(("floating rate: recomputing the EMI clears the loan exactly (balance 0) with interest 17720.18",
                   abs(f["final_balance"]) < 1e-6 and abs(f["recompute_interest"] - 17720.18) < 0.005))
    checks.append(("floating rate: keeping the old EMI takes 37 months with interest 17930.75",
                   f["keep_emi"][0] == 37 and abs(f["keep_emi"][1] - 17930.75) < 0.005))
    inst = L.flat_instalment(P, 0.08, 36)
    checks.append(("hand calculation: flat 8 percent on 100000 for 3 years has interest 24000 and instalment 3444.44",
                   abs(inst * 36 - P - 24000.0) < 1e-6 and abs(inst - 3444.44) < 0.005))
    checks.append(("reducing 8 percent has EMI 3133.64 and interest 12810.92, about half of the flat interest",
                   abs(L.emi(P, 0.08, 36) - 3133.64) < 0.005 and abs(36 * L.emi(P, 0.08, 36) - P - 12810.92) < 0.005))
    rb = L.true_annual_rate_bisect(P, inst, 36)
    rn = L.true_annual_rate_newton(P, inst, 36)
    checks.append(("worked example: the true rate of 'flat 8 percent' is 14.548 percent a year (bisection)",
                   abs(rb - 0.145481) < 1e-6))
    checks.append(("Newton's method finds the same root as bisection", abs(rb - rn) < 1e-9))
    checks.append(("the root really solves the equation: emi at the true rate = flat instalment",
                   abs(L.emi(P, rb, 36) - inst) < 1e-6))
    checks.append(("a flat 0 percent loan has true rate 0",
                   abs(L.true_annual_rate_bisect(P, L.flat_instalment(P, 0.0, 36), 36)) < 1e-5))
    e = L.emi(P, 0.12, 24)
    pv = L.present_value(e, 24, 0.06)
    checks.append(("present value of 24 EMIs of 4707.35 at 6 percent inflation is 106211.25, below the 112976.33 nominal sum",
                   abs(pv - 106211.25) < 0.01 and abs(24 * e - 112976.33) < 0.01))
    checks.append(("zero inflation: present value equals the plain sum",
                   abs(L.present_value(e, 24, 0.0) - 24 * e) < 1e-6))
    checks.append(("maximum loan with an EMI of 12000 (40 percent of 30000), 12 percent, 60 months is 539460.46",
                   abs(L.max_affordable_loan(30000.0, 0.4, 0.12, 60) - 539460.46) < 0.01
                   and abs(L.emi(539460.46, 0.12, 60) - 12000.0) < 0.01))
    checks.append(("failure case: paying 800 when the monthly interest is 1000 is negative amortisation",
                   L.is_negative_amortisation(100000.0, 0.12, 800.0) and not L.is_negative_amortisation(100000.0, 0.12, 1000.01)))
    n = L.simulate(100000.0, lambda m: 0.12, 800.0, max_months=60)
    checks.append(("failure case: after 60 months of paying 800 the balance has grown to 116333.93 and the loan never clears",
                   n[0] is None and abs(n[2][-1] - 116333.93) < 0.01))
    # mini-project: three made-up offers, 300000 over 60 months
    Pm, n = 300000.0, 60
    ex, ey, ez = L.emi(Pm, 0.105, n), L.emi(Pm, 0.095, n), L.flat_instalment(Pm, 0.06, n)
    cost = {"X": n * ex - Pm + 0.01 * Pm, "Y": n * ey - Pm + 0.03 * Pm, "Z": n * ez - Pm}
    checks.append(("mini-project: total cost X 89890.21, Y 87033.50, Z 90000.00, so Y is cheapest",
                   abs(cost["X"] - 89890.21) < 0.005 and abs(cost["Y"] - 87033.50) < 0.005
                   and abs(cost["Z"] - 90000.0) < 1e-6 and min(cost, key=cost.get) == "Y"))
    eff = {k: (1 + L.true_annual_rate_bisect(Pm * (1 - fee), ins, n) / 12) ** 12 - 1
           for k, ins, fee in (("X", ex, 0.01), ("Y", ey, 0.03), ("Z", ez, 0.0))}
    checks.append(("mini-project: effective annual rates X 11.50, Y 11.37, Z 11.40 percent (fee included)",
                   all(abs(eff[k] - v) < 5e-5 for k, v in (("X", 0.11502), ("Y", 0.11370), ("Z", 0.11404)))))
    sav = {}
    for k, ins, r in (("X", ex, 0.105), ("Y", ey, 0.095)):
        b = L.simulate(Pm, lambda m: r, ins)
        a = L.simulate(Pm, lambda m: r, ins, 50000.0, 12)
        sav[k] = (b[1] - a[1], a[0])
    checks.append(("mini-project: a 50000 lump sum after month 12 saves X 22604.66 and Y 20121.47, both ending in 49 months",
                   abs(sav["X"][0] - 22604.66) < 0.005 and abs(sav["Y"][0] - 20121.47) < 0.005
                   and sav["X"][1] == 49 and sav["Y"][1] == 49))
    checks.append(("mini-project: Z has the lowest headline rate (6 percent) yet the highest total cost",
                   max(cost, key=cost.get) == "Z"))
    checks.append(("roadmap baselines: constant 10 percent over 36 months costs 16161.87; a month-1 lump saves 32313.54",
                   abs(L.emi(100000.0, 0.10, 36) * 36 - 100000.0 - 16161.87) < 0.005
                   and abs(L.prepayment_case(lump_month=1)["base"][1] - L.prepayment_case(lump_month=1)["lump"][1] - 32313.54) < 0.005))
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
