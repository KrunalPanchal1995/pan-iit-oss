"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math
from fractions import Fraction

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    n = 1_000_000
    ref = L.exact_repeat_sum(0.1, n)
    run = L.naive_running(0.1, n)
    en = abs(run[-1] - ref)
    ek = abs(L.kahan_sum(np.full(n, 0.1)) - ref)
    ef = abs(math.fsum(np.full(n, 0.1)) - ref)
    checks.append(("exact reference for 1e6 copies of 0.1 is 1e5 (to 64-bit rounding)", ref == 100_000.0))
    checks.append(("naive sum of 0.1 one million times is off by more than 1e-8", en > 1e-8))
    checks.append(("naive error stays below the worst-case bound (n-1) u sum|x|", en <= L.naive_bound(n, 0.1 * n)))
    checks.append(("Kahan error is at least 1000 times smaller than naive", ek * 1000 <= en))
    checks.append(("math.fsum is exact here", ef == 0.0))
    checks.append(("edge: Kahan of an empty list is 0 and of [0.5] is 0.5", L.kahan_sum([]) == 0.0 and L.kahan_sum([0.5]) == 0.5))
    e = L.tick_error(23)
    checks.append(("hand calculation: chopping 0.1 at 23 places leaves error 0.1 * 2^-20 = 9.5367e-8 s",
                   Fraction(e).limit_denominator(10 ** 30) == Fraction(1, 10) * Fraction(1, 2 ** 20) or abs(e - 9.5367431640625e-8) < 1e-20))
    d = L.clock_drift(100, 23)
    checks.append(("worked example: after 100 hours the clock error is 0.343 s", abs(d - 0.3433) < 1e-3))
    checks.append(("worked example: at 1676 m/s the target moves about 575 m (more than half a kilometre)",
                   abs(L.scud_shift(d) - 575.4) < 1.0))
    checks.append(("clock drift is proportional to hours (edge: 0 h gives 0)", L.clock_drift(0) == 0.0 and abs(L.clock_drift(50) * 2 - d) < 1e-12))
    checks.append(("more binary places give a smaller drift: 28 places keep 100 h under 0.01 s",
                   L.clock_drift(100, 28) < 0.01 < L.clock_drift(100, 23)))
    checks.append(("worked example: 40000 wraps to -25536 in 16 bits", L.wrap_int16(40000) == -25536))
    checks.append(("edge: 32767 fits, 32768 wraps to -32768", L.wrap_int16(32767) == 32767 and L.wrap_int16(32768) == -32768))
    try:
        L.checked_int16(32768)
        raised = False
    except OverflowError:
        raised = True
    checks.append(("checked conversion raises on 32768 and accepts -32768", raised and L.checked_int16(-32768) == -32768))
    checks.append(("saturating conversion clamps to the 16-bit range", L.saturate_int16(1e9) == 32767 and L.saturate_int16(-1e9) == -32768))
    data = 1e9 + np.array([4.0, 7.0, 13.0, 16.0])
    checks.append(("mini-project: two-pass variance of 1e9 + [4, 7, 13, 16] is 22.5", abs(L.variance_two_pass(data) - 22.5) < 1e-9))
    checks.append(("mini-project: the naive variance is wrong by more than 100 (it is negative)", L.variance_naive(data) < 0))
    checks.append(("mini-project: naive norm of [3e200, 4e200] overflows, scaled norm is 5e200",
                   np.isinf(L.norm_naive([3e200, 4e200])) and abs(L.norm_scaled([3e200, 4e200]) / 5e200 - 1) < 1e-15))
    checks.append(("edge: scaled norm of zeros is 0", L.norm_scaled([0.0, 0.0]) == 0.0))
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
