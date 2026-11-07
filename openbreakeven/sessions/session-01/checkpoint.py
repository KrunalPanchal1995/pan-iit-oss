"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("before any cup is sold the cost is the fixed $60", abs(float(L.total_cost(0)) - 60.0) < 1e-9))
    q = L.break_even_cups()
    checks.append(("worked example: break-even is 60 / (2.00 - 0.50) = 40 cups", abs(q - 40.0) < 1e-9))
    checks.append(("worked example: at 40 cups income = cost = $80",
                   abs(float(L.income(40)) - 80.0) < 1e-9 and abs(float(L.total_cost(40)) - 80.0) < 1e-9))
    checks.append(("counting cups one by one also gives 40", L.first_profitable_cup() == 40))
    checks.append(("39 cups: still $1.50 short", abs(float(L.profit(39)) + 1.5) < 1e-9))
    checks.append(("41 cups: $1.50 ahead", abs(float(L.profit(41)) - 1.5) < 1e-9))
    checks.append(("25 cups: income $50, cost $72.50, loss $22.50",
                   abs(float(L.income(25)) - 50.0) < 1e-9 and abs(float(L.total_cost(25)) - 72.5) < 1e-9
                   and abs(float(L.profit(25)) + 22.5) < 1e-9))
    checks.append(("each extra cup adds $1.50 to the profit", abs(float(L.profit(11) - L.profit(10)) - 1.5) < 1e-9))
    checks.append(("hand calculation F=45, price 1.50, cup cost 0.60 gives 50 cups",
                   abs(L.break_even_cups(45.0, 1.5, 0.6) - 50.0) < 1e-9
                   and abs(float(L.income(50, 1.5)) - 75.0) < 1e-9))
    checks.append(("price $2.50 moves break-even to 30 cups", abs(L.break_even_cups(price=2.5) - 30.0) < 1e-9))
    checks.append(("fixed cost $45 at price $2.00 also gives 30 cups", abs(L.break_even_cups(fixed=45.0) - 30.0) < 1e-9))
    checks.append(("price $1.00 needs 120 cups", abs(L.break_even_cups(price=1.0) - 120.0) < 1e-9))
    checks.append(("limit: price equal to the cup cost has no break-even", L.break_even_cups(price=0.5) is None))
    checks.append(("limit: price below the cup cost has no break-even", L.break_even_cups(price=0.3) is None
                   and L.first_profitable_cup(price=0.3) is None))
    checks.append(("limit: no fixed cost means break-even at 0 cups", L.break_even_cups(fixed=0.0) == 0.0))
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
