"""Checkpoint for Session 1. Prints PASS or FAIL."""


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: simple interest on 10000 at 10 percent for 3 years gives 13000",
                   abs(L.simple_amount(10000, 0.10, 3) - 13000) < 1e-9))
    checks.append(("worked example: compound interest gives 13310, which is 310 more",
                   abs(L.compound_amount(10000, 0.10, 3) - 13310) < 1e-6
                   and abs(L.compound_amount(10000, 0.10, 3) - L.simple_amount(10000, 0.10, 3) - 310) < 1e-6))
    checks.append(("hand calculation: 10000 * 1.1 * 1.1 * 1.1 = 13310",
                   abs(10000 * 1.1 * 1.1 * 1.1 - L.compound_amount(10000, 0.10, 3)) < 1e-6))
    checks.append(("zero years or zero rate: nothing is added",
                   L.simple_amount(500, 0.1, 0) == 500 and L.compound_amount(500, 0.0, 7) == 500))
    checks.append(("in year 1 both methods agree (both 11000)",
                   abs(L.simple_amount(10000, 0.10, 1) - L.compound_amount(10000, 0.10, 1)) < 1e-9))
    checks.append(("after 20 years compound 67275 versus simple 30000",
                   round(L.compound_amount(10000, 0.10, 20)) == 67275 and round(L.simple_amount(10000, 0.10, 20)) == 30000))
    checks.append(("doubling time at 10 percent: simple 10 years, compound 7.27 years",
                   abs(L.doubling_time_simple(0.10) - 10.0) < 1e-9 and abs(L.doubling_time_compound(0.10) - 7.2725) < 1e-3))
    checks.append(("compound never falls below simple for t >= 1",
                   all(L.compound_amount(1000, 0.07, t) >= L.simple_amount(1000, 0.07, t) for t in range(1, 40))))
    checks.append(("exercise numbers: 5000 at 8 percent for 2 years is 5800 simple and 5832 compound",
                   abs(L.simple_amount(5000, 0.08, 2) - 5800) < 1e-9 and abs(L.compound_amount(5000, 0.08, 2) - 5832) < 1e-6))
    checks.append(("design numbers: 10000 for 5 years is 16000 at 12 percent simple and 16105.10 at 10 percent compound",
                   abs(L.simple_amount(10000, 0.12, 5) - 16000) < 1e-9 and abs(L.compound_amount(10000, 0.10, 5) - 16105.10) < 1e-6))
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
