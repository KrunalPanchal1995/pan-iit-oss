"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("machine epsilon equals 2^-52 (about 2.22e-16)", L.machine_epsilon() == 2.0 ** -52))
    s, e, f = L.decode(-6.5)
    checks.append(("worked example: -6.5 has sign 1, exponent field 1025, fraction 0.625 * 2^52",
                   (s, e, f) == (1, 1025, int(0.625 * 2 ** 52))))
    checks.append(("decoded fields rebuild the value of 0.1 exactly", L.encode_value(*L.decode(0.1)) == 0.1))
    checks.append(("hand calculation: 0.15625 = 1.25 * 2^-3 has fields (0, 1020, 2^50)", L.decode(0.15625) == (0, 1020, 2 ** 50)))
    checks.append(("1.0 has exponent field 1023 and fraction 0", L.decode(1.0) == (0, 1023, 0)))
    ex = float(L.small_root_exact(1e6, 1.0))
    checks.append(("worked example: small root of x^2 - 1e6 x + 1 is 1.000000000001e-6", abs(ex - 1.000000000001e-6) < 1e-18))
    en = L.rel_error(L.roots_naive(1e6, 1.0)[1], ex)
    es = L.rel_error(L.roots_stable(1e6, 1.0)[1], ex)
    checks.append(("worked example: textbook formula loses about 5 digits at b = 1e6 (error 1e-6 to 1e-5)", 1e-6 < en < 1e-5))
    checks.append(("stable formula is accurate to 1e-15 for b = 1e2 ... 1e8",
                   all(L.rel_error(L.roots_stable(b, 1.0)[1], float(L.small_root_exact(b, 1.0))) < 1e-15 for b in (1e2, 1e4, 1e6, 1e8))))
    checks.append(("hand calculation: at b = 1e8 the textbook small root is off by more than 10 percent",
                   L.rel_error(L.roots_naive(1e8, 1.0)[1], float(L.small_root_exact(1e8, 1.0))) > 0.1))
    checks.append(("both formulas agree on the large root", np.isclose(L.roots_naive(1e3, 1.0)[0], L.roots_stable(1e3, 1.0)[0], rtol=1e-15)))
    checks.append(("edge: 1 - cos(1e-8) is exactly 0 but 2 sin^2(t/2) is 5e-17",
                   L.one_minus_cos_naive(1e-8) == 0.0 and abs(L.one_minus_cos_stable(1e-8) - 5e-17) < 1e-20))
    checks.append(("1 - cos(0.5) is the same for both formulas to 1e-15",
                   abs(L.one_minus_cos_naive(0.5) - L.one_minus_cos_stable(0.5)) < 1e-15))
    big, tiny, sub = L.float_limits()
    checks.append(("limits: max about 1.8e308, smallest normal about 2.2e-308, smallest subnormal 5e-324",
                   1.79e308 < big < 1.80e308 and 2.2e-308 < tiny < 2.3e-308 and sub == 5e-324))
    checks.append(("edge: naive length of (3e200, 4e200) overflows, safe length is 5e200",
                   np.isinf(L.length_naive(3e200, 4e200)) and abs(L.length_safe(3e200, 4e200) / 5e200 - 1) < 1e-15))
    checks.append(("edge: safe length of (0, 0) is 0 and of (3, 4) is 5", L.length_safe(0.0, 0.0) == 0.0 and abs(L.length_safe(3.0, 4.0) - 5.0) < 1e-15))
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
